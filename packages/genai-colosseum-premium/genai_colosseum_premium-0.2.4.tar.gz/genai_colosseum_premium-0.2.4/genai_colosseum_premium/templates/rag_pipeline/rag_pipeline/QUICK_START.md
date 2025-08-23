# 🚀 RAG Pipeline - Quick Start Guide

## ⚡ Get Started in 4 Steps

### 1. 🐍 Create Virtual Environment (Recommended)

#### Option A: Automatic Setup (Linux/Mac)
```bash
# Navigate to the rag_pipeline folder
cd langchain/rag_pipeline

# Run the automatic setup script
./create_venv.sh
```

#### Option B: Manual Setup
```bash
# Navigate to the rag_pipeline folder
cd langchain/rag_pipeline

# Create virtual environment
python -m venv rag_env

# Activate virtual environment
# On Linux/Mac:
source rag_env/bin/activate
# On Windows:
# rag_env\Scripts\activate
```

### 2. 🏃‍♂️ Run Setup (Automatic)
```bash
python setup.py
```

### 2. 🔑 Add Your API Key
Edit the `.env` file and add your Groq API key: ## Great if you have an empty pocket
```bash
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### 3. 🧪 Test & Use
```bash
# Test core functionality
python test_embeddings.py

# Run full RAG system
python rag_implementation.py
```

## 🎯 What You Get

- ✅ **Complete RAG System** - Ready to use
- ✅ **HuggingFace Embeddings** - High-quality, free
- ✅ **Multiple Document Types** - TXT, PDF, Web URLs
- ✅ **Vector Stores** - FAISS & Chroma
- ✅ **LLM Integration** - Groq, OpenAI, Anthropic
- ✅ **LangChain Tracking** - Monitor your RAG system

## 🔗 Get API Keys

- **Groq (Recommended)**: https://console.groq.com/ (Free tier available)
- **LangSmith**: https://smith.langchain.com/ (Free tracking)

## 📚 Full Documentation

See `README.md` for complete API reference and advanced usage.

---

**Happy RAG-ing! 🚀**
