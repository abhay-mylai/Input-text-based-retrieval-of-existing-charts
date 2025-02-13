from superset_client import get_superset_token
from database import find_similar_charts
from query_input import process_query

def main():
    token = get_superset_token()

    # Example Query: Find similar charts to a given one
    while True:
        test_vector = process_query()
        similar_charts = find_similar_charts(test_vector, token)
        
        if similar_charts:
            print("\n🔍 Similar Charts:")
            for chart in similar_charts:
                chart_id, chart_name, similarity, permalink = chart
                print(f"➡ {chart_name} (ID: {chart_id}, Similarity: {similarity:.4f})")
                print(f"🔗 Permalink: {permalink}\n")
        else:
            print("❌ No charts found with similarity ≥ 0.2")

        string = input("continue? (y/n): ")
        if string != "y":
            break

        print("--------------------------------\n")

if __name__ == "__main__":
    main()