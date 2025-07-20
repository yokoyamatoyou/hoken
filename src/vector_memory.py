from dataclasses import dataclass, field
from typing import List, Dict

from .memory import MessageMemory

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class VectorMemory(MessageMemory):
    """Conversation memory backed by a simple vector store using TF-IDF."""

    messages: List[Dict[str, str]] = field(default_factory=list)

    def search(self, query: str, top_k: int = 3) -> List[str]:
        """Return the contents of the messages most similar to the query."""
        corpus = [m["content"] for m in self.messages]
        if not corpus:
            return []
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(corpus + [query])
        sims = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
        indices = sims.argsort()[::-1][:top_k]
        return [corpus[i] for i in indices]

