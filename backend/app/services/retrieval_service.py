import psycopg
import numpy as np
from typing import List, Dict, Any, Tuple
from bson import ObjectId
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
        """Chunks document text, generates 384-dim embeddings, stores in MongoDB + PostgreSQL vector store."""
        if not text or not text.strip():
            return

        db = get_mongo_db()
        doc_oid = ObjectId(document_id) if ObjectId.is_valid(document_id) else document_id
        chunks = self._chunk_text(text, chunk_size=400, overlap=40)

        # 1. Store chunks & vectors in MongoDB document_chunks
        await db.document_chunks.delete_many({"document_id": doc_oid})
        chunk_docs = []
        for idx, chunk in enumerate(chunks):
            vec = self.embed_text(chunk)
            chunk_docs.append({
                "document_id": doc_oid,
                "chunk_index": idx,
                "chunk_text": chunk,
                "embedding": vec
            })
        if chunk_docs:
            await db.document_chunks.insert_many(chunk_docs)

        # 2. Store in PostgreSQL Vector Store
        try:
            pg_uri = settings.POSTGRES_URI
            conn = psycopg.connect(pg_uri, autocommit=True, connect_timeout=3)
            with conn.cursor() as cur:
                for idx, chunk in enumerate(chunks):
                    vec = self.embed_text(chunk)
                    cur.execute("""
                        INSERT INTO document_embeddings (document_id, chunk_index, chunk_text, embedding)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (document_id, chunk_index) DO UPDATE
                        SET chunk_text = EXCLUDED.chunk_text, embedding = EXCLUDED.embedding;
                    """, (str(document_id), idx, chunk, vec))
            conn.close()
            print(f"Document {document_id} indexed in PostgreSQL Vector Store successfully.")
        except Exception as e:
            print(f"PostgreSQL vector index note: {e}")

    async def hybrid_search(self, query: str, top_k: int = 5) -> Tuple[List[str], str]:
        """Combines PostgreSQL / MongoDB Vector Cosine Search with Keyword matching."""
        semantic_docs = []
        q_vec = np.array(self.embed_text(query))
        q_norm = np.linalg.norm(q_vec)
        
        # 1. Try PostgreSQL Vector search
        try:
            conn = psycopg.connect(settings.POSTGRES_URI, autocommit=True, connect_timeout=3)
            with conn.cursor() as cur:
                cur.execute("SELECT document_id, chunk_text, embedding FROM document_embeddings LIMIT 300;")
                rows = cur.fetchall()
                scores = []
                for r in rows:
                    doc_id, text, emb = r[0], r[1], r[2]
                    if emb:
                        d_vec = np.array(emb, dtype=float)
                        d_norm = np.linalg.norm(d_vec)
                        sim = float(np.dot(q_vec, d_vec) / (q_norm * d_norm)) if (q_norm * d_norm) > 0 else 0.0
                        scores.append({"document_id": doc_id, "text": text, "score": sim})
                scores.sort(key=lambda x: x["score"], reverse=True)
                semantic_docs = scores[:top_k]
            conn.close()
        except Exception as e:
            print(f"PostgreSQL search note: {e}")

        # 2. Fallback to MongoDB Vector Cosine Similarity Search if PostgreSQL is offline
        if not semantic_docs:
            db = get_mongo_db()
            cursor = db.document_chunks.find({}).limit(300)
            scores = []
            async for chunk_doc in cursor:
                d_vec = np.array(chunk_doc.get("embedding", []), dtype=float)
                if len(d_vec) == 384:
                    d_norm = np.linalg.norm(d_vec)
                    sim = float(np.dot(q_vec, d_vec) / (q_norm * d_norm)) if (q_norm * d_norm) > 0 else 0.0
                    scores.append({
                        "document_id": str(chunk_doc.get("document_id")),
                        "text": chunk_doc.get("chunk_text", ""),
                        "score": sim
                    })
            scores.sort(key=lambda x: x["score"], reverse=True)
            semantic_docs = scores[:top_k]

        # 3. MongoDB Keyword/Structured Search
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

    def _chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 40) -> List[str]:
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
