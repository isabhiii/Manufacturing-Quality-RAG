import os
import shutil
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

def load_documents(source_dir: str) -> List[Document]:
    """Loads all PDF documents from the source directory."""
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
                # Add source metadata just in case
                for doc in docs:
                   doc.metadata["source"] = filename
                   # Fix 0-based indexing to 1-based for humans
                   current_page = doc.metadata.get("page", 0)
                   doc.metadata["page"] = current_page + 1
                documents.extend(docs)
                logger.info(f"Loaded {len(docs)} pages from {filename}")
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
    return documents

def chunk_documents(documents: List[Document]) -> List[Document]:
    """Splits documents into semantic chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
    return chunks

def index_chunks(chunks: List[Document], index_dir: str):
    """Indexes chunks into ChromaDB."""
    if not chunks:
        logger.warning("No chunks to index.")
        return

    embedding_function = SentenceTransformerEmbeddings(model_name=settings.EMBEDDING_MODEL)
    
    # Verify if index_dir exists
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)

    # Initialize Chroma (persistent)
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=index_dir
    )
    logger.info(f"Indexed {len(chunks)} chunks to {index_dir}")

def ingest_docs():
    """Main entry point for ingestion."""
    logger.info("Starting ingestion...")
    docs = load_documents(settings.DOCS_DIR)
    chunks = chunk_documents(docs)
    
    # Optional: Clear existing index if doing a full re-index
    # For now, we appends. Ideally we might want to clean `settings.INDEX_DIR` first
    # if os.path.exists(settings.INDEX_DIR):
    #     shutil.rmtree(settings.INDEX_DIR)
        
    index_chunks(chunks, settings.INDEX_DIR)
    logger.info("Ingestion complete.")

if __name__ == "__main__":
    ingest_docs()
