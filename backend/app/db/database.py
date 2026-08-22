import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import psycopg
from app.core.config import settings

# MongoDB Motor Client (Async)
mongo_client: AsyncIOMotorClient = None
db = None

def get_mongo_db():
    global mongo_client, db
    if mongo_client is None:
        mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = mongo_client[settings.MONGODB_DB_NAME]
    return db

async def init_db():
    try:
        database = get_mongo_db()
        # Initialize MongoDB indexes with 3.0s timeout
        async with asyncio.timeout(3.0):
            await database.users.create_index("email", unique=True)
            await database.refresh_tokens.create_index("token_hash", unique=True)
            await database.refresh_tokens.create_index("user_id")
            await database.documents.create_index("status")
            await database.documents.create_index("classification.document_type")
            await database.documents.create_index("uploaded_by")
            await database.documents.create_index([("created_at", -1)])
            await database.extracted_documents.create_index("document_id", unique=True)
            await database.extracted_documents.create_index("document_type")
            await database.extracted_documents.create_index("needs_review")
            await database.insights.create_index([("status", 1), ("severity", 1)])
            await database.insights.create_index("related_entity")
            await database.insights.create_index("type")
            await database.insights.create_index([("created_at", -1)])
            await database.erp_records.create_index([("record_type", 1), ("erp_status", 1)])
            await database.erp_records.create_index("source")
            await database.erp_records.create_index("party_name")
            await database.chat_sessions.create_index([("user_id", 1), ("updated_at", -1)])
            await database.audit_logs.create_index([("resource_type", 1), ("resource_id", 1)])
            await database.audit_logs.create_index([("user_id", 1), ("created_at", -1)])
            print("MongoDB indexes initialized successfully.")
    except Exception as e:
        print(f"MongoDB connection/index note: {e}")

    # Initialize PostgreSQL pgvector table if PostgreSQL is available
    try:
        conn = psycopg.connect(settings.POSTGRES_URI, autocommit=True, connect_timeout=3)
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS document_embeddings (
                    id           BIGSERIAL PRIMARY KEY,
                    document_id  VARCHAR(24) NOT NULL,
                    chunk_index  INT NOT NULL,
                    chunk_text   TEXT NOT NULL,
                    embedding    VECTOR(384) NOT NULL,
                    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
                    UNIQUE (document_id, chunk_index)
                );
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS document_embeddings_document_id_idx ON document_embeddings (document_id);")
        conn.close()
        print("PostgreSQL pgvector database initialized successfully.")
    except Exception as e:
        print(f"PostgreSQL pgvector initialization note: {e}")

