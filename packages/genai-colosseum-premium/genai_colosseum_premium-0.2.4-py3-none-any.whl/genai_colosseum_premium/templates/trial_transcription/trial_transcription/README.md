# 🎵 Trial Transcription System

A powerful audio transcription and summarization system using OpenAI's Whisper and GPT-4.1-nano models. Transcribe audio files and automatically generate concise summaries.

## ✨ Features

- **Audio Transcription**: Convert audio files to text using OpenAI Whisper
- **Auto Language Detection**: Supports multiple languages automatically
- **Smart Summarization**: Generate concise summaries using GPT-4.1-nano
- **Multiple Audio Formats**: Supports .wav, .mp3, .m4a, .mp4, and more
- **Flexible Output**: Save transcripts and summaries to custom directories
- **Easy Integration**: Simple API for standalone use or integration

## 🏗️ Architecture

The system consists of two main components:

1. **Transcription Engine**: Uses OpenAI Whisper for high-quality audio-to-text conversion
2. **Summarization Engine**: Uses GPT-4.1-nano for intelligent text summarization

## 📁 Project Structure

```
trial_transcription/
├── transcribe_and_summarize.py  # Main transcription and summarization script
├── requirements.txt             # Python dependencies
├── README.md                   # This file
├── setup.py                    # Automated setup script
├── create_venv.sh              # Virtual environment script
├── env_template.txt            # Environment variables template
├── QUICK_START.md              # Quick start guide
├── sample.wav                  # Sample audio file for testing
├── sample_transcript.txt       # Sample transcript output
└── image.png                   # Project documentation image
```

## 🚀 Quick Start

### 1. Setup Environment

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

### 2. Configure API Key

Create a `.env` file:
```bash
cp env_template.txt .env
# Edit .env with your actual OpenAI API key
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### 3. Run Transcription

```bash
# Basic usage
python transcribe_and_summarize.py

# Or import and use in your code
from transcribe_and_summarize import transcribe_with_whisper, summarize_with_nano
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with your configuration:

```env
# Required: Your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Additional configuration
DEBUG=false
LOG_LEVEL=INFO
```

### Audio File Requirements

- **Supported Formats**: .wav, .mp3, .m4a, .mp4, .flac, .ogg
- **File Size**: Up to 25MB (OpenAI Whisper limit)
- **Duration**: No strict limit, but longer files take more time
- **Quality**: Higher quality audio produces better results

## 📖 Usage Examples

### Basic Transcription

```python
from transcribe_and_summarize import transcribe_with_whisper

# Transcribe an audio file
transcript = transcribe_with_whisper("path/to/audio.wav")
print(transcript)
```

### Transcription with Custom Output

```python
# Save transcript to specific directory
transcript = transcribe_with_whisper(
    "path/to/audio.wav", 
    out_dir="./outputs"
)
```

### Summarization

```python
from transcribe_and_summarize import summarize_with_nano

# Summarize transcript
summary = summarize_with_nano(transcript, max_bullets=8)
print(summary)
```

### Complete Workflow

```python
# Transcribe and summarize in one go
transcript = transcribe_with_whisper("meeting.wav")
summary = summarize_with_nano(transcript, max_bullets=10)

print("Transcript:", transcript)
print("Summary:", summary)
```

## 🎯 API Reference

### `transcribe_with_whisper(audio_path, out_dir=None)`

Transcribe audio using OpenAI Whisper.

**Parameters:**
- `audio_path` (str): Path to audio file
- `out_dir` (str, optional): Output directory for transcript file

**Returns:**
- `str`: Transcribed text

**Raises:**
- `EnvironmentError`: If OPENAI_API_KEY is not set
- `FileNotFoundError`: If audio file doesn't exist

### `summarize_with_nano(transcript_text, max_bullets=8)`

Summarize transcript using GPT-4.1-nano.

**Parameters:**
- `transcript_text` (str): Text to summarize
- `max_bullets` (int): Maximum number of bullet points

**Returns:**
- `str`: Markdown-formatted summary

## 🔍 Supported Languages

The system automatically detects and transcribes audio in multiple languages:

- **English** (primary)
- **Spanish, French, German, Italian**
- **Chinese, Japanese, Korean**
- **Arabic, Hindi, Russian**
- **And many more...**

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   EnvironmentError: OPENAI_API_KEY is not set
   ```
   **Solution**: Check your `.env` file and ensure the API key is correct.

2. **Audio File Not Found**
   ```
   FileNotFoundError: Audio file not found
   ```
   **Solution**: Verify the audio file path is correct and the file exists.

3. **Large File Error**
   ```
   File size exceeds 25MB limit
   ```
   **Solution**: Compress or split the audio file.

4. **Network Issues**
   ```
   Connection error during transcription
   ```
   **Solution**: Check your internet connection and OpenAI API status.

### Debug Mode

Enable detailed logging by setting environment variables:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🚀 Advanced Usage

### Custom Models

You can modify the model in `transcribe_and_summarize.py`:

```python
# For transcription
resp = client.audio.transcriptions.create(
    model="gpt-4o-transcribe",  # Latest model
    file=f,
)

# For summarization
llm = ChatOpenAI(
    model="gpt-4o-mini",  # Different model
    temperature=0.1,
)
```

### Batch Processing

```python
import os
from pathlib import Path

# Process multiple audio files
audio_dir = Path("./audio_files")
for audio_file in audio_dir.glob("*.wav"):
    transcript = transcribe_with_whisper(str(audio_file))
    summary = summarize_with_nano(transcript)
    
    # Save results
    output_file = audio_file.parent / f"{audio_file.stem}_summary.txt"
    output_file.write_text(summary)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Verify your API key configuration
4. Ensure all dependencies are installed
5. Check OpenAI API status

---

**Happy transcribing! 🎵**
