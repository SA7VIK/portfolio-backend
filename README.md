# Portfolio Backend API

A FastAPI backend for Satvik's portfolio website with an intelligent chatbot powered by LLMs.

## Features

- 🤖 **Intelligent Chatbot**: Powered by various LLM providers (Groq, OpenRouter, Ollama, etc.)
- 📝 **Blog Integration**: Fetches Medium blog posts via RSS
- 🏥 **Health Monitoring**: Comprehensive health checks
- 🌐 **CORS Support**: Configured for frontend integration
- 🔧 **Flexible LLM**: Easy to switch between different LLM providers

## LLM Providers

The backend supports multiple LLM providers:

### 1. Mock Mode (Default)
- **Provider**: `mock`
- **Use Case**: Testing and development
- **Setup**: No API keys required
- **Response**: Pre-defined responses with context

### 2. Groq (Recommended for Production)
- **Provider**: `groq`
- **Models**: `llama3-8b-8192`, `mixtral-8x7b-32768`
- **Setup**: Set `GROQ_API_KEY` environment variable
- **Cost**: Very affordable, fast responses

### 3. OpenRouter
- **Provider**: `openrouter`
- **Models**: Various models from different providers
- **Setup**: Set `OPENROUTER_API_KEY` environment variable
- **Cost**: Pay-per-use

### 4. Ollama (Local)
- **Provider**: `ollama`
- **Models**: Any model installed locally
- **Setup**: Install Ollama and run locally
- **Cost**: Free (local processing)

## Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables** (optional):
   ```bash
   export LLM_PROVIDER=mock  # or groq, openrouter, ollama
   export LLM_MODEL=llama3-8b-8192
   export GROQ_API_KEY=your_groq_api_key  # if using Groq
   ```

3. **Run the server**:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Test the API**:
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Chat with the bot
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Tell me about Satvik"}'
   ```

### Deployment

#### Using the Deployment Script

```bash
./deploy.sh
```

This script will:
- Install dependencies
- Test the application
- Verify endpoints work
- Provide deployment instructions

#### Manual Deployment

1. **Push to GitHub**
2. **Connect to Render/Railway/Heroku**
3. **Set environment variables**:
   - `LLM_PROVIDER`: Choose your provider
   - `LLM_MODEL`: Model name
   - `GROQ_API_KEY`: If using Groq
   - `OPENROUTER_API_KEY`: If using OpenRouter

## API Endpoints

### `GET /`
Root endpoint with API information.

### `GET /health`
Health check endpoint.
```json
{
  "status": "healthy",
  "rag_ready": true,
  "llm_ready": true,
  "message": "All systems operational"
}
```

### `POST /chat`
Main chatbot endpoint.
```json
{
  "message": "Tell me about Satvik's skills",
  "conversation_history": []
}
```

Response:
```json
{
  "response": "Based on the information provided, Satvik has expertise in...",
  "context_used": "Direct context system"
}
```

### `GET /personal-info`
Get Satvik's information context.

### `GET /medium-blogs`
Fetch blog posts from Medium RSS feed.

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LLM_PROVIDER` | LLM provider to use | `mock` | No |
| `LLM_MODEL` | Model name for the provider | `llama3-8b-8192` | No |
| `GROQ_API_KEY` | API key for Groq | - | Yes (if using Groq) |
| `OPENROUTER_API_KEY` | API key for OpenRouter | - | Yes (if using OpenRouter) |

## Context System

The chatbot uses a comprehensive context about Satvik including:
- Personal information
- Technical skills
- Projects
- Experience
- Interests
- Contact information

This context is provided directly to the LLM, ensuring accurate and relevant responses.

## Troubleshooting

### Common Issues

1. **LLM not responding**:
   - Check API keys are set correctly
   - Verify provider and model names
   - Test with mock mode first

2. **Deployment failures**:
   - Ensure all dependencies are in `requirements.txt`
   - Check environment variables are set
   - Verify the start command in deployment config

3. **CORS errors**:
   - Update `allow_origins` in `main.py` with your frontend URL

### Testing

Use the deployment script to test everything:
```bash
./deploy.sh
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
