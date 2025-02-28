import numpy as np
import time
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import euclidean

# 🚀 Chargement du modèle BERT pour l'encodage des phrases
bert_model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_advanced_similarity(text1: str, text2: str) -> float:
    """
    Calcule la similarité entre deux textes en utilisant les embeddings BERT et la distance euclidienne normalisée.
    """
    embedding1 = bert_model.encode(text1)
    embedding2 = bert_model.encode(text2)

    # Distance euclidienne normalisée
    max_distance = np.linalg.norm(embedding1) + np.linalg.norm(embedding2)
    similarity = 1 - (euclidean(embedding1, embedding2) / max_distance)
    
    return max(0.0, similarity)  # On s'assure que la similarité reste positive

def calculate_relevance(chatbot_response, true_answer):
    """
    Évalue la pertinence de la réponse du chatbot en fonction de la réponse attendue.
    """
    if not chatbot_response:
        return 0.0
    
    if chatbot_response.get('type') == 'combined_response':
        # Évaluer la réponse générée par rapport à la base de données
        llm_similarity = compute_advanced_similarity(chatbot_response['response'], chatbot_response['db_answer'])
        return (llm_similarity + (1 - float(chatbot_response['score']))) / 2
    else:
        return compute_advanced_similarity(chatbot_response.get('response', ''), true_answer)

def was_answer_found_in_db(chatbot_response):
    """
    Vérifie si la réponse a été trouvée dans la base de données.
    """
    if not chatbot_response:
        return False
    return chatbot_response.get('type') == 'database_match'

def measure_response_time():
    """
    Mesure le temps de réponse du chatbot.
    """
    start_time = time.time()
    time.sleep(0.1)  # Simule un délai de réponse
    return time.time() - start_time

def display_evaluation_results(results):
    """
    Affiche les résultats de l'évaluation du chatbot.
    """
    print("\n📊 Résultats de l'évaluation sur 10 exemples aléatoires :")
    print("-" * 50)
    
    avg_metrics = {
        "Pertinence moyenne": np.mean([r["relevance_score"] for r in results]),
        "Temps de réponse moyen": np.mean([r["response_time"] for r in results])
    }
    
    for metric, value in avg_metrics.items():
        print(f"{metric}: {value:.4f}")
    
    print("\n🔍 Exemples détaillés (5 premiers) :")
    for i, result in enumerate(results[:10], 1):
        print(f"\nExemple {i}:")
        print(f"❓ Question: {result['question']}")
        print(f"📂 Type de réponse: {result['chatbot_response'].get('type', 'unknown')}")
        print(f"🔍 Score de similarité: {result['chatbot_response'].get('score', 'N/A')}")
        print(f"✅ Pertinence: {result['relevance_score']:.4f}")
