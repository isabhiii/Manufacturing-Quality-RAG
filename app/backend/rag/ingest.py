import os
import shutil
import threading
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.backend.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global lock to prevent concurrent indexing which corrupts ChromaDB
_ingestion_lock = threading.Lock()

def load_documents(source_dir: str) -> List[Document]:
    """Loads all PDF documents from the source directory with better metadata tracking."""
    documents = []
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
        return []

    for filename in os.listdir(source_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(source_dir, filename)
            try:
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                # Explicitly stamp documents with source and 1-based page numbers
                for doc in docs:
                    doc.metadata["source"] = filename
                    # PDF page indexes are 0-based, convert to 1-based for users
                    page_num = doc.metadata.get("page", 0) + 1
                    doc.metadata["page"] = page_num
                documents.extend(docs)
                logger.info(f"Loaded {len(docs)} pages from {filename}")
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
    return documents

def chunk_documents(documents: List[Document]) -> List[Document]:
    """Splits documents into semantic chunks while preserving source metadata."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        add_start_index=True,
    )
    # metadata is preserved by default in LangChain's RecursiveCharacterTextSplitter
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
    return chunks

def index_chunks(chunks: List[Document], index_dir: str):
    """Indexes chunks into ChromaDB."""
    if not chunks:
        logger.warning("No chunks to index.")
        return

    embedding_function = SentenceTransformerEmbeddings(model_name=settings.EMBEDDING_MODEL)
    
    # Ensure index_dir is completely clean before building
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)
    os.makedirs(index_dir)

    # Initialize Chroma and persist
    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=index_dir
    )
    logger.info(f"Successfully indexed {len(chunks)} chunks to {index_dir}")

def ingest_docs():
    """Main entry point for ingestion with active locking."""
    if _ingestion_lock.locked():
        logger.warning("Ingestion already in progress. Skipping concurrent task.")
        return

    with _ingestion_lock:
        logger.info("Starting atomic ingestion...")
        try:
            docs = load_documents(settings.DOCS_DIR)
            if not docs:
                # If no docs, ensure index is cleared
                if os.path.exists(settings.INDEX_DIR):
                    shutil.rmtree(settings.INDEX_DIR)
                logger.info("No documents found. Index cleared.")
                return
                
            chunks = chunk_documents(docs)
            index_chunks(chunks, settings.INDEX_DIR)
            logger.info("Atomic ingestion complete.")
        except Exception as e:
            logger.error(f"Ingestion critical failure: {e}")

if __name__ == "__main__":
    ingest_docs()
