import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Manufacturing Quality Assistant"
    API_V1_STR: str = "/api"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DOCS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))), "data", "docs")
    INDEX_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))), "data", "index")
    
    # RAG Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_DB_K: int = 5
    
    # LLM Settings
    GOOGLE_API_KEY: str = "" # Set via .env file
    LLM_MODEL: str = "gemini-2.0-flash" # Latest Flash model
    
    class Config:
        env_file = ".env"

settings = Settings()
