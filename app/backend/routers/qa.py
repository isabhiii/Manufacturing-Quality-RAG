from fastapi import APIRouter, HTTPException
from app.backend.models.api import QueryRequest, QueryResponse, Citation, RawContext
from app.backend.rag.pipeline import RAGPipeline
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize pipeline once (load model, etc.)
# In a real heavy app, use lifecycle events or dependency injection to load lazily or on startup
try:
    rag_pipeline = RAGPipeline()
except Exception as e:
    logger.error(f"Failed to initialize RAG Pipeline: {e}")
    # We don't raise here to allow app to start even if RAG fails (e.g. no index yet)
    rag_pipeline = None

@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG Pipeline not initialized (Index missing?)")
    
    try:
        result = rag_pipeline.run(request.question)
        
        # Format citations
        citations = []
        raw_context = []
        
        for doc, score in result["citations"]:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", None)
            
            # Note: Chroma score is distance (lower is better) or similarity?
            # Standard SentenceTransformer + Chroma usually defaults to L2 (distance).
            # But the 'similarity_search_with_score' naming suggests similarity?
            # Actually Chroma's default is L2. 
            # We will just pass the raw score for now or invert it if we assume Cosine.
            # Let's just output it as is.
            
            citations.append(Citation(
                doc_name=source,
                page=page,
                score=score
            ))
            
            raw_context.append(RawContext(
                content=doc.page_content,
                doc_name=source,
                page=page
            ))
            
        return QueryResponse(
            answer=result["answer"],
            citations=citations,
            raw_context=raw_context
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
