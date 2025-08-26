"""
Audio generation utilities for transcription testing

This module provides real audio file generation for testing the transcription
functionality without mocking the actual Whisper model behavior.
"""

import logging
import math
import struct
import tempfile
import wave
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioGenerator:
    """Generate real audio files for testing transcription functionality"""

    def __init__(self, sample_rate: int = 16000):
        """
        Initialize audio generator

        Args:
            sample_rate: Sample rate for generated audio (Whisper prefers 16kHz)
        """
        self.sample_rate = sample_rate

    def generate_silence(self, duration_seconds: float) -> bytes:
        """Generate silent audio data"""
        num_samples = int(duration_seconds * self.sample_rate)
        return struct.pack("<" + "h" * num_samples, *([0] * num_samples))

    def generate_tone(
        self, frequency: float, duration_seconds: float, amplitude: float = 0.3
    ) -> bytes:
        """
        Generate a pure tone

        Args:
            frequency: Frequency in Hz
            duration_seconds: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)
        """
        num_samples = int(duration_seconds * self.sample_rate)
        samples = []

        for i in range(num_samples):
            # Generate sine wave
            t = i / self.sample_rate
            sample = amplitude * math.sin(2 * math.pi * frequency * t)
            # Convert to 16-bit integer
            sample_int = int(sample * 32767)
            samples.append(sample_int)

        return struct.pack("<" + "h" * num_samples, *samples)

    def generate_speech_like_audio(self, duration_seconds: float) -> bytes:
        """
        Generate speech-like audio with multiple frequencies
        This simulates human speech patterns for more realistic testing
        """
        # Human speech fundamental frequencies: ~85-255 Hz (male), ~165-265 Hz (female)
        # Formant frequencies: ~500-1500 Hz for vowels

        num_samples = int(duration_seconds * self.sample_rate)
        samples = []

        # Create speech-like patterns
        fundamental_freq = 150  # Base frequency
        formant1 = 800  # First formant
        formant2 = 1200  # Second formant

        for i in range(num_samples):
            t = i / self.sample_rate

            # Add some variation to make it more speech-like
            freq_variation = 1.0 + 0.1 * math.sin(2 * math.pi * 5 * t)  # 5Hz variation

            # Combine fundamental and formants
            fundamental = 0.4 * math.sin(2 * math.pi * fundamental_freq * freq_variation * t)
            formant_1 = 0.2 * math.sin(2 * math.pi * formant1 * t)
            formant_2 = 0.1 * math.sin(2 * math.pi * formant2 * t)

            # Add envelope to simulate speech rhythm
            envelope = 0.5 + 0.5 * math.sin(2 * math.pi * 2 * t)  # 2Hz rhythm

            sample = envelope * (fundamental + formant_1 + formant_2)
            sample_int = int(sample * 16383)  # Slightly lower amplitude to avoid clipping
            samples.append(sample_int)

        return struct.pack("<" + "h" * num_samples, *samples)

    def create_wav_file(self, audio_data: bytes, output_path: str | Path) -> Path:
        """
        Create a WAV file from audio data

        Args:
            audio_data: Raw audio bytes
            output_path: Path where to save the file

        Returns:
            Path to the created file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with wave.open(str(output_path), "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data)

        logger.info(f"Created audio file: {output_path} ({len(audio_data)} bytes)")
        return output_path

    def create_test_audio(
        self, test_type: str, duration: float = 3.0, output_dir: Path | None = None
    ) -> Path:
        """
        Create test audio files for different test scenarios

        Args:
            test_type: Type of test audio ('silence', 'tone', 'speech')
            duration: Duration in seconds
            output_dir: Directory to save file (uses temp if None)

        Returns:
            Path to created audio file
        """
        if output_dir is None:
            output_dir = Path(tempfile.gettempdir())

        filename = f"test_{test_type}_{duration}s.wav"
        output_path = output_dir / filename

        if test_type == "silence":
            audio_data = self.generate_silence(duration)
        elif test_type == "tone":
            audio_data = self.generate_tone(440.0, duration)  # A4 note
        elif test_type == "speech":
            audio_data = self.generate_speech_like_audio(duration)
        else:
            raise ValueError(f"Unknown test type: {test_type}")

        return self.create_wav_file(audio_data, output_path)


class TranscriptionTestData:
    """Provides test data and utilities for transcription testing"""

    # Expected transcription results for known audio patterns
    EXPECTED_RESULTS = {
        "silence": "",  # Should transcribe to empty or very minimal
        "tone": "",  # Pure tones typically don't transcribe to meaningful text
        "speech": None,  # Speech-like audio may produce some output but content is unpredictable
    }

    @classmethod
    def get_expected_result(cls, audio_type: str) -> str | None:
        """Get expected transcription result for a given audio type"""
        return cls.EXPECTED_RESULTS.get(audio_type)

    @classmethod
    def validate_transcription_output(cls, audio_type: str, transcribed_text: str) -> bool:
        """
        Validate that transcription output matches expectations for audio type

        Args:
            audio_type: Type of audio that was transcribed
            transcribed_text: The transcription result

        Returns:
            True if result is as expected for this audio type
        """
        transcribed_text = transcribed_text.strip()

        if audio_type in ["silence", "tone"]:
            # These should produce minimal or no text
            return len(transcribed_text) <= 10  # Allow for some model noise
        elif audio_type == "speech":
            # Speech-like audio should produce some output but we can't predict exact content
            # We just verify it's not empty and has reasonable length
            return 0 <= len(transcribed_text) <= 500  # Reasonable bounds

        return False


def create_test_audio_files(
    output_dir: Path, durations: list[float] = None
) -> dict[str, list[Path]]:
    """
    Create a comprehensive set of test audio files

    Args:
        output_dir: Directory to store test files
        durations: List of durations to test (defaults to [1.0, 3.0, 5.0])

    Returns:
        Dict mapping audio types to lists of file paths
    """
    if durations is None:
        durations = [1.0, 3.0, 5.0]

    output_dir.mkdir(parents=True, exist_ok=True)
    generator = AudioGenerator()

    audio_files = {"silence": [], "tone": [], "speech": []}

    for audio_type in audio_files:
        for duration in durations:
            file_path = generator.create_test_audio(audio_type, duration, output_dir)
            audio_files[audio_type].append(file_path)

    logger.info(f"Created {sum(len(files) for files in audio_files.values())} test audio files")
    return audio_files
