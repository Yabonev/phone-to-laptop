#!/usr/bin/env python3
"""Test Bulgarian transcription with Whisper"""

import logging
from pathlib import Path

import whisper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_bulgarian_transcription():
    """Test if Whisper can correctly transcribe Bulgarian"""

    # Check if there's an audio file to test with
    audio_dir = Path("./audio")
    audio_files = list(audio_dir.glob("*.ogg"))

    if not audio_files:
        logger.error("No audio files found in ./audio directory")
        return

    audio_file = audio_files[0]
    logger.info(f"Testing with audio file: {audio_file}")

    # Load Whisper model
    logger.info("Loading Whisper model (large)...")
    model = whisper.load_model("large")

    # Test 1: Auto-detect language
    logger.info("\n=== Test 1: Auto-detect ===")
    result_auto = model.transcribe(str(audio_file), fp16=False)
    logger.info(f"Detected language: {result_auto.get('language', 'unknown')}")
    logger.info(f"Transcription: {result_auto['text']}")

    # Test 2: Force Bulgarian language
    logger.info("\n=== Test 2: Force Bulgarian ===")
    result_bg = model.transcribe(str(audio_file), language="bg", fp16=False)
    logger.info(f"Transcription (forced BG): {result_bg['text']}")

    # Test 3: Translate to English
    logger.info("\n=== Test 3: Translate to English ===")
    result_translate = model.transcribe(
        str(audio_file), language="bg", task="translate", fp16=False
    )
    logger.info(f"English translation: {result_translate['text']}")

    # Compare results
    logger.info("\n=== Analysis ===")
    if result_auto["text"] != result_bg["text"]:
        logger.warning("Auto-detect and forced Bulgarian give different results!")
        logger.info(f"Auto: {result_auto['text']}")
        logger.info(f"BG:   {result_bg['text']}")
    else:
        logger.info("Auto-detect and forced Bulgarian match ✓")


if __name__ == "__main__":
    test_bulgarian_transcription()
