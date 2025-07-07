#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install setuptools wheel

# Install clean requirements (no ML dependencies)
pip install -r requirements_clean.txt

# Create necessary directories
mkdir -p data 