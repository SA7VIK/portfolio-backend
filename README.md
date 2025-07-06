# Portfolio Chatbot Backend

A FastAPI-based backend for a portfolio chatbot that uses RAG (Retrieval-Augmented Generation) and LLM to provide information about a person.

## Features

- **FastAPI**: Modern, fast web framework
- **RAG System**: Uses FAISS and Sentence Transformers for semantic search
- **Multiple LLM Providers**: Support for Ollama (local), OpenRouter (cloud), and Hugging Face
- **CORS Support**: Ready for frontend integration
- **Health Checks**: System status monitoring
- **Auto-reload**: Development-friendly

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure LLM Provider

Choose one of the following LLM providers:

#### Option A: Ollama (Recommended - Local, Free)

1. Install Ollama: https://ollama.ai/
2. Pull a model:
   ```bash
   ollama pull llama2
   # or
   ollama pull mistral
   ```
3. Set environment variables:
   ```bash
   export LLM_PROVIDER=ollama
   export LLM_MODEL=llama2
   ```

#### Option B: OpenRouter (Cloud, Free Tier)

1. Get API key from: https://openrouter.ai/
2. Set environment variables:
   ```bash
   export OPENROUTER_API_KEY=your_api_key_here
   export LLM_PROVIDER=openrouter
   export LLM_MODEL=openai/gpt-3.5-turbo
   ```

#### Option C: Hugging Face (Local, Free)

1. Install additional dependencies:
   ```bash
   pip install transformers torch
   ```
2. Set environment variables:
   ```bash
   export LLM_PROVIDER=huggingface
   export LLM_MODEL=gpt2
   ```

### 3. Customize Personal Information

Edit `app/data/personal_info.md` with your own information. The system will automatically build the RAG index from this file.

### 4. Run the Backend

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: http://localhost:8000

## API Endpoints

### Health Check
```bash
GET /health
```
Returns system status and readiness.

### Chat
```bash
POST /chat
Content-Type: application/json

{
  "message": "What are your skills?",
  "conversation_history": []
}
```

### Rebuild Index
```bash
POST /rebuild-index
```
Rebuilds the RAG index from personal info (useful after updating personal_info.md).

### Get Personal Info
```bash
GET /personal-info
```
Returns the current personal information.

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── rag.py               # RAG system implementation
│   ├── llm.py               # LLM interface
│   ├── utils.py             # Utility functions
│   └── data/
│       ├── personal_info.md # Your personal information
│       └── rag_index.pkl    # Generated RAG index (auto-created)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Environment Variables

- `LLM_PROVIDER`: "ollama", "openrouter", or "huggingface"
- `LLM_MODEL`: Model name for the selected provider
- `OPENROUTER_API_KEY`: API key for OpenRouter (if using OpenRouter)

## Troubleshooting

### Ollama Connection Issues
- Make sure Ollama is running: `ollama serve`
- Check if model is downloaded: `ollama list`
- Test connection: `curl http://localhost:11434/api/tags`

### RAG Index Issues
- Delete `app/data/rag_index.pkl` and restart to rebuild
- Check if `personal_info.md` exists and has content

### Memory Issues
- Use smaller models (e.g., `llama2:7b` instead of `llama2:70b`)
- Reduce chunk size in `utils.py`

## Development

### Adding New LLM Providers

1. Add provider logic in `llm.py`
2. Update the `generate_response` method
3. Add provider to environment variable options

### Customizing RAG

- Modify chunk size in `utils.py`
- Change embedding model in `rag.py`
- Adjust similarity threshold in `get_context_for_query`

## Production Deployment

For production:
1. Set specific CORS origins instead of "*"
2. Use environment variables for configuration
3. Add proper logging
4. Consider using a production ASGI server like Gunicorn
5. Add rate limiting and authentication if needed
