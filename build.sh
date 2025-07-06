#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install setuptools wheel

# Try to install faiss-cpu-noavx2 first, fallback to scikit-learn if it fails
if pip install faiss-cpu-noavx2==1.7.4; then
    echo "Successfully installed faiss-cpu-noavx2"
else
    echo "faiss-cpu-noavx2 failed, trying alternative approach..."
    # Install scikit-learn as alternative for vector operations
    pip install scikit-learn
    # Create a simple fallback for FAISS
    echo "Using scikit-learn as FAISS alternative"
fi

# Install remaining requirements
pip install -r requirements.txt

# Create necessary directories
mkdir -p rag_index 