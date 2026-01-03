import numpy as np
from numpy.linalg import norm

def compute_similarity(embedding1, embedding2):
    """Compute cosine similarity between two embeddings."""
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)
    similarity = np.dot(embedding1, embedding2) / (norm(embedding1) * norm(embedding2))
    return similarity