"""
FastAPI application for Multi-Model AI Chat System.
Provides REST API endpoints for chat and document upload.
"""

import os
import shutil
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import config
from app.session import session_manager, Session
from app.router import intelligent_router
from app.models import model_manager
from app.agents import math_agent
from app.rag import rag_manager


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session ID")
    routing_metadata: Dict[str, Any] = Field(..., description="Routing decision information")


class UploadResponse(BaseModel):
    """Response model for upload endpoint."""
    message: str = Field(..., description="Upload status message")
    session_id: str = Field(..., description="Session ID")
    filename: str = Field(..., description="Uploaded filename")
    chunks_stored: int = Field(..., description="Number of text chunks stored")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    message: str


# Initialize FastAPI app
app = FastAPI(
    title="Multi-Model AI Chat System",
    description="Intelligent routing chat system with RAG capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        config.validate()
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)
        os.makedirs(config.VECTOR_STORE_PATH, exist_ok=True)
        print("✅ Application initialized successfully")
    except Exception as e:
        print(f"❌ Startup error: {str(e)}")
        raise


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint for health check."""
    return HealthResponse(
        status="ok",
        message="Multi-Model AI Chat System is running"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="All systems operational"
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint with intelligent routing.
    
    Handles multi-turn conversations with dynamic model selection
    based on query type and context.
    """
    try:
        # Get or create session
        session_id, session = session_manager.get_or_create_session(request.session_id)
        
        # Add user message to history
        session.add_message("user", request.message)
        
        # Route the query
        route_decision, routing_metadata = intelligent_router.route(
            request.message,
            session
        )
        
        # Handle based on route category
        response_text = ""
        
        if route_decision.category == "math":
            # Use math agent with calculator tool
            result = math_agent.solve(request.message)
            response_text = result["answer"]
            
            # Add tool metadata if used
            if result["tool_used"]:
                routing_metadata["calculator_used"] = True
                routing_metadata["calculation"] = result["calculation"]
                routing_metadata["calculation_result"] = result["calculation_result"]
        
        elif route_decision.category == "document":
            # Use RAG pipeline
            if not session.document_uploaded:
                response_text = "I don't have access to any documents yet. Please upload a PDF using the /upload-pdf endpoint."
            else:
                rag_pipeline = rag_manager.get_pipeline(session_id)
                rag_result = rag_pipeline.query(request.message)
                response_text = rag_result["answer"]
                routing_metadata["contexts_used"] = rag_result["num_contexts"]
        
        else:
            # Use appropriate model based on routing decision
            model = model_manager.get_model(route_decision.model_type)
            
            # Get conversation history for context
            history = session.get_conversation_history(limit=5)
            
            # Build messages with history
            messages = []
            for msg in history[:-1]:  # Exclude current message
                messages.append(msg)
            messages.append({"role": "user", "content": request.message})
            
            # Invoke model
            response = model.invoke(messages)
            response_text = response.content
        
        # Add assistant response to history
        session.add_message("assistant", response_text, metadata=routing_metadata)
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            routing_metadata=routing_metadata
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/upload-pdf", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
) -> UploadResponse:
    """
    Upload PDF endpoint for RAG pipeline.
    
    Processes PDF, extracts text, creates embeddings, and stores in vector DB.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Get or create session
        session_id, session = session_manager.get_or_create_session(session_id)
        
        # Save uploaded file
        upload_path = os.path.join(config.UPLOAD_DIR, f"{session_id}_{file.filename}")
        
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process with RAG pipeline
        rag_pipeline = rag_manager.get_pipeline(session_id)
        chunks_stored = rag_pipeline.store_document(upload_path)
        
        # Update session
        session.set_document(file.filename)
        
        return UploadResponse(
            message="PDF uploaded and processed successfully",
            session_id=session_id,
            filename=file.filename,
            chunks_stored=chunks_stored
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and associated data."""
    try:
        deleted = session_manager.delete_session(session_id)
        if deleted:
            # Clean up RAG pipeline
            rag_manager.remove_pipeline(session_id)
            return {"message": "Session deleted successfully", "session_id": session_id}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")


@app.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session."""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "document_uploaded": session.document_uploaded,
            "document_name": session.document_name,
            "message_count": len(session.messages),
            "history": session.get_conversation_history()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )
