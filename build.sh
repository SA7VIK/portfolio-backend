#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install setuptools wheel

# Install minimal requirements (no Rust dependencies)
pip install -r requirements_minimal_render.txt

# Create necessary directories
mkdir -p rag_index 