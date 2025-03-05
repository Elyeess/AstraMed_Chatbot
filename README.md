# 🏥 AstraMed - Chatbot d'Assistance Médicale avec RAG & Cloud AI 🚀
<img width="595" alt="image" src="https://github.com/user-attachments/assets/0140af8a-fe64-4095-baee-1fd673c5c79d" />
<img width="941" alt="image" src="https://github.com/user-attachments/assets/3643713c-cb1f-4fa7-9823-7e64bc63002b" />

AstraMed est un chatbot intelligent basé sur l'intelligence artificielle, conçu pour fournir des réponses fiables aux questions médicales des utilisateurs. Il intègre un système avancé de Retrieval-Augmented Generation (RAG) combinant LangChain, Vertex AI, PostgreSQL Vector, et Google Cloud Storage, garantissant ainsi des réponses pertinentes et basées sur des sources vérifiées.

## ✨ Fonctionnalités Clés

- 🔍 **Recherche Sémantique Avancée** : Utilisation de vecteurs pour rechercher les questions médicales les plus pertinentes.
- 📚 **Base de Connaissances Structurée** : Intégration avec PostgreSQL + pgvector pour stocker les embeddings et les métadonnées.
- 🤖 **Génération Augmentée par Récupération (RAG)** : Amélioration de la qualité des réponses en combinant recherche et IA.
- ⚡ **FastAPI & Streamlit** : API REST performante et interface utilisateur interactive.
- 🌍 **Support Multilingue** : Capacité de traduction en Français, Anglais et Arabe.
- 🏆 **Affichage des Sources & Scores de Confiance** : Transparence des références utilisées.
- 🛡 **Respect des Normes de Confidentialité** : Aucune donnée utilisateur n'est stockée de manière permanente.

## 🔗 Architecture

Les composants sont interconnectés de la manière suivante :

1. **Cloud Storage** fournit les données à **PostgreSQL**.
2. **FastAPI** interagit avec **LangChain** et **PostgreSQL**.
3. **Vertex AI** assure les fonctionnalités d'intelligence artificielle.
4. **Streamlit** offre une interface utilisateur reliée à **FastAPI**.

## 📁 Structure du Projet

```
AstraMed_chatbot/
│── downloaded_files/
│   └── medquadd.csv  # Données d'entraînement
├── api.py                 # Backend FastAPI
├── app.py                 # Interface utilisateur Streamlit
├── config.py              # Configuration des variables cloud
├── ingest.py              # Chargement et indexation des données
├── retrieve.py            # Récupération des documents pertinents
├── eval.py                # Évaluation du chatbot
├── utils_eval.py          # Fonctions d'évaluation
├── requirements.txt       # Liste des dépendances Python
├── Dockerfile             # Dockerfile pour Streamlit
├── Dockerfile_api         # Dockerfile pour FastAPI
├── .env                   # Variables d'environnement (non versionnées)
```

## 🔧 Installation & Configuration

### Prérequis

- Python 3.11+
- Docker (optionnel pour le déploiement)
- Accès à Google Cloud Storage & Cloud SQL

### Installation

Clonez le repository Git et installez les dépendances :

```bash
# Cloner le repository
git clone https://github.com/<votre-repo>/AstraMed_chatbot.git
cd AstraMed_chatbot

# Créer un environnement virtuel
conda create --name (env_name) python=3.10
conda activate (env_name)

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration des Variables d'Environnement

Créez un fichier `.env` à la racine du projet et ajoutez les informations suivantes :

```ini
DB_PASSWORD=<votre_password>
API_KEY=<votre_api_key>
PROJECT_ID=<votre_project_id>
INSTANCE=<nom_instance>
REGION=<votre_region>
DATABASE=<nom_database>
DB_USER=<utilisateur>
TABLE_NAME=<nom_table>
```

## 🛠️ Utilisation

### Lancer l'API avec FastAPI

```bash
uvicorn api:app --host 0.0.0.0 --port 8181
```

L'API sera accessible sur [http://127.0.0.1:8181](http://127.0.0.1:8181)

### Lancer l'interface utilisateur Streamlit

```bash
streamlit run app.py
```

L'interface utilisateur sera disponible sur [http://localhost:8501](http://localhost:8501)

## 🛢️ Déploiement avec Docker

### Déploiement de l'API

```bash
docker build -t astramed-api -f Dockerfile_api .
docker run -p 8181:8181 astramed-api
```

### Déploiement de l'interface utilisateur

```bash
docker build -t astramed-ui -f Dockerfile .
docker run -p 8501:8080 astramed-ui
```

## 📖 Bonnes Pratiques de Code

AstraMed respecte les conventions de code avec **Flake8** et **PyLint**. Pour analyser votre code :

```bash
flake8 --max-line-length=120
pylint --disable=C,R,W *.py
```

Pour autoformater le code avec **Autopep8** :

```bash
autopep8 --in-place --aggressive --aggressive *.py
```

## 🌟 Fonctionnalités Principales

- 🔍 **Recherche de documents médicaux** : Basée sur la similarité vectorielle.
- 👨‍🎓 **Génération de réponses** : LangChain RAG + Vertex AI.
- 🌍 **Traduction automatique** : FR, EN, AR.
- 📱 **Interface utilisateur moderne** : Streamlit.
- 🔢 **Évaluation des performances** : Métriques de similarité et pertinence.

## 💪 Contributeurs

Ce projet a été développé par **Donia Tekaya & Mohamed Elyes Maalel**.

