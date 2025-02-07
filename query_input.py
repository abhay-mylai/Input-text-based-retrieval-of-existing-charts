import re
from store_embeddings import generate_embedding 

def preprocess_query(query):
    query = query.lower()  # Convert to lowercase

    query = re.sub(r'[^a-z0-9\s]', '', query)  # Remove special characters
    query = query.strip()  # Remove extra spaces
    return query

def process_query():
    query = input("Enter your query: ")
    cleaned_query = preprocess_query(query)
    
    # Step 2: Convert query to vector embedding
    query_embedding = generate_embedding(cleaned_query)
    
    print(f"Query Embedding: {query_embedding}")
    return query_embedding 


if __name__ == "__main__":
    process_query()
