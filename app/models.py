from pydantic import BaseModel
from typing import List, Optional, Any

# --- Original Internal Models ---

class QueryRequest(BaseModel):
    """
    Defines the structure for a single query request (used in original endpoints).
    """
    query: str

class QueryResponse(BaseModel):
    """
    Defines the detailed response for a single query, including decision,
    justification, and confidence.
    """
    response: str
    decision: str
    amount: Optional[str] = None
    confidence: Optional[float] = None
    justification: Optional[str] = None
    referenced_clauses: Optional[List[str]] = None

class DocumentChunk(BaseModel):
    """
    Represents a single chunk of a document, including its text, metadata,
    and vector embedding.
    """
    id: str
    text: str
    metadata: dict
    embedding: Optional[List[float]] = None

class ProcessingResult(BaseModel):
    """
    Summarizes the result of processing a document.
    """
    chunks_processed: int
    document_name: str
    status: str
    message: str

# --- New Models for HackRX Competition ---

class HackRXRequest(BaseModel):
    documents: str
    questions: List[str]

class HackRXResponse(BaseModel):
    answers: List[str]