#!/bin/bash

echo "🚀 Activating Portfolio Backend Environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Creating one..."
    python -m venv venv
    echo "📚 Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "🔌 Activating existing virtual environment..."
    source venv/bin/activate
fi

echo "✅ Environment activated! You can now run:"
echo "   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "   Or test with:"
echo "   python test_setup.py" 