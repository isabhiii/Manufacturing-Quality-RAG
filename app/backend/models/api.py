from pydantic import BaseModel
from typing import List, Optional

# Request Models
class QueryRequest(BaseModel):
    question: str

# Response Models
class Citation(BaseModel):
    doc_id: Optional[str] = None
    doc_name: str
    page: Optional[int] = None
    score: float

class RawContext(BaseModel):
    content: str
    doc_name: str
    page: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    raw_context: List[RawContext]
