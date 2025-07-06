#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install setuptools wheel
pip install -r requirements.txt

# Create necessary directories
mkdir -p rag_index 