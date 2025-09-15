import mlflow
import pandas as pd
import os
import subprocess
import numpy as np
from dotenv import load_dotenv
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from xgboost import XGBRegressor
import boto3
import joblib
import io

load_dotenv(dotenv_path='.secrets')

mlflow.set_tracking_uri(os.getenv('BACKEND_STORE_URI'))
os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
os.environ['MLFLOW_DEFAULT_ARTIFACT_ROOT'] = os.getenv('MLFLOW_DEFAULT_ARTIFACT_ROOT')
os.environ['S3_BUCKET'] = os.getenv('S3_BUCKET')

# Log configurations au démarrage
print("=== Configuration MLflow ===")
print(f"Tracking URI: {mlflow.get_tracking_uri()}")
print(f"Artifact Store: {os.getenv('MLFLOW_DEFAULT_ARTIFACT_ROOT')}")
print(f"AWS Access: {'Configuré' if os.getenv('AWS_ACCESS_KEY_ID') else 'Manquant'}")

s3 = boto3.client('s3')
try:
   response = s3.list_objects_v2(Bucket=os.getenv('S3_BUCKET'))
   print("S3 contents:", response.get('Contents', []))
except Exception as e:
   print("S3 error:", e)

df = pd.read_csv('/mnt/c/Users/m_bar/dsfs_ft/GETAROUND/pricing_clean.csv')
feature_list = df.drop('rental_price_per_day', axis=1)
target = df['rental_price_per_day']
X = feature_list
Y = target
X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size=0.2, random_state=42)

numeric_features = ['mileage', 'engine_power']
categorical_features = ['model_key','fuel', 'paint_color', 'car_type', 'private_parking_available', 'has_gps', 'has_air_conditioning','automatic_car','has_getaround_connect','has_speed_regulator','winter_tires']

numeric_transformer = Pipeline(steps=[('scaler', StandardScaler())])
categorical_transformer = Pipeline(steps=[('encoder', OneHotEncoder(drop='if_binary', handle_unknown='ignore'))])

preprocessor = ColumnTransformer(transformers =[
    ('num', numeric_transformer, numeric_features),
    ('cat', categorical_transformer, categorical_features)
])

def train_evaluate_model_with_mlflow(model, X_train, X_test, Y_train, Y_test, model_name):
   print(f"\n=== Démarrage entraînement {model_name} ===")
   print(f"Tracking URI: {mlflow.get_tracking_uri()}")
   print(f"Registry URI: {mlflow.get_registry_uri()}")
   
   mlflow.set_experiment("price_prediction")
   print(f"Experiment: price_prediction")
   s3 = boto3.client('s3')

   with mlflow.start_run() as run:
       print(f"Run ID: {run.info.run_id}")
       
       print("Entraînement du modèle...")
       model.fit(X_train, Y_train)
       
       #save model to S3
       print("Enregistrement du modèle sur S3...")
       model_path = f"mlflow/models/{model_name}_{run.info.run_id}.joblib"
       buffer = io.BytesIO()
       joblib.dump(model, buffer)
       s3.put_object(
           Bucket=os.getenv('S3_BUCKET'),
           Key=model_path,
           Body=buffer.getvalue()
       )
       print("Modèle enregistré")
       
       y_pred = model.predict(X_test)
       metrics = {
           "RMSE": np.sqrt(mean_squared_error(Y_test, y_pred)),
           "MAE": mean_absolute_error(Y_test, y_pred),
           "R2": r2_score(Y_test, y_pred)
       }
       
       print("\nEnregistrement des métriques...")
       for name, value in metrics.items():
           mlflow.log_metric(name, value)
           print(f"{name}: {value:.2f}")
       
       return model, run.info.run_id

if __name__ == "__main__":
    xgb_best_param = XGBRegressor(learning_rate = 0.1, max_depth = 5, n_estimators =200, n_jobs = 1)
    xgb_final = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('xgboost_best', xgb_best_param)
    ])
    _, run_id = train_evaluate_model_with_mlflow(
        xgb_final, X_train, X_test, Y_train, Y_test, "xgboost_model"
    )
    print(f"Run ID: {run_id}")