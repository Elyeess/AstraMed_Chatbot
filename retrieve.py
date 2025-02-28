import os
from ingest import create_cloud_sql_database_connection, get_embeddings, get_vector_store
from langchain_google_cloud_sql_pg import PostgresVectorStore
from langchain_core.documents.base import Document
from config import TABLE_NAME

def get_relevant_documents(
    query: str, vector_store: PostgresVectorStore, similarity_threshold: float = 0.5
) -> list[Document]:
    """
    Retrieve the 3 most relevant documents based on a query using a vector store.

    Args:
        query (str): The search query string.
        vector_store (PostgresVectorStore): An instance of PostgresVectorStore.
        similarity_threshold (float, optional): Minimum similarity score to consider. Default is 0.5.

    Returns:
        list[Document]: A list of the top 3 relevant documents.
    """
    relevant_docs_scores = vector_store.similarity_search_with_relevance_scores(
        query=query, k=3  # On garde les 3 meilleurs documents
    )

    # Trier par score de similarité décroissant
    relevant_docs_scores.sort(key=lambda x: x[1], reverse=True)

    # Ajouter le score de similarité dans les métadonnées
    for doc, score in relevant_docs_scores:
        doc.metadata["score"] = score

    # Filtrer selon le seuil de similarité
    relevant_docs = [doc for doc, score in relevant_docs_scores if score >= similarity_threshold]

    return relevant_docs  # Retourne les 3 documents les plus pertinents

def format_relevant_documents(documents: list[Document]) -> str:
    """
    Format medical documents into a readable string.

    Args:
        documents (list[Document]): A list of medical QA documents.

    Returns:
        str: Formatted string with questions, answers, and sources.
    """
    formatted_docs = []
    for i, doc in enumerate(documents):
        formatted_doc = (
            f"📖 **Document {i+1}**:\n"
            f"🔹 **Question**: {doc.page_content}\n"
            f"💡 **Réponse**: {doc.metadata.get('answer', 'Non disponible')}\n"
            f"📚 **Source**: {doc.metadata.get('source', 'Inconnue')}\n"
            f"⚕️ **Domaine médical**: {doc.metadata.get('focus_area', 'Non spécifié')}\n"
            f"📊 **Score de similarité**: {doc.metadata.get('score', 'N/A')}\n"
            "-----"
        )
        formatted_docs.append(formatted_doc)
    return "\n".join(formatted_docs)

if __name__ == '__main__':
    engine = create_cloud_sql_database_connection()
    embedding = get_embeddings()
    vector_store = get_vector_store(engine, TABLE_NAME, embedding)
    
    test_query = "What are the treatments for Prescription and Illicit Drug Abuse ??"
    
    # Appel de la fonction avec un seuil de 0.5
    documents = get_relevant_documents(test_query, vector_store, similarity_threshold=0.5)
    
    # Affichage des documents
    doc_str = format_relevant_documents(documents)
    print("📌 Documents les plus pertinents :")
    print(doc_str)
    print("\n✅ Test passed successfully.")
