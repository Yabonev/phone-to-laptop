"""
Performance and benchmarking tests for the transcription system

These tests measure actual performance characteristics of the real system
components to ensure they meet performance requirements.
"""

import asyncio
import statistics
import time

import pytest

from src.core.services.container import ServiceContainer
from src.infrastructure.transcription.whisper_adapter import TranscriptionService


class TestTranscriptionPerformanceBenchmarks:
    """Benchmark transcription performance with real Whisper models"""

    @pytest.mark.performance
    @pytest.mark.transcription
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_whisper_model_loading_benchmark(self, temp_dir):
        """Benchmark Whisper model loading times for different models"""
        models_to_test = ["tiny", "base"]  # Don't test larger models in CI
        results = {}

        for model_name in models_to_test:
            # Test model loading time
            service = TranscriptionService(model_name=model_name, audio_dir=temp_dir / "audio")

            start_time = time.time()
            service._load_model()
            load_time = time.time() - start_time

            results[model_name] = load_time

            # Verify model loaded correctly
            assert service.model is not None

            print(f"{model_name} model loading time: {load_time:.2f}s")

        # Performance assertions
        assert results["tiny"] < 30.0, f"Tiny model loading too slow: {results['tiny']:.2f}s"
        if "base" in results:
            assert results["base"] < 60.0, f"Base model loading too slow: {results['base']:.2f}s"

        print(f"Model loading benchmark results: {results}")

    @pytest.mark.performance
    @pytest.mark.transcription
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_transcription_speed_benchmark(
        self, real_transcription_service, audio_generator, temp_dir
    ):
        """Benchmark transcription speed for different audio durations"""
        service = real_transcription_service

        # Test different audio durations
        durations = [1.0, 2.0, 5.0]  # seconds
        audio_types = ["silence", "tone", "speech"]

        results = {}

        for duration in durations:
            duration_results = {}

            for audio_type in audio_types:
                # Create test audio
                if audio_type == "silence":
                    audio_data = audio_generator.generate_silence(duration)
                elif audio_type == "tone":
                    audio_data = audio_generator.generate_tone(440.0, duration)
                else:  # speech
                    audio_data = audio_generator.generate_speech_like_audio(duration)

                audio_file = audio_generator.create_wav_file(
                    audio_data, temp_dir / f"perf_{audio_type}_{duration}s.wav"
                )

                try:
                    # Benchmark transcription
                    start_time = time.time()
                    text, language = await service.transcribe_audio(audio_file, "en")
                    transcription_time = time.time() - start_time

                    duration_results[audio_type] = {
                        "time": transcription_time,
                        "text_length": len(text),
                        "speed_ratio": transcription_time / duration,
                    }

                finally:
                    if audio_file.exists():
                        audio_file.unlink()

            results[duration] = duration_results

        # Print benchmark results
        print("\n=== Transcription Speed Benchmark ===")
        for duration, types in results.items():
            print(f"\n{duration}s audio:")
            for audio_type, metrics in types.items():
                print(
                    f"  {audio_type}: {metrics['time']:.2f}s "
                    f"(ratio: {metrics['speed_ratio']:.2f}x, "
                    f"output: {metrics['text_length']} chars)"
                )

        # Performance assertions
        for duration, types in results.items():
            for audio_type, metrics in types.items():
                # Transcription should not take more than 10x the audio duration
                max_time = duration * 10
                assert metrics["time"] < max_time, (
                    f"{audio_type} {duration}s took too long: {metrics['time']:.2f}s"
                )

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_transcription_performance(
        self, real_transcription_service, audio_generator, temp_dir
    ):
        """Test performance under concurrent transcription load"""
        service = real_transcription_service

        # Create multiple audio files
        audio_files = []
        for i in range(3):  # Test with 3 concurrent transcriptions
            audio_data = audio_generator.generate_silence(2.0)
            audio_file = audio_generator.create_wav_file(
                audio_data, temp_dir / f"concurrent_{i}.wav"
            )
            audio_files.append(audio_file)

        try:
            # Test sequential transcription
            sequential_start = time.time()
            for audio_file in audio_files:
                await service.transcribe_audio(audio_file, "en")
            sequential_time = time.time() - sequential_start

            # Test concurrent transcription
            concurrent_start = time.time()
            tasks = [service.transcribe_audio(audio_file, "en") for audio_file in audio_files]
            await asyncio.gather(*tasks)
            concurrent_time = time.time() - concurrent_start

            print(f"Sequential transcription: {sequential_time:.2f}s")
            print(f"Concurrent transcription: {concurrent_time:.2f}s")
            print(f"Speedup: {sequential_time / concurrent_time:.2f}x")

            # Concurrent should not be significantly slower than sequential
            # (Whisper model is CPU-bound, so we don't expect major speedup)
            assert concurrent_time < sequential_time * 1.5, (
                "Concurrent transcription significantly slower than sequential"
            )

        finally:
            # Cleanup
            for audio_file in audio_files:
                if audio_file.exists():
                    audio_file.unlink()


