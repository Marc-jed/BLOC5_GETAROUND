---
title: Fastapi Get
emoji: 🏢
colorFrom: yellow
colorTo: green
sdk: docker
pinned: false
license: apache-2.0
---

🚗 Getaround Car Rental - API de Prédiction

Cette API permet de prédire le prix journalier de location d’un véhicule sur Getaround, en fonction de ses caractéristiques techniques (marque, type de carburant, puissance moteur, etc.).

Elle est basée sur un modèle XGBoost optimisé et hébergée sur Hugging Face Spaces avec FastAPI.

⚡ Endpoints disponibles
🔹 POST /predict

Prédit le prix de location journalier.

Méthode : POST

curl -X POST "https://gdleds-api-gat.hf.space/predict" \
-H "Content-Type: application/json" \
-d '{
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
}'


Sortie (JSON) :

{
  "predicted_price_per_day":124.9
}

🔹 GET /docs

Accès à la documentation interactive (Swagger UI).
👉 Exemple : https://gdleds-api-get.hf.space/docs

🛠️ Stack technique

Python 3.10

FastAPI + Uvicorn

XGBoost

scikit-learn

Hugging Face Spaces

Stockage du modèle sur S3 (Amazon)

🚀 Exemple avec curl
curl -X POST "https://ton-espace.hf.space/predict" \
-H "Content-Type: application/json" \
-d '{"input": [[100000, 120, "diesel", "black", "estate", 1, 1, 0, 0, 1, 0, 1]]}'

📦 Déploiement local (optionnel)

Pour tester localement :

uvicorn app:app --reload --host 0.0.0.0 --port 8000


Puis tester avec :
👉 http://127.0.0.1:8000/docs


Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
