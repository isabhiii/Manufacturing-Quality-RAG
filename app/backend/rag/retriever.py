from typing import List, Tuple
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document
from app.backend.core.config import settings

class Retriever:
    def __init__(self):
        self.embedding_function = SentenceTransformerEmbeddings(model_name=settings.EMBEDDING_MODEL)
        self.db = Chroma(
            persist_directory=settings.INDEX_DIR,
            embedding_function=self.embedding_function
        )

    def retrieve(self, query: str, k: int = settings.VECTOR_DB_K) -> List[Tuple[Document, float]]:
        """
        Retrieves top-k documents relevant to the query.
        Returns a list of tuples (Document, score). 
        Note: Chroma functionality might return scores differently (distance vs similarity).
        We will use similarity_search_with_score.
        """
        # Chrome similarity_search_with_score returns L2 distance by default (lower is better)
        # unless configured otherwise.
        results = self.db.similarity_search_with_score(query, k=k)
        return results
