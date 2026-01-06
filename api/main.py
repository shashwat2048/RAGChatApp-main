"""
FastAPI backend for RAG Chatbot
Production-grade API with proper error handling, logging, and health checks
"""
import os
import sys
import logging
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.chatbot import RAGChatbot
from app.retriever import DocumentRetriever

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global chatbot instance
chatbot_instance: Optional[RAGChatbot] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global chatbot_instance
    
    # Startup
    logger.info("Starting RAG Chatbot API...")
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
        
        chatbot_instance = RAGChatbot(api_key)
        logger.info("Chatbot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {str(e)}")
        logger.warning("API will start but chat endpoints may not work until chatbot is initialized")
        chatbot_instance = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG Chatbot API...")
    chatbot_instance = None


# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Production-grade RAG Chatbot API with FAISS, Sentence-Transformers, and Google Gemini",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Chat request model."""
    query: str = Field(..., description="User query/question", min_length=1, max_length=1000)
    use_history: bool = Field(True, description="Whether to use conversation history")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the key points about Chartered Accountants?",
                "use_history": True,
                "session_id": "user-123"
            }
        }


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="Generated response")
    session_id: Optional[str] = Field(None, description="Session ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Based on the documents, Chartered Accountants...",
                "session_id": "user-123"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    chatbot_initialized: bool = Field(..., description="Whether chatbot is initialized")
    message: str = Field(..., description="Status message")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")


# Session management (in-memory, use Redis for production)
sessions: dict[str, RAGChatbot] = {}


def get_chatbot(session_id: Optional[str] = None) -> RAGChatbot:
    """Get chatbot instance for session."""
    if session_id:
        if session_id not in sessions:
            api_key = os.getenv('GEMINI_API_KEY')
            sessions[session_id] = RAGChatbot(api_key)
        return sessions[session_id]
    return chatbot_instance


# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    logger.error(f"ValueError: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid request", "detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    try:
        is_initialized = chatbot_instance is not None
        status_msg = "healthy" if is_initialized else "chatbot not initialized"
        
        return HealthResponse(
            status="ok",
            chatbot_initialized=is_initialized,
            message=status_msg
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="error",
            chatbot_initialized=False,
            message=f"Health check failed: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat endpoint for querying the RAG chatbot.
    
    - **query**: The user's question
    - **use_history**: Whether to use conversation history (default: True)
    - **session_id**: Optional session ID for conversation tracking
    """
    try:
        if not chatbot_instance and not request.session_id:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chatbot not initialized. Please check server logs."
            )
        
        chatbot = get_chatbot(request.session_id)
        
        if not chatbot:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chatbot not available"
            )
        
        logger.info(f"Processing query: {request.query[:50]}...")
        
        response_text = chatbot.chat(request.query, use_history=request.use_history)
        
        logger.info("Query processed successfully")
        
        return ChatResponse(
            response=response_text,
            session_id=request.session_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )


@app.delete("/chat/session/{session_id}", tags=["Chat"])
async def clear_session(session_id: str):
    """Clear conversation history for a session."""
    try:
        if session_id in sessions:
            sessions[session_id].clear_history()
            logger.info(f"Cleared history for session: {session_id}")
            return {"message": f"Session {session_id} history cleared"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/chat/clear", tags=["Chat"])
async def clear_chat():
    """Clear the default chatbot conversation history."""
    try:
        if chatbot_instance:
            chatbot_instance.clear_history()
            logger.info("Cleared default chatbot history")
            return {"message": "Chat history cleared"}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chatbot not initialized"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

