import os
from dotenv import load_dotenv
from langchain_google_cloud_sql_pg import PostgresEngine, PostgresVectorStore
from langchain_google_vertexai import VertexAIEmbeddings
from sqlalchemy.exc import ProgrammingError
import asyncio

# 🔹 Charger les variables d'environnement
load_dotenv()
DB_PASSWORD = os.environ["DB_PASSWORD"]

# 🔹 Informations Cloud SQL
PROJECT_ID = "my-dproject-452220"
INSTANCE = "elyessiki"
REGION = "europe-west1"
DATABASE = "health_database"
DB_USER = "postgres"
TABLE_NAME = "elyes_med"

# 🔹 Initialiser l'embedding model
def get_embeddings() -> VertexAIEmbeddings:
    return VertexAIEmbeddings(
        model_name="textembedding-gecko@latest",
        project=PROJECT_ID
    )

# 🔹 Connexion à la base de données
def create_cloud_sql_database_connection() -> PostgresEngine:
    return PostgresEngine.from_instance(
        project_id=PROJECT_ID,
        instance=INSTANCE,
        region=REGION,
        database=DATABASE,
         user=DB_USER,
        password=DB_PASSWORD,
    )

# 🔹 Création de la table si elle n'existe pas
async def create_table_if_not_exists(table_name: str, engine: PostgresEngine) -> None:
    try:
        await engine.init_vectorstore_table(
            table_name=table_name,  
            vector_size=768,
        )
        print(f"✅ Table '{table_name}' créée avec succès (ou déjà existante).")
    except ProgrammingError:
        print(f"⚠ La table '{table_name}' existe déjà.")

# 🔹 Récupérer le vector store
def get_vector_store(engine: PostgresEngine, table_name: str, embedding: VertexAIEmbeddings) -> PostgresVectorStore:
    return PostgresVectorStore.create_sync(
        engine=engine,
        table_name=table_name,
        embedding_service=embedding,
    )

# 🔹 Fonction principale
async def main():
    print("🔹 Connexion à la base de données...")
    engine = create_cloud_sql_database_connection()
    print("✅ Connexion réussie.")

    print(f"\n🔹 Vérification de la table '{TABLE_NAME}'...")
    await create_table_if_not_exists(TABLE_NAME, engine)
    print("✅ Vérification/Création table terminée.")
    
if _name_ == '_main_':
    try:
        asyncio.run(main())  # Lancer l'exécution asynchrone
    except RuntimeError:
        # Alternative pour éviter l'erreur d'event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

    print("\n🎉 Ingestion terminée. La table est prête à être utilisée.")