class TestServicePerformanceBenchmarks:
    """Benchmark service layer performance"""

    @pytest.mark.performance
    @pytest.mark.integration
    def test_state_service_performance(self, temp_dir):
        """Benchmark state service operations"""
        from src.infrastructure.storage.json_state import StateService

        state_file = temp_dir / "perf_state.json"
        service = StateService(state_file)

        # Benchmark project operations
        num_projects = 100

        # Time project additions
        start_time = time.time()
        for i in range(num_projects):
            service.add_project(f"project_{i:03d}", f"Project {i}")
        add_time = time.time() - start_time

        # Time project retrievals
        start_time = time.time()
        for _ in range(100):
            service.get_projects()
        get_time = time.time() - start_time

        # Time message processing tracking
        start_time = time.time()
        for i in range(1000):
            service.mark_message_processed(f"msg_{i}")
        message_time = time.time() - start_time

        print("State service performance:")
        print(
            f"  Add {num_projects} projects: {add_time:.3f}s ({add_time / num_projects * 1000:.1f}ms each)"
        )
        print(f"  100 project retrievals: {get_time:.3f}s ({get_time / 100 * 1000:.1f}ms each)")
        print(
            f"  1000 message marks: {message_time:.3f}s ({message_time / 1000 * 1000:.1f}ms each)"
        )

        # Performance assertions
        assert add_time < 1.0, f"Adding {num_projects} projects too slow: {add_time:.3f}s"
        assert get_time < 0.5, f"100 project retrievals too slow: {get_time:.3f}s"
        assert message_time < 1.0, f"1000 message marks too slow: {message_time:.3f}s"

    @pytest.mark.performance
    @pytest.mark.integration
    def test_project_service_performance(self, temp_dir):
        """Benchmark project service file operations"""
        from src.infrastructure.storage.file_project import ProjectService

        projects_dir = temp_dir / "projects"
        service = ProjectService(projects_dir)

        # Time project creation
        num_projects = 20
        project_ids = []

        start_time = time.time()
        for i in range(num_projects):
            project_id = service.create_project(f"Perf Project {i}", {})
            project_ids.append(project_id)
        creation_time = time.time() - start_time

        # Time note addition
        notes_per_project = 10
        start_time = time.time()
        for project_id in project_ids:
            for j in range(notes_per_project):
                service.add_note(project_id, f"Performance test note {j} for project {project_id}")
        note_time = time.time() - start_time

        # Time statistics calculation
        start_time = time.time()
        for project_id in project_ids:
            service.get_project_stats(project_id)
        stats_time = time.time() - start_time

        total_notes = num_projects * notes_per_project

        print("Project service performance:")
        print(
            f"  Create {num_projects} projects: {creation_time:.3f}s ({creation_time / num_projects * 1000:.1f}ms each)"
        )
        print(
            f"  Add {total_notes} notes: {note_time:.3f}s ({note_time / total_notes * 1000:.1f}ms each)"
        )
        print(
            f"  Calculate {num_projects} stats: {stats_time:.3f}s ({stats_time / num_projects * 1000:.1f}ms each)"
        )

        # Performance assertions
        assert creation_time < 5.0, (
            f"Creating {num_projects} projects too slow: {creation_time:.3f}s"
        )
        assert note_time < 5.0, f"Adding {total_notes} notes too slow: {note_time:.3f}s"
        assert stats_time < 2.0, f"Calculating {num_projects} stats too slow: {stats_time:.3f}s"

    @pytest.mark.performance
    @pytest.mark.integration
    def test_service_container_initialization_performance(self, test_config):
        """Benchmark service container initialization"""
        num_initializations = 10
        times = []

        for _i in range(num_initializations):
            start_time = time.time()
            container = ServiceContainer(test_config)
            # Get all services to ensure they're initialized
            container.get_all()
            initialization_time = time.time() - start_time
            times.append(initialization_time)

        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)

        print("Service container initialization performance:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Min: {min_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        print(f"  All times: {[f'{t:.3f}' for t in times]}")

        # Performance assertions
        assert avg_time < 2.0, f"Service container initialization too slow: {avg_time:.3f}s"
        assert max_time < 5.0, f"Slowest initialization too slow: {max_time:.3f}s"


class TestMemoryUsageBenchmarks:
    """Test memory usage characteristics (basic monitoring)"""

    @pytest.mark.performance
    @pytest.mark.slow
    def test_transcription_service_memory_usage(self, temp_dir):
        """Monitor memory usage of transcription service operations"""
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create transcription service (should load model)
        service = TranscriptionService(model_name="tiny", audio_dir=temp_dir / "audio")
        service._load_model()

        # Memory after model loading
        model_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = model_memory - baseline_memory

        print("Memory usage benchmark:")
        print(f"  Baseline: {baseline_memory:.1f} MB")
        print(f"  After tiny model load: {model_memory:.1f} MB")
        print(f"  Model memory overhead: {memory_increase:.1f} MB")

        # Memory usage should be reasonable for tiny model
        assert memory_increase < 500, f"Tiny model uses too much memory: {memory_increase:.1f} MB"

        # Cleanup
        del service

    @pytest.mark.performance
    @pytest.mark.integration
    def test_large_project_memory_usage(self, temp_dir):
        """Test memory usage with large project files"""
        import os

        import psutil

        from src.infrastructure.storage.file_project import ProjectService

        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        projects_dir = temp_dir / "projects"
        service = ProjectService(projects_dir)

        # Create project with many notes
        project_id = service.create_project("Large Project", {})

        # Add many notes to simulate large project
        for i in range(500):  # 500 notes
            long_text = (
                f"This is note {i} with some longer text content to simulate realistic note sizes. "
                * 5
            )
            service.add_note(project_id, long_text)

        # Check memory after large project operations
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - baseline_memory

        # Test reading project stats (should not load entire file into memory persistently)
        for _ in range(10):
            service.get_project_stats(project_id)

        stats_memory = process.memory_info().rss / 1024 / 1024  # MB
        stats_increase = stats_memory - baseline_memory

        print("Large project memory usage:")
        print(f"  Baseline: {baseline_memory:.1f} MB")
        print(f"  After 500 notes: {final_memory:.1f} MB (+{memory_increase:.1f} MB)")
        print(f"  After stats operations: {stats_memory:.1f} MB (+{stats_increase:.1f} MB)")

        # Memory increases should be reasonable
        assert memory_increase < 100, (
            f"Large project uses too much memory: {memory_increase:.1f} MB"
        )
        assert stats_increase < 120, f"Stats operations leak memory: {stats_increase:.1f} MB"
