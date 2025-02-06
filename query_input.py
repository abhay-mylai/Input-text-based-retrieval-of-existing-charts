import re

def preprocess_query(query):
    query = query.lower()  # Convert to lowercase
    query = re.sub(r'[^a-z0-9\s]', '', query)  # Remove special characters
    query = query.strip()  # Remove extra spaces
    return query

def get_user_query():
    query = input("Enter your query: ")
    return preprocess_query(query)

if __name__ == "__main__":
    user_query = get_user_query()
    print(f"Processed Query: {user_query}")
