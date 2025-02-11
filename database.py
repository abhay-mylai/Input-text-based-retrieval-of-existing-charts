import psycopg2
import numpy as np
from config import DB_CONFIG

# Store chart embeddings in PostgreSQL (pgvector)
def store_embedding(chart_id, chart_name, vector):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Ensure table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chart_embeddings (
            chart_id INT PRIMARY KEY,
            chart_name TEXT,
            embedding vector(384)  -- Using 384-dim embeddings from MiniLM
        )
    """)


    # Insert or update embedding
    cur.execute("""
        INSERT INTO chart_embeddings (chart_id, chart_name, embedding)
        VALUES (%s, %s, %s)
        ON CONFLICT (chart_id) DO UPDATE SET embedding = EXCLUDED.embedding
    """, (chart_id, chart_name, np.array(vector).tolist()))

    conn.commit()
    cur.close()
    conn.close()

    


def find_similar_charts(vector, top_k=3, threshold=0.5):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Convert numpy array to pgvector format (comma-separated)
    vector_str = "[" + ",".join(map(str, vector)) + "]"

    cur.execute("""
        SELECT chart_id, chart_name, 1 - (embedding <=> %s::vector) AS similarity
        FROM chart_embeddings
        ORDER BY similarity DESC
        LIMIT %s
    """, (vector_str, top_k))

    results = cur.fetchall()
    cur.close()
    conn.close()

    # Filter results based on threshold
    filtered_results = [chart for chart in results if chart[2] >= threshold]

    return filtered_results
