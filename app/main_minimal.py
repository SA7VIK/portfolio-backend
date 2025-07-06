import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import feedparser
import json

# Import basic RAG system
from .rag_basic import RAGSystemBasic as RAGSystem

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

# Global instances
rag_system = None

def load_personal_info():
    """Load personal information from file."""
    try:
        with open("personal_info.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
# Satvik - AI Engineer & Researcher

## About Me
I'm an AI Engineer & Researcher with expertise in high-performance computing, quantum machine learning, and RAG systems. I love building intelligent systems that can actually think.

## Technical Skills
- **High-Performance Computing**: CUDA, MPI, distributed systems
- **Quantum Machine Learning**: Qiskit, quantum algorithms
- **RAG Systems**: Vector databases, embeddings, retrieval
- **Agent-to-Agent MCP**: Multi-agent systems, coordination
- **Languages**: Python, C++, Rust, JavaScript
- **Frameworks**: PyTorch, TensorFlow, FastAPI, React

## Projects
- **MoneyInsight**: AI-powered financial analysis platform
- **DermCare Solutions**: Medical image analysis for dermatology
- **Email Marketing Agent**: Automated email campaign optimization

## Experience
- AI Research at leading institutions
- Full-stack development experience
- Published research in quantum ML
- Open source contributions

## Interests
- Gym and fitness
- Cooking and experimenting with recipes
- Anime and Japanese culture
- Spirituality and meditation
"""

def validate_question(message: str) -> bool:
    """Validate if the question is appropriate."""
    if len(message.strip()) < 3:
        return False
    return True

def format_response(response: str) -> str:
    """Format the response for better presentation."""
    return response.strip()

@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup."""
    global rag_system
    
    print("Starting Portfolio Chatbot API...")
    
    # Initialize RAG system
    rag_system = RAGSystem()
    
    # Try to load existing index, otherwise build new one
    if not rag_system.load_index():
        print("Building new RAG index...")
        personal_info = load_personal_info()
        rag_system.build_index(personal_info)
        rag_system.save_index()
    
    print("RAG system initialized successfully")

@app.get("/")
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

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global rag_system
    
    rag_ready = rag_system is not None
    
    status = "healthy" if rag_ready else "unhealthy"
    message = "All systems operational" if rag_ready else "RAG system not ready"
    
    return {
        "status": status,
        "rag_ready": rag_ready,
        "llm_ready": True,  # Mock LLM for now
        "message": message
    }

@app.post("/chat")
async def chat(request: Request):
    """Main chat endpoint."""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Parse request body
        body = await request.json()
        message = body.get("message", "")
        conversation_history = body.get("conversation_history", [])
        
        # Validate the question format
        if not validate_question(message):
            return {
                "response": "Please ask a valid question about Satvik (at least 3 characters).",
                "error": "Invalid question format"
            }
        
        # Get relevant context using RAG
        context = rag_system.get_context_for_query(message)
        
        # Generate simple response (mock LLM for now)
        if context and context != "I don't have specific information about that.":
            response = f"Based on my knowledge about Satvik: {context}\n\nI'm Satvik's AI assistant. I can help you learn more about my background, projects, and expertise. What would you like to know?"
        else:
            response = "I'm Satvik's AI assistant. I can help you learn about my background, projects, and expertise. What would you like to know?"
        
        # Format the response
        formatted_response = format_response(response)
        
        return {
            "response": formatted_response,
            "context_used": context if context != "I don't have specific information about that." else None
        }
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return {
            "response": "Sorry, I encountered an error while processing your question. Please try again.",
            "error": str(e)
        }

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

if __name__ == "__main__":
    uvicorn.run(
        "app.main_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 