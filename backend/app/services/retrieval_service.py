import psycopg
from typing import List, Dict, Any, Tuple
from app.core.config import settings
from app.db.database import get_mongo_db

class RetrievalService:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        return self._model

    def embed_text(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    async def index_document(self, document_id: str, text: str):
        """Chunks document text, generates 384-dim embeddings, stores in pgvector."""
        if not text.strip():
            return

        chunks = self._chunk_text(text, chunk_size=500, overlap=50)
        
        try:
            conn = psycopg.connect(settings.POSTGRES_URI, autocommit=True)
            with conn.cursor() as cur:
                for idx, chunk in enumerate(chunks):
                    vec = self.embed_text(chunk)
                    vec_str = "[" + ",".join(map(str, vec)) + "]"
                    cur.execute("""
                        INSERT INTO document_embeddings (document_id, chunk_index, chunk_text, embedding)
                        VALUES (%s, %s, %s, %s::vector)
                        ON CONFLICT (document_id, chunk_index) DO UPDATE
                        SET chunk_text = EXCLUDED.chunk_text, embedding = EXCLUDED.embedding;
                    """, (str(document_id), idx, chunk, vec_str))
            conn.close()
        except Exception as e:
            print(f"pgvector indexing note: {e}")

    async def hybrid_search(self, query: str, top_k: int = 5) -> Tuple[List[str], str]:
        """Combines pgvector semantic search with MongoDB keyword search."""
        semantic_docs = []
        try:
            query_vec = self.embed_text(query)
            vec_str = "[" + ",".join(map(str, query_vec)) + "]"
            conn = psycopg.connect(settings.POSTGRES_URI, autocommit=True)
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT document_id, chunk_text, (1 - (embedding <=> %s::vector)) as similarity
                    FROM document_embeddings
                    ORDER BY similarity DESC
                    LIMIT %s;
                """, (vec_str, top_k))
                rows = cur.fetchall()
                for r in rows:
                    semantic_docs.append({"document_id": r[0], "text": r[1], "score": float(r[2])})
            conn.close()
        except Exception as e:
            print(f"pgvector search note: {e}")

        # MongoDB Keyword/Structured Search
        db = get_mongo_db()
        keyword_docs = []
        regex_query = {"$regex": query, "$options": "i"}
        cursor = db.extracted_documents.find({
            "$or": [
                {"document_type": regex_query},
                {"fields.invoice_number": regex_query},
                {"fields.po_number": regex_query},
                {"fields.vendor": regex_query},
                {"fields.customer": regex_query},
                {"fields.lead_name": regex_query}
            ]
        }).limit(top_k)

        async for doc in cursor:
            keyword_docs.append(str(doc.get("document_id")))

        # Merge source document IDs
        source_ids = list(set([d["document_id"] for d in semantic_docs] + keyword_docs))
        
        context_snippets = [d["text"] for d in semantic_docs[:3]]
        context_str = "\n---\n".join(context_snippets) if context_snippets else "No direct document passage matches found."

        return source_ids, context_str

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        words = text.split()
        if len(words) <= chunk_size:
            return [text]
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
        return chunks

retrieval_service = RetrievalService()
