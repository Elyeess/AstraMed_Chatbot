# AstraMed Chatbot
<img width="959" alt="image" src="https://github.com/user-attachments/assets/a01d5d8b-08db-4870-b17b-808f86ada86a" />


AstraMed est un chatbot d'assistance médicale basé sur l'intelligence artificielle, conçu pour fournir des réponses fiables aux questions médicales des utilisateurs. Il utilise un système de recherche avancé combinant Google Cloud Storage, PostgreSQL Vector, LangChain RAG, et Vertex AI pour générer des réponses pertinentes.

---

## 🎨 Aperçu du projet



Le projet est structuré autour des composants suivants :

- **Google Cloud Storage** : Stockage des données médicales sous forme de fichiers CSV.
- **PostgreSQL + Vector** : Base de données vectorielle pour la recherche de similarité.
- **LangChain RAG** : Génération augmentée par récupération (RAG) pour améliorer les réponses du chatbot.
- **Vertex AI** : Utilisation de modèles avancés pour l'analyse et la reformulation des réponses.
- **FastAPI** : API backend pour servir les réponses du chatbot.
- **Streamlit** : Interface utilisateur intuitive pour interagir avec le chatbot.

---

## 🔧 Installation et Configuration

### Prérequis

1. **Python 3.11+**
2. **Docker (optionnel pour le déploiement)**
3. **Accès à Google Cloud Storage & Cloud SQL**

### Installation

Clonez le repository Git et installez les dépendances :

```bash
# Cloner le repository
git clone[ https://github.com/<votre-repo>/AstraMed_chatbot.git](https://github.com/doniatekaya/AstraMed_Chatbot/tree/main)
cd AstraMed_chatbot

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sous Windows: venv\Scripts\activate

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

---

## 🛠️ Utilisation

### Lancer l'API avec FastAPI

```bash
uvicorn api:app --host 0.0.0.0 --port 8181
```

L'API sera accessible sur `http://127.0.0.1:8181`

### Lancer l'interface utilisateur Streamlit

```bash
streamlit run app.py
```

L'interface utilisateur sera disponible sur `http://localhost:8501`

---

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

---

## 🔬 Structure du Repository

```plaintext
AstraMed_chatbot/
│── downloaded_files/
│   └── medquadd.csv  # Données d'entraînement
│── __pycache__/       # Cache Python
│── api.py             # Backend FastAPI
│── app.py             # Interface Streamlit
│── config.py          # Variables de configuration
│── ingest.py          # Connexion Cloud SQL et stockage vectoriel
│── retrieve.py        # Récupération des documents pertinents
│── eval.py            # Évaluation du chatbot
│── utils_eval.py      # Fonctions d'évaluation
│── requirements.txt   # Dépendances Python
│── Dockerfile         # Fichier Docker pour Streamlit
│── Dockerfile_api     # Fichier Docker pour l'API
│── .env               # Variables d'environnement
```

---

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

---

## 🌟 Fonctionnalités Principales

- 🔍 **Recherche de documents médicaux** : Basée sur la similarité vectorielle.
- 👨‍🎓 **Génération de réponses** : LangChain RAG + Vertex AI.
- 🌍 **Traduction automatique** : FR, EN, AR.
- 📱 **Interface utilisateur moderne** : Streamlit.
- 🔢 **Évaluation des performances** : Métriques de similarité et pertinence.

---

## 💪 Contributeurs

Ce projet a été développé par **Donia Tekaya & Mohamed Elyes Maalel**.

Pour toute contribution, ouvrez une PR ou contactez-nous ! 🚀

