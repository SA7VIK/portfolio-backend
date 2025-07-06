#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install setuptools wheel

# Install simplified requirements (no FAISS)
pip install -r requirements_simple.txt

# Create necessary directories
mkdir -p rag_index 