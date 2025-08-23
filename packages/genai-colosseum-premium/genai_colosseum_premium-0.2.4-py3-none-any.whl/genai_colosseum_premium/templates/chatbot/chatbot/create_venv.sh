#!/bin/bash
# Chatbot Virtual Environment Setup
# Simple script to create and activate virtual environment

echo "🤖 Chatbot Virtual Environment Setup"
echo "===================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ -d "chatbot_env" ]; then
    echo "⚠️  Virtual environment 'chatbot_env' already exists"
    read -p "   Recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf chatbot_env
    else
        echo "   Using existing environment"
    fi
fi

if [ ! -d "chatbot_env" ]; then
    python3 -m venv chatbot_env
    echo "✅ Virtual environment created"
fi

# Activate
echo ""
echo "🔌 Activating virtual environment..."
source chatbot_env/bin/activate

echo "✅ Virtual environment activated!"
echo "   You should see (chatbot_env) in your prompt"
echo ""
echo "📋 Next steps:"
echo "1. Install requirements: pip install -r requirements.txt"
echo "2. Run setup: python setup.py"
echo "3. Start chatbot: streamlit run app.py"
echo ""
echo "💡 To deactivate: deactivate"
echo "💡 To reactivate: source chatbot_env/bin/activate"
