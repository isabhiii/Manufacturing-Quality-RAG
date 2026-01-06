from typing import List, Tuple
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document
from app.backend.core.config import settings

import os

class Retriever:
    def __init__(self):
        self.embedding_function = SentenceTransformerEmbeddings(model_name=settings.EMBEDDING_MODEL)

    def _get_db(self):
        """Re-initializes Chroma connection to ensure it syncs with physical files."""
        # Check if index directory exists and is not empty
        if not os.path.exists(settings.INDEX_DIR) or not os.listdir(settings.INDEX_DIR):
            return None
            
        return Chroma(
            persist_directory=settings.INDEX_DIR,
            embedding_function=self.embedding_function
        )

    def retrieve(self, query: str, k: int = settings.VECTOR_DB_K) -> List[Tuple[Document, float]]:
        """Retrieves top-k documents with a fresh DB connection and retry logic."""
        for attempt in range(3):
            db = self._get_db()
            if not db:
                time.sleep(1)  # Wait for index to be created
                continue
                
            try:
                # Standard retrieval
                return db.similarity_search_with_score(query, k=k)
            except Exception as e:
                # Handle cases where DB is specifically locked or corrupted during re-indexing
                logger.warning(f"Retrieval attempt {attempt+1} failed: {e}")
                time.sleep(2)  # Wait for ingestion to finish
                
        logger.error("All retrieval attempts failed.")
        return []
