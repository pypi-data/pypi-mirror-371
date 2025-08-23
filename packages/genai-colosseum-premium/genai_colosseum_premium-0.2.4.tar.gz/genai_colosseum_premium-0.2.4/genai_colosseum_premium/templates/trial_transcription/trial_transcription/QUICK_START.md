# 🚀 Quick Start Guide

Get the Trial Transcription System running in 4 simple steps!

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

## 🔑 Step 2: Get OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key to your `.env` file:
   ```bash
   # Edit .env file
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

## 🎵 Step 3: Test with Sample Audio

```bash
# Run the transcription system
python transcribe_and_summarize.py
```

This will:
- Transcribe the sample.wav file
- Generate a summary
- Save both transcript and summary files

## 📝 Step 4: Use Your Own Audio

Edit the `AUDIO_PATH` variable in `transcribe_and_summarize.py`:

```python
AUDIO_PATH = "path/to/your/audio/file.wav"
```

## 🎯 What You Get

- **Audio Transcription**: Convert audio to text using OpenAI Whisper
- **Smart Summarization**: Generate concise summaries using GPT-4.1-nano
- **Multiple Formats**: Supports .wav, .mp3, .m4a, .mp4, and more
- **Auto Language Detection**: Works with multiple languages

## 🆘 Need Help?

- **Documentation**: See `README.md` for complete details
- **Troubleshooting**: Check the troubleshooting section in README
- **Examples**: Look at the sample files included

## 📁 File Structure

```
trial_transcription/
├── transcribe_and_summarize.py  # Main script
├── requirements.txt             # Dependencies
├── setup.py                     # Automated setup
├── create_venv.sh               # Virtual environment script
├── env_template.txt             # Environment template
├── sample.wav                   # Sample audio file
└── sample_transcript.txt        # Sample output
```

---

**That's it! You're ready to transcribe audio! 🎵**
