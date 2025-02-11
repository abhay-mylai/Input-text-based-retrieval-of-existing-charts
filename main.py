from generate_embeddings import generate_embedding
from superset_client import get_superset_token, get_charts
from database import store_embedding, find_similar_charts
from query_input import process_query

def main():
    token = get_superset_token()
    charts = get_charts(token)

    # Ensure charts data is valid
    for chart in charts:
        chart_id = chart["id"]
        chart_name = chart["slice_name"]
        metadata_text = f"{chart_name}, {chart['viz_type']}, {chart.get('query_context', '')}"

        vector = generate_embedding(metadata_text)
        store_embedding(chart_id, chart_name, vector)

    # Example Query: Find similar charts to a given one
    while True:
        
        test_vector = process_query()
        similar_charts = find_similar_charts(test_vector)
        
        if similar_charts:
            print("\n🔍 Similar Charts:")
            for chart in similar_charts:
                print(f"➡ {chart[1]} (ID: {chart[0]}, Similarity: {chart[2]:.4f})")
        else:
            print("❌ No charts found with similarity ≥ 0.9")

        string = input("continue? (y/n): ")
        if string == "n":
            break

        print("--------------------------------\n")

if __name__ == "__main__":
    main()