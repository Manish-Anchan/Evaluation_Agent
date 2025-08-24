import numpy as np


def get_embedding(text: str, client, model):
    return np.array(client.feature_extraction(text, model=model), dtype="float32")

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))