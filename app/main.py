import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json

# Try to import feedparser, but make it optional
try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    print("Warning: feedparser not available. Blog functionality will be disabled.")

# Import LLM interface
from .llm import LLMInterface

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    global llm_interface
    
    # Startup
    print("Starting Portfolio Chatbot API...")
    
    # Initialize LLM interface
    # You can change the provider here: "ollama", "openrouter", "huggingface", "groq", "mock"
    llm_provider = os.getenv("LLM_PROVIDER", "mock")
    llm_model = os.getenv("LLM_MODEL", "llama3-8b-8192")
    
    llm_interface = LLMInterface(provider=llm_provider, model_name=llm_model)
    
    print(f"Initialized with LLM provider: {llm_provider}, model: {llm_model}")
    
    yield
    
    # Shutdown
    print("Shutting down Portfolio Chatbot API...")

# Initialize FastAPI app
app = FastAPI(
    title="Portfolio Chatbot API",
    description="A chatbot API that provides information about Satvik using LLM",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://sa7vik.in",      # Production
        "https://www.sa7vik.in",  # Production with www
        "https://portfolio-frontend-two-phi.vercel.app",  # Vercel preview
        "https://portfolio-website-sa7vik.vercel.app",   # Vercel production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Satvik's information as context
SATVIK_CONTEXT = """
## About Satvik
Satvik is an AI Engineer & Researcher with expertise in high-performance computing, quantum machine learning, and RAG systems. He loves building intelligent systems that can actually think.

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

## Personal Interests
- Gym and fitness
- Cooking and experimenting with recipes
- Anime and Japanese culture
- Spirituality and meditation

## Contact Information
- Email: Available through portfolio
- GitHub: @SA7VIK
- LinkedIn: Satvik Singh
"""

# Global LLM interface
llm_interface = None

def validate_question(message: str) -> bool:
    """Validate if the question is appropriate."""
    if len(message.strip()) < 3:
        return False
    return True



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
    global llm_interface
    
    llm_ready = llm_interface is not None and llm_interface.test_connection()
    
    status = "healthy" if llm_ready else "unhealthy"
    message = "All systems operational" if llm_ready else "LLM system not ready"
    
    return {
        "status": status,
        "rag_ready": True,
        "llm_ready": llm_ready,
        "message": message
    }

@app.post("/chat")
async def chat(request: Request):
    """Main chat endpoint."""
    global llm_interface
    
    if not llm_interface:
        raise HTTPException(status_code=503, detail="LLM system not initialized")
    
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
        
        # Generate response using LLM with context
        response = llm_interface.generate_response(message, SATVIK_CONTEXT)
        
        return {
            "response": response,
            "context_used": "Direct context system"
        }
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return {
            "response": "Sorry, I encountered an error while processing your question. Please try again.",
            "error": str(e)
        }

@app.get("/personal-info")
async def get_personal_info():
    """Get Satvik's personal information."""
    return {"personal_info": SATVIK_CONTEXT}

@app.get("/medium-blogs")
async def get_medium_blogs():
    """Fetch and parse Medium RSS feed for @sa7vik and return blog post data as JSON."""
    if not FEEDPARSER_AVAILABLE:
        return JSONResponse(content=[], status_code=503, headers={
            "X-Warning": "Blog functionality disabled - feedparser not available"
        })
    
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
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 