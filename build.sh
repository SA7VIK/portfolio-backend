#!/bin/bash

echo "🔧 Building Portfolio Backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies with no binary wheels (force pure Python)
echo "📚 Installing dependencies..."
pip install --no-binary=all -r requirements.txt

echo "✅ Build completed successfully!"

# Create necessary directories
mkdir -p data 