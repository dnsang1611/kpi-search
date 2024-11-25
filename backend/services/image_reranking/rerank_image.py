import numpy as np
from typing import List, Dict

class RerankImages:
    def __init__(self, alpha: float, beta: float, gamma: float):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def reformulate(self, query_vector: np.ndarray, relevant_vectors: List[np.ndarray], irrelevant_vectors: List[np.ndarray]) -> np.ndarray:
        if query_vector is None or not query_vector.size:
            text_query = np.zeros_like(relevant_vectors[0] if relevant_vectors else irrelevant_vectors[0])
        else:
            text_query = query_vector
        sum_relevant = np.sum(relevant_vectors, axis=0) if relevant_vectors else np.zeros_like(text_query)
        norm_relevant = sum_relevant / np.linalg.norm(sum_relevant) if np.linalg.norm(sum_relevant) != 0 else np.zeros_like(text_query)
        sum_irrelevant = np.sum(irrelevant_vectors, axis=0) if irrelevant_vectors else np.zeros_like(text_query)
        norm_irrelevnt = sum_irrelevant / np.linalg.norm(sum_irrelevant) if np.linalg.norm(sum_irrelevant) != 0 else np.zeros_like(text_query)
        modified_query = self.alpha * text_query + self.beta * norm_relevant - self.gamma * norm_irrelevnt
        return modified_query