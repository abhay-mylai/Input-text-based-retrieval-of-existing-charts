import spacy

nlp = spacy.load("en_core_web_sm")

# Helper function to apply attention mechanism
def apply_attention(text):
    doc = nlp(text)
    # Applying attention mechanism: Extracting the most important words based on named entities, noun chunks, etc.
    important_words = [token.text for token in doc if token.dep_ in ("nsubj", "dobj", "amod", "attr", "nmod") or token.pos_ in ("PROPN", "NOUN")]
    return " ".join(important_words)



