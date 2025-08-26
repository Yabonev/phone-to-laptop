"""
REAL transcription tests using actual Whisper models and audio files

These tests replace the mock-abusing transcription tests with real functionality validation.
We use actual Whisper models and generated audio to verify transcription actually works.
"""

import pytest

from src.infrastructure.transcription.whisper_adapter import TranscriptionService
from tests.audio_helpers import TranscriptionTestData


class TestRealTranscriptionService:
    """Test transcription service with REAL Whisper models and audio"""

    @pytest.mark.transcription
    def test_service_initialization_creates_audio_dir(self, temp_dir):
        """Test that service properly initializes and creates directories"""
        audio_dir = temp_dir / "audio"
        service = TranscriptionService(model_name="tiny", audio_dir=audio_dir)

        # Verify properties set correctly
        assert service.model_name == "tiny"
        assert service.audio_dir == audio_dir
        assert service.model is None  # Lazy loading

        # Verify directory was created
        assert audio_dir.exists()
        assert audio_dir.is_dir()

    @pytest.mark.transcription
    def test_model_loading_actually_loads_whisper(self, real_transcription_service):
        """Test that model loading actually loads a real Whisper model"""
        service = real_transcription_service

        # Model should be None initially (or pre-loaded in fixture)
        # Load it if not already loaded
        if service.model is None:
            service._load_model()

        # Verify we have a real Whisper model
        assert service.model is not None
        assert hasattr(service.model, "transcribe")
        assert callable(service.model.transcribe)

    @pytest.mark.transcription
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_transcribe_silence_produces_minimal_output(
        self, real_transcription_service, audio_generator, temp_dir
    ):
        """Test that silent audio produces minimal or no transcription"""
        service = real_transcription_service

        # Create 2 seconds of silence
        silence_data = audio_generator.generate_silence(2.0)
        audio_file = audio_generator.create_wav_file(silence_data, temp_dir / "silence.wav")

        try:
            # Transcribe the silence
            text, language = await service.transcribe_audio(audio_file, "en")

            # Silence should produce minimal text (Whisper may output some noise)
            assert TranscriptionTestData.validate_transcription_output("silence", text)
            assert language == "en"

            # Log what was actually transcribed for debugging
            print(f"Silence transcription result: '{text}' (length: {len(text)})")

        finally:
            # Cleanup
            if audio_file.exists():
                audio_file.unlink()

    @pytest.mark.transcription
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_transcribe_tone_produces_minimal_output(
        self, real_transcription_service, audio_generator, temp_dir
    ):
        """Test that pure tone audio produces minimal transcription"""
        service = real_transcription_service

        # Create 3 seconds of 440Hz tone (A4 note)
        tone_data = audio_generator.generate_tone(440.0, 3.0)
        audio_file = audio_generator.create_wav_file(tone_data, temp_dir / "tone.wav")

        try:
            # Transcribe the tone
            text, language = await service.transcribe_audio(audio_file, "en")

            # Pure tones should not transcribe to meaningful text
            assert TranscriptionTestData.validate_transcription_output("tone", text)
            assert language == "en"

            print(f"Tone transcription result: '{text}' (length: {len(text)})")

        finally:
            if audio_file.exists():
                audio_file.unlink()

    @pytest.mark.transcription
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_transcribe_speech_like_audio(
        self, real_transcription_service, audio_generator, temp_dir
    ):
        """Test that speech-like audio produces some transcription output"""
        service = real_transcription_service

        # Create 4 seconds of speech-like audio
        speech_data = audio_generator.generate_speech_like_audio(4.0)
        audio_file = audio_generator.create_wav_file(speech_data, temp_dir / "speech.wav")

        try:
            # Transcribe the speech-like audio
            text, language = await service.transcribe_audio(audio_file, "en")

            # Speech-like audio may produce some output
            assert TranscriptionTestData.validate_transcription_output("speech", text)
            assert language == "en"

            print(f"Speech-like transcription result: '{text}' (length: {len(text)})")

        finally:
            if audio_file.exists():
                audio_file.unlink()

    @pytest.mark.transcription
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_translation_to_english_with_bulgarian_language(
        self, real_transcription_service, audio_generator, temp_dir
    ):
        """Test Bulgarian to English translation functionality"""
        service = real_transcription_service

        # Create test audio (speech-like for Bulgarian)
        speech_data = audio_generator.generate_speech_like_audio(3.0)
        audio_file = audio_generator.create_wav_file(speech_data, temp_dir / "bulgarian.wav")

        try:
            # Test translation function
            translation = await service.translate_to_english(audio_file, "bg")

            # Should return a string (even if empty or minimal for generated audio)
            assert isinstance(translation, str)
            # Translation should be reasonable length (not massive)
            assert len(translation) <= 500

            print(f"Bulgarian translation result: '{translation}' (length: {len(translation)})")

        finally:
            if audio_file.exists():
                audio_file.unlink()

    @pytest.mark.transcription
    def test_temp_audio_file_creation(self, real_transcription_service):
        """Test that temporary audio files are created correctly"""
        service = real_transcription_service

        # Create temp file
        temp_file = service.create_temp_audio_file(".ogg")

        try:
            # Verify file properties
            assert temp_file.exists()
            assert temp_file.suffix == ".ogg"
            assert temp_file.parent == service.audio_dir

            # Verify we can write to it
            temp_file.write_bytes(b"test data")
            assert temp_file.read_bytes() == b"test data"

        finally:
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()

    @pytest.mark.transcription
    def test_audio_file_cleanup(self, real_transcription_service, temp_dir):
        """Test that audio file cleanup actually deletes files"""
        service = real_transcription_service

        # Create test file
        test_file = temp_dir / "test_cleanup.ogg"
        test_file.write_bytes(b"test audio data")
        assert test_file.exists()

        # Cleanup file
        service.cleanup_audio_file(test_file)

        # Verify file was deleted
        assert not test_file.exists()

        # Cleanup non-existent file should not error
        service.cleanup_audio_file(test_file)  # Should not raise

    @pytest.mark.transcription
    @pytest.mark.asyncio
    async def test_transcription_with_nonexistent_file_raises_error(
        self, real_transcription_service, temp_dir
    ):
        """Test that transcribing non-existent file raises appropriate error"""
        service = real_transcription_service

        nonexistent_file = temp_dir / "does_not_exist.wav"
        assert not nonexistent_file.exists()

        # Should raise an exception when trying to transcribe non-existent file
        with pytest.raises(Exception):  # Could be FileNotFoundError or other Whisper error
            await service.transcribe_audio(nonexistent_file, "en")

    @pytest.mark.transcription
    @pytest.mark.asyncio
    async def test_transcription_with_invalid_language_code(
        self, real_transcription_service, audio_generator, temp_dir
    ):
        """Test transcription behavior with invalid language codes"""
        service = real_transcription_service

        # Create valid audio
        silence_data = audio_generator.generate_silence(1.0)
        audio_file = audio_generator.create_wav_file(silence_data, temp_dir / "test.wav")

        try:
            # Test with invalid language code
            # Whisper should handle this gracefully or raise specific error
            text, language = await service.transcribe_audio(audio_file, "invalid_lang")

            # Should either work (Whisper fallback) or raise exception
            # The key is that it should be consistent and not crash unexpectedly
            assert isinstance(text, str)
            assert isinstance(language, str)

        except Exception as e:
            # If it raises an exception, it should be a sensible one
            assert "language" in str(e).lower() or "invalid" in str(e).lower()

        finally:
            if audio_file.exists():
                audio_file.unlink()


