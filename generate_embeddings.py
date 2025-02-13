from sentence_transformers import SentenceTransformer
from attention_mechanism import apply_attention

# Load pre-trained model and spaCy for attention mechanism
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text):
    # Apply attention mechanism to input text
    attention_applied_text = apply_attention(text)

    # Ensure that the input is always passed as a list, even if it's a single string
    if isinstance(attention_applied_text, str):
        attention_applied_text = [attention_applied_text]  # Convert to list if it's a single string

    # Generate embedding
    return model.encode(attention_applied_text).tolist()
