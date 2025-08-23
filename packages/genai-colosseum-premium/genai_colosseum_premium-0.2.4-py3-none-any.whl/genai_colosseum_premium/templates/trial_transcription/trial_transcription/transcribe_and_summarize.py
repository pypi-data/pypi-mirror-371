#!/usr/bin/env python3
"""
Standalone utilities to:
1) Transcribe an audio file with OpenAI Whisper (auto language detection).
2) Summarize the transcript with gpt-4.1-nano-2025-04-14 using langchain-openai.

Both functions load .env themselves, so they can be imported and used independently.
"""

from pathlib import Path
from typing import Optional

import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI


def transcribe_with_whisper(audio_path: str, out_dir: Optional[str] = None) -> str:
    """
    Transcribe audio using OpenAI's hosted Whisper.

    - Model: "whisper-1" (auto language detection by default).
      (If you want, you can swap to "gpt-4o-transcribe" for OpenAI's latest transcribe model.)

    Args:
        audio_path: Local path to the audio file (.mp3/.wav/.m4a/.mp4 etc.).
        out_dir: Optional directory to write "<stem>_transcript.txt".

    Returns:
        The transcript as a UTF-8 string.
    """
    # Ensure the API key is available even when used standalone
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY is not set. Put it in a .env or set it in the environment.")

    audio_file = Path(audio_path).expanduser().resolve()
    if not audio_file.exists() or not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    client = OpenAI()

    # Call the audio transcription endpoint (Whisper does language auto-detect)
    with audio_file.open("rb") as f:
        resp = client.audio.transcriptions.create(
            model="whisper-1",   # consider "gpt-4o-transcribe" if you want the newest transcribe model
            file=f,
        )

    transcript_text = getattr(resp, "text", "").strip()
    if not transcript_text:
        # Fallback: stringify the response
        transcript_text = str(resp).strip()

    # Decide output location and write file
    out_dir_path = Path(out_dir).expanduser().resolve() if out_dir else audio_file.parent
    out_dir_path.mkdir(parents=True, exist_ok=True)
    transcript_path = out_dir_path / f"{audio_file.stem}_transcript.txt"
    transcript_path.write_text(transcript_text, encoding="utf-8")

    return transcript_text


def summarize_with_nano(transcript_text: str, max_bullets: int = 8) -> str:
    """
    Summarize transcript text with langchain-openai (ChatOpenAI).

    Args:
        transcript_text: Raw transcript text to summarize.
        max_bullets: Upper bound on bullet points in the markdown summary.

    Returns:
        Markdown summary text.
    """
    # Ensure the API key is available even when used standalone
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY is not set. Put it in a .env or set it in the environment.")

    system_prompt = f"""You are a precise, no-fluff transcript summarizer.
- Return up to {max_bullets} bullet points in Markdown.
- Keep key facts, names, dates, decisions, and action items.
- Merge duplicates; avoid filler; keep wording simple.
- If the transcript is very short, return 2–4 bullets.
"""

    llm = ChatOpenAI(
        model="gpt-4.1-nano-2025-04-14",
        temperature=0,
        max_tokens=None,  # let the API choose based on input size
    )

    messages = [
        ("system", system_prompt),
        ("human", "Summarize the following transcript:\n\n" + transcript_text),
    ]

    ai_msg = llm.invoke(messages)
    return ai_msg.content.strip()


if __name__ == "__main__":
    # >>> EDIT THESE THREE VARIABLES <<<
    AUDIO_PATH = r"C:\Users\SUJAAN BHATTACHARYYA\Documents\Industry Projects\HUMANIZE_TECH_IEM\trial_transcription\sample.wav"
    # OUT_DIR = r".\outputs"      # can be None to save next to the audio file
    MAX_BULLETS = 10

    # 1) Transcribe
    transcript = transcribe_with_whisper(AUDIO_PATH)
    print("\n=== Transcript (first 500 chars) ===")
    print(transcript[:500] + ("..." if len(transcript) > 500 else ""))

    # 2) Summarize
    summary = summarize_with_nano(transcript, max_bullets=MAX_BULLETS)
    print("\n=== Summary ===")
    print(summary)
