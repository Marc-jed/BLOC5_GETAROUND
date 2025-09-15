
# 🚗 Getaround – Industrialisation & Déploiement d’un modèle Machine Learning

## 📌 Contexte du projet
Getaround est une plateforme de location de voitures entre particuliers, souvent appelée le "Airbnb des voitures".  
Un problème récurrent est celui des **retards lors de la restitution des véhicules** :  
- Le prochain utilisateur peut devoir attendre,  
- Ou pire, annuler sa réservation,  
➡️ générant insatisfaction client et pertes de revenus.

L’objectif de ce projet est double :
1. **Analyser les retards** et leur impact sur les revenus.  
2. **Construire et déployer un modèle de Machine Learning** capable d’optimiser la tarification et d’aider à la décision produit.

---

## 🎯 Objectifs
- Étudier la fréquence et l’impact des retards.  
- Déterminer un **délai minimum optimal** entre deux locations.  
- Construire un **modèle de pricing prédictif** basé sur XGBoost.  
- Déployer une **API** permettant de consommer le modèle en production.  
- Créer un **dashboard Streamlit** interactif pour l’équipe produit.  

---

## 📊 Analyse exploratoire (EDA)
L’EDA a permis de mettre en évidence :
- Les retards concernent une minorité de locations mais génèrent une perte financière non négligeable.  
- L’impact dépend fortement du **type de contrat** (mobile, Connect, papier).  
- Certains seuils de délai réduisent fortement les frictions tout en maintenant les revenus.  

**Graphiques exploratoires réalisés** :
- Histogramme des retards,  
- Courbe des revenus impactés selon différents seuils,  
- Analyse comparative par type de contrat.  

---

## 🤖 Modélisation Machine Learning
- **Algorithme choisi** : `XGBoost Regressor`  
- **Pipeline** : Prétraitement des données (numériques & catégorielles) → entraînement → validation.  
- **Évaluation** : RMSE & R².  
- **Résultat** : le modèle identifie les variables les plus influentes pour le pricing.    

---

## ⚙️ API – FastAPI
Une API a été développée pour rendre le modèle accessible en production.  

### 📍 Endpoint disponible
- `POST /predict` : permet d’envoyer des données d’entrée et de recevoir une prédiction de prix.

\ https://gdleds-api-get.hf.space/docs#/default/predict_predict_post

---

## 📊 Dashboard – Streamlit

Un tableau de bord a été développé pour l’équipe produit :

* Explorer la distribution des retards,
* Simuler différents **seuils de délai minimum** et observer l’impact sur les revenus,
* Visualiser les métriques clés pour la prise de décision.

👉 https://huggingface.co/spaces/gdleds/stream_get

---

## 🛠️ Technologies utilisées

* Python (Pandas, Scikit-learn, XGBoost, Plotly)
* FastAPI
* Streamlit
* Docker
* MLflow (versioning des modèles)
* AWS S3 (stockage)

---

## 🚀 Perspectives

* Améliorer le modèle de pricing avec plus de variables (saisonnalité, météo, concurrence).
* Monitorer l’API en production et gérer la scalabilité (Kubernetes, load balancing).
* Intégrer le dashboard avec l’API pour un produit complet.

---

## 👤 Auteur

Projet réalisé dans le cadre du **Bootcamp Fullstack Data Science – Jedha**.

```


