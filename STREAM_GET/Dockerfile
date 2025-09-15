FROM python:3.13.5-slim

# Définir le dossier de travail
WORKDIR /app

# Installer dépendances système utiles
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et code
COPY requirements.txt ./
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port Streamlit
EXPOSE 8501

# Vérification de santé
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Lancer Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
