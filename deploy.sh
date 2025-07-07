#!/bin/bash

echo "🚀 Deploying Portfolio Backend..."

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Test the application
echo "🧪 Testing the application..."
python -c "
import uvicorn
from app.main import app
print('✅ Application imports successfully')
"

# Start the server for testing
echo "🌐 Starting server for testing..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait a moment for server to start
sleep 3

# Test the health endpoint
echo "🏥 Testing health endpoint..."
curl -s http://localhost:8000/health | python -m json.tool

# Test the chat endpoint
echo "💬 Testing chat endpoint..."
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Who is Satvik?"}' \
  | python -m json.tool

# Stop the test server
kill $SERVER_PID

echo "✅ Backend is ready for deployment!"
echo ""
echo "📋 Next steps:"
echo "1. Push your code to GitHub"
echo "2. Connect your repository to Render"
echo "3. Set environment variables in Render dashboard:"
echo "   - LLM_PROVIDER (mock, groq, openrouter, etc.)"
echo "   - LLM_MODEL (llama3-8b-8192, etc.)"
echo "   - GROQ_API_KEY (if using Groq)"
echo "   - OPENROUTER_API_KEY (if using OpenRouter)"
echo ""
echo "🌐 Your backend will be available at: https://your-app-name.onrender.com" 