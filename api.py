from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import uvicorn
from langchain.agents import Tool, ZeroShotAgent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from ingest import create_cloud_sql_database_connection, get_embeddings, get_vector_store
from retrieve import get_relevant_documents
from config import TABLE_NAME
import re

# Load environment variables
load_dotenv()
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY is missing. Please set it in the environment variables.")

SYSTEM_PROMPT = """
Tu es AstraMed, un assistant virtuel spécialisé dans l'information médicale. Voici tes objectifs et tes règles :
1. Tu n'es pas un médecin et tu ne peux pas remplacer un avis médical professionnel.
2. Tes réponses doivent rester professionnelles, claires et factuelles.
3. Si tu ne connais pas la réponse ou si l'information est incertaine, indique-le de manière transparente.
4. Utilise un ton poli et empathique.
5. Invite toujours l'utilisateur à consulter un professionnel de santé pour un diagnostic ou un traitement précis.
6. Tes réponses peuvent contenir des explications médicales simplifiées, mais veille à ne pas fournir de diagnostic formel.
"""

app = FastAPI(
    title="AstraMed API",
    description="API pour AstraMed via Agent LangChain",
    version="1.0.0"
)

engine = create_cloud_sql_database_connection()
embedding = get_embeddings()
vector_store = get_vector_store(engine, TABLE_NAME, embedding)

class UserInput(BaseModel):
    question: str
    temperature: float
    language: str
    similarity_threshold: float
    session_id: str = ""

class FeedbackInput(BaseModel):
    session_id: str
    question: str
    rating: int  # 1 pour 👍, 0 pour 👎
    comments: str = ""

# Function to parse agent output more robustly
def parse_agent_output(agent_output: str) -> dict:
    # Find all observations
    observations = re.findall(r"Observation:\s*(.+?)(?=\n\w+:|$)", agent_output, re.DOTALL)
    
    # Determine response type
    is_general_response = "general_response" in agent_output
    is_medical_response = "search_medical_docs" in agent_output
    
    # If observations exist, use the last one
    if observations:
        generated_response = observations[-1].strip()
        
        # Determine response type
        if is_general_response:
            response_type = "general"
        elif is_medical_response:
            response_type = "medical"
            # Append standard medical advice
            generated_response += " Consultez un professionnel de santé."
        else:
            response_type = "general"
        
        return {
            "type": response_type,
            "generated_response": generated_response
        }
    
    # Fallback parsing for Final Answer format
    match = re.search(r"Final Answer:\s*\[TYPE:\s*(general|medical)\]\s*(.+)", agent_output, re.DOTALL)
    if match:
        response_type = match.group(1)
        generated_response = match.group(2).strip()
        
        # Append medical advice for medical responses
        if response_type == "medical":
            generated_response += " Consultez un professionnel de santé."
        
        return {
            "type": response_type,
            "generated_response": generated_response
        }
    
    # Alternative observation parsing
    observation_match = re.search(r"Observation:\s*(.+?)(?:\nThought:|$)", agent_output, re.DOTALL)
    if observation_match:
        generated_response = observation_match.group(1).strip()
        response_type = "general" if is_general_response else "medical"
        
        # Append medical advice for medical responses
        if response_type == "medical":
            generated_response += " Consultez un professionnel de santé."
        
        return {
            "type": response_type,
            "generated_response": generated_response
        }
    
    # Fallback parsing for lines
    lines = [line.strip() for line in agent_output.splitlines() if line.strip()]
    if lines:
        # Take the last meaningful line
        generated_response = lines[-1]
        response_type = "general" if is_general_response else "medical"
        
        # Append medical advice for medical responses
        if response_type == "medical":
            generated_response += " Consultez un professionnel de santé."
        
        return {
            "type": response_type,
            "generated_response": generated_response
        }
    
    # Complete fallback
    return {
        "type": "unknown",
        "generated_response": "Erreur lors de la génération de la réponse."
    }

# Bonus function to extract sources for medical responses
def extract_medical_sources(agent_output: str) -> List[dict]:
    # Regex to extract sources with their details
    source_pattern = r"🏥 *Source \d+:\s*(\w+)\s*\(Similarité:\s*([\d.]+)\)\n🔹 *Réponse \d+ *:*\s*(.+?)(?=\n🏥 *Source|\n\n|$)"
    
    sources = []
    for match in re.finditer(source_pattern, agent_output, re.DOTALL | re.IGNORECASE):
        sources.append({
            "source": match.group(1),
            "similarity": float(match.group(2)),
            "content": match.group(3).strip()
        })
    
    return sources

# Function to search medical documents
def search_medical_docs(query: str, similarity_threshold: float) -> tuple[str, List[dict]]:
    docs = get_relevant_documents(query, vector_store, similarity_threshold)
    print(f"[DEBUG] Documents trouvés dansGAR vector_store : {len(docs)}")
    if not docs:
        return "Aucune source pertinente trouvée.", []
    
    top_docs = []
    for doc in docs[:3]:
        ans = doc.metadata.get("answer", "Réponse non disponible.")
        src = doc.metadata.get("source", "Inconnue")
        scr = doc.metadata.get("score", 0.0)
        top_docs.append({
            "message": ans,
            "metadata": {
                "source": src,
                "similarity_score": scr
            }
        })
    print(f"[DEBUG] Top 3 documents : {top_docs}")
    top_docs_str = "\n".join([f"{doc['message']}" for doc in top_docs if doc["message"] != "Réponse non disponible."])
    return top_docs_str, top_docs

