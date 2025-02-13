import time
from generate_embeddings import generate_embedding
from superset_client import get_superset_token, get_charts
from database import store_embedding

def update_charts():
    while True:
        token = get_superset_token()
        charts = get_charts(token)

        for chart in charts:
            
            
            # Check if the 'changed_on' or an equivalent field exists
            last_updated = chart.get("changed_on")  # Default to 'changed_on'
            
            if not last_updated:
                # You can try other potential fields here if 'changed_on' is not available
                last_updated = chart.get("last_modified")  # Example: try 'last_modified'
            
            if not last_updated:
                
                continue  # Skip if no last updated timestamp is found

            metadata_text = f"{chart['slice_name']}, {chart['viz_type']}, {chart.get('query_context', '')}"
            vector = generate_embedding(metadata_text)
            store_embedding(chart['id'], chart['slice_name'], vector, last_updated)

        print("✅ Chart embeddings updated. Sleeping for 1 minute...")
        time.sleep(60)  # Sleep for 60 seconds before running again

if __name__ == "__main__":
    update_charts()
