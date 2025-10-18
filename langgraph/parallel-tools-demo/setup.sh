#!/bin/bash

# Setup script for parallel-tools-demo

echo "🚀 Setting up Parallel Tools Demo..."
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the demo:"
echo "  1. source venv/bin/activate"
echo "  2. python main.py"
echo ""
echo "To deactivate the virtual environment:"
echo "  deactivate"
echo ""