# Function for general responses
def general_response(query: str) -> str:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=API_KEY,
        temperature=0.3,
        verbose=True
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]
    response = llm.invoke(messages)
    return response.content

# Initialize the language model
def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=API_KEY,
        temperature=temperature,
        verbose=True
    )

@app.post("/feedback")
async def feedback(feedback: FeedbackInput):
    try:
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
        # Define tools
        tool_search = Tool(
            name="search_medical_docs",
            func=lambda q: search_medical_docs(q, user_input.similarity_threshold)[0],
            description="Recherche dans la base de documents médicaux. À utiliser uniquement pour les questions médicales spécifiques (symptômes, diagnostics, traitements)."
        )
        tool_general = Tool(
            name="general_response",
            func=general_response,
            description="Répond aux questions générales ou salutations en utilisant le prompt système."
        )

        # Language model with adjustable temperature
        llm = get_llm(temperature=user_input.temperature)

        # Updated agent prompt with clear format and examples
        agent_prompt = """
Tu es AstraMed, un assistant médical spécialisé. L'entrée fournie est de la forme :
[question]
Langue de réponse : [language]

Suis ces étapes strictement :
1. Analyse uniquement la partie [question] pour déterminer si elle est :
   - Médicale : Symptômes, maladies, traitements (ex: 'mal de tête', 'diabète')
   - Générale : Salutations, questions personnelles, remerciements (ex: 'bonjour', 'merci')
2. Si la question est GÉNÉRALE :
   - Utilise l'outil general_response avec [question] uniquement.
   - Réponds dans la langue spécifiée par [language].
   - Formate ta réponse finale comme suit : "Final Answer: [TYPE: general] [réponse]"
3. Si la question est MÉDICALE :
   - Utilise l'outil search_medical_docs avec [question] uniquement.
   - Intègre les sources dans ta réponse avec la mention "[Source]".
   - Ajoute à la fin : "Consultez un professionnel de santé."
   - Réponds dans la langue spécifiée par [language].
   - Formate ta réponse finale comme suit : "Final Answer: [TYPE: medical] [réponse]"

Exemples de réponses attendues :
- Pour "bonjour" :
  Thought: La question est une salutation, donc de type GÉNÉRALE.
  Action: general_response
  Action Input: bonjour
  Observation: Bonjour ! Je suis AstraMed, votre assistant virtuel d'information médicale. Comment puis-je vous aider aujourd'hui ? ...
  Final Answer: [TYPE: general] Bonjour ! Je suis AstraMed, votre assistant virtuel d'information médicale. Comment puis-je vous aider aujourd'hui ? N'oubliez pas que je ne peux pas donner d'avis médical.
- Pour "quels sont les symptômes du diabète" :
  Thought: La question concerne une maladie, donc de type MÉDICALE.
  Action: search_medical_docs
  Action Input: quels sont les symptômes du diabète
  Observation: Les symptômes du diabète incluent ...
  Final Answer: [TYPE: medical] Les symptômes du diabète incluent ... [Source]. Consultez un professionnel de santé.

Entrée complète : {input}
{agent_scratchpad}
"""

        # Configure prompt and LLM chain
        prompt_template = PromptTemplate(
            input_variables=["input", "agent_scratchpad"],
            template=agent_prompt
        )
        llm_chain = LLMChain(llm=llm, prompt=prompt_template)

        # Initialize agent with iteration limit
        agent_instance = ZeroShotAgent(
            llm_chain=llm_chain,
            tools=[tool_search, tool_general],
            verbose=True
        )
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent_instance,
            tools=[tool_search, tool_general],
            verbose=True,
            max_iterations=1  # Limit to one iteration
        )

        # Format user input
        user_query = f"{user_input.question}\nLangue de réponse : {user_input.language}"

        # Run the agent
        agent_output = agent_executor.run(user_query)
        print(f"[DEBUG] Agent output raw: {agent_output}")

        # Parse the agent's response
        parsed_response = parse_agent_output(agent_output)
        response_type = parsed_response["type"]
        generated_response = parsed_response["generated_response"]

        # Retrieve relevant documents for medical responses
        if response_type == "medical":
            _, relevant_docs = search_medical_docs(user_input.question, user_input.similarity_threshold)
        else:
            relevant_docs = []

        print(f"[AstraMed] Réponse finale: {response_type} - {generated_response}")
        print(f"[DEBUG] Réponse JSON : {{'type': '{response_type}', 'generated_response': '{generated_response}', 'answers': {relevant_docs}}}")

        # Return the final response
        return {
            "type": response_type,
            "generated_response": generated_response,
            "answers": relevant_docs if response_type == "medical" else []
        }
    except Exception as e:
        print(f"❌ Erreur détaillée: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement : {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8181)
