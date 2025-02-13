import psycopg2
import numpy as np
import requests
from config import DB_CONFIG, SUPERSET_URL
from superset_client import get_chart_permalink

# Store chart embeddings in PostgreSQL (pgvector)
def store_embedding(chart_id, chart_name, vector, last_updated):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Ensure table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chart_embeddings (
            chart_id INT PRIMARY KEY,
            chart_name TEXT,
            embedding vector(384),
            last_updated TIMESTAMP  -- Store last updated timestamp
        )
    """)

    # Check if the chart already exists and if it was updated
    cur.execute("""
        SELECT last_updated FROM chart_embeddings WHERE chart_id = %s
    """, (chart_id,))
    
    row = cur.fetchone()
    
    if row is None or row[0] < last_updated:  # If new chart or updated chart
        cur.execute("""
            INSERT INTO chart_embeddings (chart_id, chart_name, embedding, last_updated)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (chart_id) DO UPDATE 
            SET embedding = EXCLUDED.embedding, last_updated = EXCLUDED.last_updated
        """, (chart_id, chart_name, np.array(vector).tolist(), last_updated))

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
