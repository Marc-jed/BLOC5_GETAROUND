from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
import pandas as pd
import boto3
import joblib
import os
import io

# === Initialisation FastAPI ===
app = FastAPI(
    title="🚗 Getaround Price Prediction API",
    description="""
### 🎯 Description  
Cette API prédit le **prix de location journalier** d’un véhicule.

👉 Pour certaines colonnes (`model_key`, `fuel`, `car_type`, `paint_color`), **choisir une valeur parmi les critères listés**.  
ModelKey =
    "Citroën", "Peugeot", "PGO", "Renault", "Audi", "BMW", "Ford", "Mercedes","Opel", "Porsche", "Volkswagen", "KIA Motors", "Alfa Romeo", "Ferrari", "Fiat",
    "Lamborghini", "Maserati", "Lexus", "Honda", "Mazda", "Mini", "Mitsubishi","Nissan", "SEAT", "Subaru", "Suzuki", "Toyota", "Yamaha"

Mileage = Renseigner des valeurs entre 0 et 400000

EnginePower = Renseigner des valeurs entre 10 et 300

Fuel = "diesel", "petrol", "hybrid_petrol", "electro"

PaintColor = "black", "grey", "white", "red", "silver", "blue", "orange","beige", "brown", "green"

CarType = "convertible", "coupe", "estate", "hatchback", "sedan", "subcompact", "suv", "van"

👉 Pour les autres options (`private_parking_available`, `has_gps`, etc.), utiliser **true pour Oui** et **false pour Non**.

Exemple :  
```json
{
  "model_key": "Audi",
  "mileage": 100000,
  "engine_power": 120,
  "fuel": "diesel",
  "paint_color": "black",
  "car_type": "estate",
  "private_parking_available": true,
  "has_gps": true,
  "has_air_conditioning": false,
  "automatic_car": false,
  "has_getaround_connect": true,
  "has_speed_regulator": false,
  "winter_tires": true
}
""",
version="1.0"
)

# === Schéma attendu pour l'entrée ===
class InputData(BaseModel):
    model_key: str
    mileage: int
    engine_power: int
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

# === Configuration S3 ===
S3_BUCKET = os.getenv("S3_BUCKET")
MODEL_KEY = os.getenv("MODEL_KEY", "mlflow/models/xgboost_model.joblib")
s3 = boto3.client("s3")

# === Chargement du modèle depuis S3 au démarrage ===
model = None

@app.on_event("startup")
def load_model():
    global model
    try:
        print(f"Téléchargement du modèle depuis s3://{S3_BUCKET}/{MODEL_KEY}")
        response = s3.get_object(Bucket=S3_BUCKET, Key=MODEL_KEY)
        model_bytes = io.BytesIO(response["Body"].read())
        model = joblib.load(model_bytes)
        print("✅ Modèle chargé avec succès")
    except Exception as e:
        print(f"❌ Erreur chargement modèle : {e}")
        raise RuntimeError(f"Impossible de charger le modèle : {e}")

# === Routes ===
@app.get("/")
def home():
    return {"message": "Bienvenue sur l'API Getaround 🚗 - Utilisez /predict pour faire une prédiction"}

@app.post("/predict")
def predict(data: InputData):
    try:
        # Convertir les données en DataFrame avec colonnes correctes
        df = pd.DataFrame([data.dict()])
        print("📥 Données reçues :", df.to_dict())

        # Faire la prédiction
        prediction = model.predict(df)
        price = float(prediction[0])

        return {"predicted_price_per_day": [round(float(prediction), 2)]}

    except Exception as e:
        print(f"❌ Erreur prédiction : {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
