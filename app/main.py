import logging
import os
import shutil
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import models and services
from .models import (
    HackRXRequest,
    HackRXResponse,
    # Keep original models if other endpoints use them
)
from .document_processor import DocumentProcessor
from .query_processor import QueryProcessor
from .embedding_service import EmbeddingService
from .in_memory_vector_store import InMemoryVectorStore


# --- Load Environment Variables ---
load_dotenv()

# --- Setup Logging ---

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Security Setup ---
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify Bearer token for authentication"""
    expected_token = os.getenv("API_TOKEN", "de76f5235c90aed44bb592ab29e6649d9bb023277d2a45b20640fdcf40031d91")
    if credentials.credentials != expected_token:
        logger.warning(f"❌ Invalid token attempt: {credentials.credentials[:10]}...")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    logger.info("✅ Token validated successfully")
    return credentials

# --- Global Services ---
embedding_service: EmbeddingService
document_processor: DocumentProcessor
query_processor: QueryProcessor
vector_store: InMemoryVectorStore

# --- Application Lifespan (Startup/Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes the system on startup and handles shutdown."""
    global embedding_service, document_processor, query_processor, vector_store

    # --- ADDED: Diagnostic check for the API Key ---
    logger.info("--- CHECKING ENVIRONMENT VARIABLES ---")
    api_key_value = os.getenv("GEMINI_API_KEY")
    token_value = os.getenv("API_TOKEN")
    if api_key_value:
        logger.info("✅ SUCCESS: GEMINI_API_KEY was found!")
    else:
        logger.error("❌ FAILURE: GEMINI_API_KEY is NOT set. Check your .env file's name, location, and content.")
    if token_value:
        logger.info("✅ SUCCESS: API_TOKEN was found!")
    else:
        logger.info("⚠️ WARNING: API_TOKEN not set, using default token")
    logger.info("------------------------------------")
    # --- END of Diagnostic check ---

    try:
        logger.info("🚀 Initializing HackRX System...")

        embedding_service = EmbeddingService()
        vector_store = InMemoryVectorStore()  # Use in-memory store
        document_processor = DocumentProcessor(embedding_service, vector_store)
        query_processor = QueryProcessor(embedding_service, vector_store)

        logger.info("✅ HackRX System initialized successfully!")
        yield

    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {str(e)}")
        raise
    finally:
        logger.info("🛑 Shutting down HackRX system...")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="HackRX Insurance Claim System",
    description="LLM-powered document analysis for the HackRX competition.",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "HackRX Insurance System is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "service": "HackRX Insurance System",
        "version": "2.0.0",
        "timestamp": time.time()
    }

@app.post("/hackrx/run", response_model=HackRXResponse)
async def hackrx_run(request: HackRXRequest, credentials: HTTPAuthorizationCredentials = Security(verify_token)):
    """Main competition endpoint with authentication and explicit memory cleanup"""
    # Create temporary instances for this request
    temp_vector_store = None
    temp_query_processor = None

    try:
        start_time = time.time()
        logger.info(f"🔍 Processing HackRX request with {len(request.questions)} questions")
        logger.info(f"📄 Document URL: {request.documents}")

        # Process document from URL
        logger.info("📥 Downloading and processing document...")
        chunks = await document_processor.process_document_from_url(request.documents)

        if not chunks:
            logger.error("❌ No content extracted from document")
            return HackRXResponse(answers=["No content found in document"] * len(request.questions))

        # Create temporary vector store for this request
        temp_vector_store = InMemoryVectorStore()
        temp_query_processor = QueryProcessor(embedding_service, temp_vector_store)

        # Process all questions against the document
        logger.info("🤖 Processing queries with LLM...")
        answers = await temp_query_processor.process_batch_queries(request.questions, chunks)

        processing_time = time.time() - start_time
        logger.info(f"✅ Completed processing in {processing_time:.2f}s")
        logger.info(f"📊 Processed {len(chunks)} chunks, answered {len(answers)} questions")

        return HackRXResponse(answers=answers)

    except Exception as e:
        logger.error(f"❌ HackRX processing failed: {str(e)}")
        # Return error responses for all questions
        error_answers = [f"Unable to process question due to error: {str(e)}"] * len(request.questions)
        return HackRXResponse(answers=error_answers)
    
    finally:
        # Explicit cleanup
        if temp_vector_store:
            temp_vector_store.clear()
            logger.info("🧹 Explicitly cleared vector store memory")

        # Clear temporary variables
        temp_vector_store = None
        temp_query_processor = None
        chunks = None

        logger.info("🧼 Request-specific memory cleanup completed")

# --- Main Execution Block ---
# Change this line in main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",  # Changed from "app.main:app"
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False,  # Set to False for production
        log_level="info"
    )