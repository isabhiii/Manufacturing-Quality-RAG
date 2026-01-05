import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.backend.core.config import settings
from app.backend.rag.ingest import ingest_docs
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def run_ingestion_task():
    """Background task to run ingestion."""
    logger.info("Triggering background ingestion...")
    try:
        ingest_docs()
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")

@router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        # Ensure docs directory exists
        if not os.path.exists(settings.DOCS_DIR):
            os.makedirs(settings.DOCS_DIR)
            
        file_path = os.path.join(settings.DOCS_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"File {file.filename} saved to {settings.DOCS_DIR}")
        
        # Trigger re-indexing in background
        background_tasks.add_task(run_ingestion_task)
        
        return {"message": f"File {file.filename} uploaded successfully. Ingestion started."}
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
