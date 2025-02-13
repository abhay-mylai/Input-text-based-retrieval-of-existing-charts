import psycopg2
import numpy as np
import requests
from config import DB_CONFIG, SUPERSET_URL
from superset_client import get_chart_permalink

# Store chart embeddings in PostgreSQL (pgvector)
def store_embedding(chart_id, chart_name, vector, last_updated):
    vector = np.array(vector, dtype=np.float32).tolist()  # Ensure proper vector format

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Ensure table exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chart_embeddings (
                        chart_id INT PRIMARY KEY,
                        chart_name TEXT,
                        embedding vector(384),
                        last_updated TIMESTAMP
                    )
                """)

                # Check if chart exists
                cur.execute("SELECT last_updated FROM chart_embeddings WHERE chart_id = %s", (chart_id,))
                row = cur.fetchone()

                if row is None or row[0] < last_updated:
                    cur.execute("""
                        INSERT INTO chart_embeddings (chart_id, chart_name, embedding, last_updated)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (chart_id) DO UPDATE 
                        SET embedding = EXCLUDED.embedding, last_updated = EXCLUDED.last_updated
                    """, (chart_id, chart_name, vector, last_updated))

                    conn.commit()
                    print(f"Stored/Updated embedding for chart_id: {chart_id}")

    except psycopg2.Error as e:
        print(f"Database error in store_embedding: {e}")


# Find similar charts using pgvector
def find_similar_charts(vector, token, top_k=3, threshold=0.2):
    vector = np.array(vector, dtype=np.float32).flatten().tolist()  # Ensure it's a 1D list

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT chart_id, chart_name, 1 - (embedding <=> %s::vector) AS similarity
                    FROM chart_embeddings
                    ORDER BY similarity DESC
                    LIMIT %s
                """, (vector, top_k))

                results = cur.fetchall()

    except psycopg2.Error as e:
        print(f"Database error in find_similar_charts: {e}")
        return []

    similar_charts = []
    for chart_id, chart_name, similarity in results:
        if similarity >= threshold:
            permalink = get_chart_permalink(chart_id, token) or f"{SUPERSET_URL}/superset/explore/?slice_id={chart_id}"
            similar_charts.append((chart_id, chart_name, similarity, permalink))

    return similar_charts
