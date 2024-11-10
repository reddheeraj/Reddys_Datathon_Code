import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(embedding1, embedding2):
    """Calculate cosine similarity between two embeddings."""
    return cosine_similarity([embedding1], [embedding2])[0][0]

def log(message):
    """Log messages for debugging or tracking purposes."""
    print(f"[LOG] {message}")
