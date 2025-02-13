import time
from generate_embeddings import generate_embedding
from superset_client import get_superset_token, get_charts
from database import store_embedding

def update_charts():
    while True:
        token = get_superset_token()
        charts = get_charts(token)

        for chart in charts:
            chart_id = chart["id"]
            chart_name = chart["slice_name"]
            last_updated = chart["changed_on"]  # Timestamp from Superset
            metadata_text = f"{chart_name}, {chart['viz_type']}, {chart.get('query_context', '')}"

            vector = generate_embedding(metadata_text)
            store_embedding(chart_id, chart_name, vector, last_updated)

        print("✅ Chart embeddings updated. Sleeping for 1 minute...")
        time.sleep(60)

if __name__ == "__main__":
    update_charts()
