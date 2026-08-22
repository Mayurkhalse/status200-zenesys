import psycopg

def main():
    # 1. Connect to postgres default DB and set password
    try:
        conn = psycopg.connect('postgresql://postgres@localhost:5432/postgres', autocommit=True)
        with conn.cursor() as cur:
            cur.execute("ALTER USER postgres WITH PASSWORD 'postgres';")
            print("[1/3] PostgreSQL password set to 'postgres' successfully.")
            
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'intelliparse'")
            if not cur.fetchone():
                cur.execute("CREATE DATABASE intelliparse;")
                print("[2/3] Database 'intelliparse' created successfully.")
            else:
                print("[2/3] Database 'intelliparse' already exists.")
        conn.close()
    except Exception as e:
        print(f"PostgreSQL DB init note: {e}")

    # 2. Connect to intelliparse DB and enable pgvector
    try:
        conn2 = psycopg.connect('postgresql://postgres:postgres@localhost:5432/intelliparse', autocommit=True)
        with conn2.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("[3/3] pgvector extension enabled successfully in PostgreSQL!")
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS document_embeddings (
                    id SERIAL PRIMARY KEY,
                    document_id VARCHAR(64) NOT NULL,
                    chunk_index INT NOT NULL,
                    chunk_text TEXT NOT NULL,
                    embedding vector(384),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(document_id, chunk_index)
                );
            """)
            print("PostgreSQL document_embeddings table initialized with 384-dim vector support!")
        conn2.close()
    except Exception as e:
        print(f"pgvector extension error: {e}")

if __name__ == "__main__":
    main()
