#!/bin/bash
set -e

echo "Installing Python dependencies..."
pip install --break-system-packages -r requirements.txt

echo "Pre-downloading EasyOCR models..."
python init_model.py

echo "Build complete."
