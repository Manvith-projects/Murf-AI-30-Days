#!/bin/bash

# 🚀 Voice AI Agent Setup Script
# This script helps you get started with the Voice AI Agent project

echo "🎤 Setting up Voice AI Agent..."
echo "=================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $(python --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv flask_env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source flask_env/Scripts/activate
else
    source flask_env/bin/activate
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy environment template
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your API keys"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run: python app.py"
echo "3. Open: http://127.0.0.1:5000"
echo ""
echo "📚 For detailed instructions, see README.md"
