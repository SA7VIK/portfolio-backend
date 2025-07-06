from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import feedparser
from fastapi.responses import JSONResponse

from .rag import RAGSystem
from .llm import LLMInterface
from .utils import load_personal_info, validate_question, format_response
from .security import security_guardrails

# Initialize FastAPI app
app = FastAPI(
    title="Portfolio Chatbot API",
    description="A chatbot API that provides information about a person using RAG and LLM",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://sa7vik.in",      # Production
        "https://www.sa7vik.in",  # Production with www
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    context_used: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    rag_ready: bool
    llm_ready: bool
    message: str

# Global instances
rag_system = None
llm_interface = None

@app.on_event("startup")
async def startup_event():
    """Initialize RAG and LLM systems on startup."""
    global rag_system, llm_interface
    
    print("Starting Portfolio Chatbot API...")
    
    # Initialize RAG system
    rag_system = RAGSystem()
    
    # Try to load existing index, otherwise build new one
    if not rag_system.load_index():
        print("Building new RAG index...")
        personal_info = load_personal_info()
        rag_system.build_index(personal_info)
        rag_system.save_index()
    
    # Initialize LLM interface
    # You can change the provider here: "ollama", "openrouter", "huggingface", "groq", "mock"
    llm_provider = os.getenv("LLM_PROVIDER", "mock")
    llm_model = os.getenv("LLM_MODEL", "llama3-8b-8192")
    
    llm_interface = LLMInterface(provider=llm_provider, model_name=llm_model)
    
    print(f"Initialized with LLM provider: {llm_provider}, model: {llm_model}")

@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Portfolio Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global rag_system, llm_interface
    
    rag_ready = rag_system is not None and rag_system.index is not None
    llm_ready = llm_interface is not None and llm_interface.test_connection()
    
    status = "healthy" if rag_ready and llm_ready else "unhealthy"
    message = "All systems operational" if rag_ready and llm_ready else "Some systems are not ready"
    
    return HealthResponse(
        status=status,
        rag_ready=rag_ready,
        llm_ready=llm_ready,
        message=message
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """Main chat endpoint with security guardrails."""
    global rag_system, llm_interface
    
    if not rag_system or not llm_interface:
        raise HTTPException(status_code=503, detail="Systems not initialized")
    
    # Get client IP
    client_ip = http_request.client.host
    user_agent = http_request.headers.get("user-agent", "")
    
    # Security validation
    is_valid, validation_msg, violations = security_guardrails.validate_request(
        message=request.message,
        conversation_history=request.conversation_history,
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    if not is_valid:
        return ChatResponse(
            response="I'm sorry, but I cannot process that request. Please ask a valid question about Satvik.",
            error=validation_msg
        )
    
    # Validate the question format
    if not validate_question(request.message):
        return ChatResponse(
            response="Please ask a valid question about Satvik (at least 3 characters).",
            error="Invalid question format"
        )
    
    try:
        # Get relevant context using RAG
        context = rag_system.get_context_for_query(request.message)
        
        # Generate response using LLM
        response = llm_interface.generate_response(request.message, context)
        
        # Format the response
        formatted_response = format_response(response)
        
        return ChatResponse(
            response=formatted_response,
            context_used=context if context != "I don't have specific information about that." else None
        )
        
    except Exception as e:
        import traceback
        print(f"Error in chat endpoint: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return ChatResponse(
            response="Sorry, I encountered an error while processing your question. Please try again.",
            error=str(e)
        )

@app.post("/rebuild-index")
async def rebuild_index():
    """Rebuild the RAG index from personal info."""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        personal_info = load_personal_info()
        rag_system.build_index(personal_info)
        rag_system.save_index()
        
        return {"message": "RAG index rebuilt successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rebuilding index: {str(e)}")

@app.get("/personal-info")
async def get_personal_info():
    """Get the current personal information."""
    try:
        personal_info = load_personal_info()
        return {"personal_info": personal_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading personal info: {str(e)}")

@app.get("/medium-blogs")
async def get_medium_blogs():
    """Fetch and parse Medium RSS feed for @sa7vik and return blog post data as JSON."""
    rss_url = "https://medium.com/feed/@sa7vik"
    try:
        feed = feedparser.parse(rss_url)
        blogs = []
        for entry in feed.entries:
            # Try to extract the image from the content or media:content
            image_url = None
            if 'media_content' in entry and entry.media_content:
                image_url = entry.media_content[0].get('url')
            elif 'content' in entry and entry.content:
                import re
                img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.content[0].value)
                if img_match:
                    image_url = img_match.group(1)
            blogs.append({
                "title": entry.title,
                "description": entry.summary,
                "imageUrl": image_url,
                "publishDate": entry.published,
                "mediumUrl": entry.link,
                "tags": [tag.term for tag in entry.tags] if 'tags' in entry else [],
                "readTime": entry.get('reading_time', "")
            })
        return JSONResponse(content=blogs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Medium blogs: {str(e)}")

@app.get("/security/stats")
async def get_security_stats():
    """Get security statistics (admin only in production)."""
    return security_guardrails.get_security_stats()

@app.post("/security/reset/{ip}")
async def reset_ip_block(ip: str):
    """Reset IP block (admin only in production)."""
    if ip in security_guardrails.blocked_ips:
        security_guardrails.blocked_ips.remove(ip)
        security_guardrails.ip_violation_count[ip] = 0
        return {"message": f"IP {ip} unblocked successfully"}
    return {"message": f"IP {ip} was not blocked"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
