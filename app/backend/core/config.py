import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Manufacturing Quality Assistant"
    API_V1_STR: str = "/api"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DOCS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))), "data", "docs")
    INDEX_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))), "data", "index")
    
    # RAG Settings (Increased for better context retention)
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    VECTOR_DB_K: int = 8
    
    # LLM Settings
    GOOGLE_API_KEY: str = ""  # Set via environment variable or .env file
    LLM_MODEL: str = "gemini-2.5-flash" 
    
    class Config:
        env_file = ".env"

settings = Settings()
