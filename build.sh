#!/bin/bash

echo "🔧 Building Portfolio Backend..."

# Upgrade pip
pip install --upgrade pip

# Install dependencies with no binary wheels (force pure Python)
pip install --no-binary=all -r requirements.txt

echo "✅ Build completed successfully!"

# Create necessary directories
mkdir -p data 