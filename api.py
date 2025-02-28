from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from ingest import create_cloud_sql_database_connection, get_embeddings, get_vector_store
from retrieve import get_relevant_documents
from config import TABLE_NAME
from uuid import uuid4

# Charger les variables d'environnement
load_dotenv()
API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise ValueError("API_KEY is missing. Please set it in the environment variables.")

# Initialisation de l'API
app = FastAPI(
    title="AstraMed API",
    description="API pour AstraMed",
    version="1.0.0"
)

# Initialisation des connexions aux services
engine = create_cloud_sql_database_connection()
embedding = get_embeddings()
vector_store = get_vector_store(engine, TABLE_NAME, embedding)

class UserInput(BaseModel):
    question: str
    temperature: float
    language: str
    similarity_threshold: float
    session_id: str = ""

def get_llm(temperature: float = 0.3):
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=API_KEY,
        temperature=temperature,
        verbose=True
    )
class FeedbackInput(BaseModel):
    session_id: str
    question: str
    rating: int  # 1 pour 👍, 0 pour 👎
    comments: str = ""
@app.post("/feedback")
async def feedback(feedback: FeedbackInput):
    try:
        # 📌 Stockage du feedback (Exemple : print, mais peut être stocké en base)
        print(f"📊 Feedback reçu : {feedback.dict()}")
        
        return {"message": "Feedback enregistré avec succès."}
    except Exception as e:
        print(f"❌ Erreur de feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'enregistrement du feedback")

@app.get("/")
async def root():
    return {"status": "AstraMed API is running"}

@app.post("/answer")
async def answer(user_input: UserInput):
    try:
        print(f"🔍 Recherche des documents pour la question : {user_input.question}")
        documents = get_relevant_documents(user_input.question, vector_store, user_input.similarity_threshold)

        if not documents:
            return {"message": "Aucune source pertinente trouvée.", "answers": []}

        # Extraire les 3 meilleures réponses
        top_3_responses = [
            {
                "message": doc.metadata.get("answer", "Réponse non disponible."),
                "metadata": {
                    "source": doc.metadata.get("source", "Inconnue"),
                    "focus_area": doc.metadata.get("focus_area", "Non spécifié"),
                    "similarity_score": f"{doc.metadata.get('score', 'N/A'):.4f}"
                }
            } for doc in documents[:3]
        ]

        # Générer une réponse reformulée à partir des 3 meilleures réponses
        concatenated_answers = "\n".join([resp["message"] for resp in top_3_responses if resp["message"] != "Réponse non disponible."])

        if not concatenated_answers.strip():
            return {
                "answers": top_3_responses,
                "generated_response": "Impossible de générer une réponse reformulée à partir des sources disponibles."
            }

        llm = get_llm(user_input.temperature)

        prompt = f"""
        Voici trois réponses médicales pertinentes :
        {concatenated_answers}

        Reformule une réponse unique et cohérente en {user_input.language}, en synthétisant ces informations.
        """

        print(f"📢 Envoi au LLM pour reformulation...")
        generated_response = llm.invoke(prompt).content
        print(f"✅ Réponse générée : {generated_response}")

        return {
            "answers": top_3_responses,
            "generated_response": generated_response
        }

    except Exception as e:
        print(f"❌ Erreur détaillée: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement : {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8181)

