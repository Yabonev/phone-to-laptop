"""
Transcription service using Whisper - Single Responsibility
"""
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import whisper
import logging


class TranscriptionService:
    """Handles audio transcription using Whisper"""
    
    def __init__(self, model_name: str = "large", audio_dir: Path = Path("./audio")):
        self.model_name = model_name
        self.audio_dir = audio_dir
        self.audio_dir.mkdir(exist_ok=True)
        self.model = None
        self.logger = logging.getLogger(__name__)
    
    def _load_model(self):
        """Lazy load Whisper model"""
        if self.model is None:
            self.logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            self.logger.info("Whisper model loaded successfully")
    
    async def transcribe_audio(self, audio_path: Path, language: str = "en") -> Tuple[str, str]:
        """
        Transcribe audio file
        Returns: (transcribed_text, language_used)
        """
        self._load_model()
        
        self.logger.info(f"Transcribing audio: {audio_path} (language: {language})")
        
        # Set transcription parameters
        params = {
            "fp16": False,  # Use FP32 for CPU
            "language": language  # Always use specified language
        }
        
        # Transcribe with specified language
        result = self.model.transcribe(str(audio_path), **params)
        transcribed_text = result["text"].strip()
        
        self.logger.info(f"Transcription complete. Language: {language}")
        
        return transcribed_text, language
    
    async def translate_to_english(self, audio_path: Path, source_language: str) -> str:
        """Translate audio to English"""
        self._load_model()
        
        self.logger.info(f"Translating {source_language} audio to English")
        
        result = self.model.transcribe(
            str(audio_path),
            language=source_language,
            task="translate",  # Translate to English
            fp16=False
        )
        
        translated_text = result["text"].strip()
        self.logger.info("Translation complete")
        
        return translated_text
    
    def create_temp_audio_file(self, suffix: str = '.ogg') -> Path:
        """Create a temporary audio file"""
        tmp_file = tempfile.NamedTemporaryFile(
            suffix=suffix,
            dir=self.audio_dir,
            delete=False
        )
        return Path(tmp_file.name)
    
    def cleanup_audio_file(self, audio_path: Path) -> None:
        """Delete audio file"""
        if audio_path.exists():
            audio_path.unlink()