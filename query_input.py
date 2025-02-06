# query_input.py
def get_user_query():
    query = input("Enter your query: ")
    return query.strip()  # Removing extra spaces

if __name__ == "__main__":
    user_query = get_user_query()
    print(f"User Query: {user_query}")
