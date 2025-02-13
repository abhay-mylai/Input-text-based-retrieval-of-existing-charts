import psycopg2
import numpy as np
import requests
from config import DB_CONFIG, SUPERSET_URL
from superset_client import get_chart_permalink

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


def find_similar_charts(vector, token, top_k=3, threshold=0.2):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

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

    similar_charts = []
    for chart_id, chart_name, similarity in results:
        if similarity >= threshold:
            permalink = get_chart_permalink(chart_id, token)  # Fetch correct permalink
            
            # If Superset API fails, generate fallback URL
            if not permalink:
                permalink = f"{SUPERSET_URL}/superset/explore/?slice_id={chart_id}"

            similar_charts.append((chart_id, chart_name, similarity, permalink))

    return similar_charts