class TestTranscriptionPerformance:
    """Performance tests for transcription functionality"""

    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_transcription_performance_benchmarks(
        self, real_transcription_service, test_audio_files, performance_timer
    ):
        """Benchmark transcription performance with different audio types and durations"""
        service = real_transcription_service

        results = {}

        for audio_type, files in test_audio_files.items():
            type_results = []

            for audio_file in files:
                # Time the transcription
                performance_timer.start()
                text, language = await service.transcribe_audio(audio_file, "en")
                duration = performance_timer.stop()

                type_results.append(
                    {
                        "file": audio_file.name,
                        "duration": duration,
                        "text_length": len(text),
                        "text_preview": text[:50] + "..." if len(text) > 50 else text,
                    }
                )

            results[audio_type] = type_results

        # Log performance results
        print("\n=== Transcription Performance Results ===")
        for audio_type, type_results in results.items():
            print(f"\n{audio_type.upper()} Audio:")
            for result in type_results:
                print(
                    f"  {result['file']}: {result['duration']:.2f}s -> {result['text_length']} chars"
                )
                if result["text_preview"].strip():
                    print(f"    Preview: '{result['text_preview']}'")

        # Performance assertions
        for audio_type, type_results in results.items():
            for result in type_results:
                # Transcription should complete in reasonable time (adjust based on your hardware)
                assert result["duration"] < 30.0, (
                    f"Transcription took too long: {result['duration']:.2f}s"
                )

                # Validate output makes sense for audio type
                assert TranscriptionTestData.validate_transcription_output(
                    audio_type, result["text_preview"]
                ), f"Invalid output for {audio_type}: '{result['text_preview']}'"

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_model_loading_performance(self, temp_dir, performance_timer):
        """Test that model loading happens within reasonable time"""
        # Create service without pre-loaded model
        service = TranscriptionService(model_name="tiny", audio_dir=temp_dir / "audio")

        # Time model loading
        performance_timer.start()
        service._load_model()
        load_time = performance_timer.stop()

        # Model loading should be reasonably fast for tiny model
        assert load_time < 60.0, f"Model loading took too long: {load_time:.2f}s"

        # Verify model was actually loaded
        assert service.model is not None

        print(f"Tiny model loading time: {load_time:.2f}s")


class TestTranscriptionErrorHandling:
    """Test error handling and edge cases in transcription"""

    @pytest.mark.transcription
    @pytest.mark.asyncio
    async def test_corrupted_audio_file_handling(self, real_transcription_service, temp_dir):
        """Test behavior with corrupted audio files"""
        service = real_transcription_service

        # Create corrupted audio file (not valid audio format)
        corrupted_file = temp_dir / "corrupted.wav"
        corrupted_file.write_bytes(b"This is not audio data" * 100)

        try:
            # Should raise appropriate error for corrupted file
            with pytest.raises(Exception):  # Whisper will raise some exception
                await service.transcribe_audio(corrupted_file, "en")

        finally:
            if corrupted_file.exists():
                corrupted_file.unlink()

    @pytest.mark.transcription
    @pytest.mark.asyncio
    async def test_empty_audio_file_handling(self, real_transcription_service, temp_dir):
        """Test behavior with empty audio files"""
        service = real_transcription_service

        # Create empty file
        empty_file = temp_dir / "empty.wav"
        empty_file.touch()

        try:
            # Should handle empty file gracefully or raise appropriate error
            with pytest.raises(Exception):
                await service.transcribe_audio(empty_file, "en")

        finally:
            if empty_file.exists():
                empty_file.unlink()

    @pytest.mark.transcription
    def test_service_with_invalid_audio_directory(self):
        """Test service behavior with invalid audio directory"""
        # Try to create service with invalid directory path
        with pytest.raises(Exception):
            service = TranscriptionService(
                model_name="tiny", audio_dir="/invalid/path/that/does/not/exist"
            )
            # Service creation might succeed, but directory creation should fail
            service._load_model()  # This or other operations should fail
