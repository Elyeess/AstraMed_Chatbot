# Utiliser une image Python officielle légère
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Variables d'environnement pour éviter les buffers et optimiser l'exécution
ENV PYTHONUNBUFFERED=1
ENV PORT=8501

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copier le reste des fichiers de l'application
COPY . /app

# Exposer le port utilisé par Streamlit
EXPOSE 8501

# Commande pour lancer Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
