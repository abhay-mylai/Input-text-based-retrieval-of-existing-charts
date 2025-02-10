import requests
import psycopg2
import numpy as np
from generate_embeddings import generate_embedding
from query_input import process_query
from config import SUPERSET_URL, USERNAME, PASSWORD, DB_CONFIG


# Authenticate with Superset API
import jwt  # PyJWT for debugging
def get_superset_token():
    auth_url = f"{SUPERSET_URL}/api/v1/security/login"
    response = requests.post(auth_url, json={"username": USERNAME, "password": PASSWORD, "provider": "db"})  


    if response.status_code == 200:
        token = response.json()["access_token"]
        
        # Decode token for debugging
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(f"🔍 Token payload: {decoded_token}")  

        # Convert 'sub' to string if necessary
        if "sub" in decoded_token and not isinstance(decoded_token["sub"], str):
            print(f"⚠ Warning: 'sub' is not a string! Found type: {type(decoded_token['sub'])}")
            decoded_token["sub"] = str(decoded_token["sub"])  # Convert it to a string
            token = jwt.encode(decoded_token, key="wN9Z-V3cPFHtV2rVAo4JbUud0VYAX_NvDbkq9b4llUY", algorithm="HS256")  # Re-encode token (only for debugging)

        print(f"✅ Superset token: {token[:10]}...")  
        return token  
    
    else:
        raise Exception(f"❌ Authentication Failed: {response.status_code} - {response.text}")


# Fetch all charts from Superset
def get_charts(token):
    charts_url = f"http://127.0.0.1:5000/api/v1/chart"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Sending request to {charts_url} with headers {headers}")  # For debugging
    
    response = requests.get(charts_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching charts: {response.status_code} - {response.text}")
        return []  # Return an empty list in case of failure
    else:
        try:
            data = response.json()
            print(f"Response data: {data}")  # Debug the response data
            return data.get("result", [])
        except ValueError as e:
            print(f"Failed to parse response: {e}")
            return []  # Return an empty list if parsing fails


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

    # Print debug info
    print(f"📌 Storing: {chart_id} | {chart_name} | {vector[:5]}...")

    # Insert or update embedding
    cur.execute("""
        INSERT INTO chart_embeddings (chart_id, chart_name, embedding)
        VALUES (%s, %s, %s)
        ON CONFLICT (chart_id) DO UPDATE SET embedding = EXCLUDED.embedding
    """, (chart_id, chart_name, np.array(vector).tolist()))

    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ Successfully stored: {chart_name} (ID: {chart_id})")


# Find similar charts using vector similarity search
def find_similar_charts(vector, top_k=5):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Convert numpy array to pgvector format (comma-separated)
    vector_str = "[" + ",".join(map(str, vector)) + "]"

    cur.execute("""
        SELECT chart_id, chart_name, 1 - (embedding <=> %s::vector) AS similarity
        FROM chart_embeddings
        ORDER BY similarity DESC
        LIMIT %s
    """, (vector_str, top_k))  # ✅ Ensure `vector` type conversion

    results = cur.fetchall()
    cur.close()
    conn.close()
    return results


# Main Execution
def main():
    token = get_superset_token()
    charts = get_charts(token)

    # Ensure charts data is valid
   

    for chart in charts:
        chart_id = chart["id"]
        chart_name = chart["slice_name"]
        metadata_text = f"{chart_name}, {chart['viz_type']}, {chart.get('query_context', '')}"

        vector = generate_embedding(metadata_text)
        print(f"🛠 Generated vector for {chart_name}: {vector[:5]}...")
        store_embedding(chart_id, chart_name, vector)

        print(f"✔ Stored embedding for chart: {chart_name} (ID: {chart_id})")

    # Example Query: Find similar charts to a given one
    test_vector = process_query()
    similar_charts = find_similar_charts(test_vector)

    print("\n🔍 Similar Charts:")
    for chart in similar_charts:
        print(f"➡ {chart[1]} (ID: {chart[0]}, Similarity: {chart[2]:.4f})")

if __name__ == "__main__":
    main()
