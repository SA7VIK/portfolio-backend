#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install setuptools wheel

# Install basic requirements (no ML dependencies)
pip install -r requirements_basic.txt

# Create necessary directories
mkdir -p rag_index 