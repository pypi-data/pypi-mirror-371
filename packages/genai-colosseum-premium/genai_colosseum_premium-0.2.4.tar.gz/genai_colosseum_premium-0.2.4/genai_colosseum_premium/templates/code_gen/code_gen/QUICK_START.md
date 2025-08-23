# 🚀 Quick Start Guide

Get the LangGraph Code Generation System running in 4 simple steps!

## ⚡ Step 1: Setup Environment

**Option A: Automated Setup (Recommended)**
```bash
# Run the automated setup script
python setup.py
```

**Option B: Manual Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔑 Step 2: Get API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file:
   ```bash
   # Edit .env file
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## 📝 Step 3: Define Components

Edit `component_descriptions.txt` with your components:

```txt
## Component: my-header
- description: A header with navigation menu

## Component: my-content
- description: Main content area with text and images
```

## 🚀 Step 4: Generate Website

```bash
# Run the code generation system
python main.py

# View results
cd dist
python -m http.server 8000
# Open http://localhost:8000 in your browser
```

## 🎯 What You Get

- **Individual Component Files**: `output/components/` (HTML, CSS, JS)
- **Complete Website**: `dist/` folder with all pages
- **Smart Navigation**: Automatic link generation between pages
- **Responsive Design**: Mobile-friendly components

## 🆘 Need Help?

- **Documentation**: See `README.md` for complete details
- **Troubleshooting**: Check the troubleshooting section in README
- **Examples**: Look at the sample components in the setup

---

**That's it! You're ready to generate websites with AI! 🎉**
