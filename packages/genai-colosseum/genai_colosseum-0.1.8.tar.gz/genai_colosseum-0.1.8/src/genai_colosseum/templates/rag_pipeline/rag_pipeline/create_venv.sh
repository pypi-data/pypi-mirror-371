#!/bin/bash
# RAG Pipeline Virtual Environment Setup Script
# This script creates and activates a virtual environment for the RAG pipeline

echo "🚀 RAG Pipeline Virtual Environment Setup"
echo "=========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    echo "   Please install Python 3.8+ and try again"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required, but you have Python $python_version"
    echo "   Please upgrade Python and try again"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ -d "rag_env" ]; then
    echo "⚠️  Virtual environment 'rag_env' already exists"
    read -p "   Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Removing existing virtual environment..."
        rm -rf rag_env
    else
        echo "   Using existing virtual environment"
    fi
fi

if [ ! -d "rag_env" ]; then
    python3 -m venv rag_env
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created successfully"
    else
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source rag_env/bin/activate

if [ $? -eq 0 ]; then
    echo "✅ Virtual environment activated"
    echo "   You should see (rag_env) in your prompt"
    echo ""
    echo "📋 Next steps:"
    echo "1. Install requirements: pip install -r requirements.txt"
    echo "2. Run setup: python setup.py"
    echo "3. Test the system: python test_embeddings.py"
    echo ""
    echo "💡 To deactivate the virtual environment later, run: deactivate"
    echo "💡 To reactivate it, run: source rag_env/bin/activate"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

