"""Unit tests for UI features including explanations and metrics collection."""

import pytest
from src.musicrec.ui.explanations import generate_explanation, get_top_features
from src.musicrec.metrics.collector import MetricsCollector


class TestExplanationGenerator:
    """Test suite for recommendation explanation generation."""

    def test_generate_explanation_similarity(self):
        """Test explanation generation for similarity-based recommendations."""
        track_info = {
            "track_name": "Test Song",
            "artist_name": "Test Artist",
            "genre_path": ["rock", "alternative"],
            "mood_tags": ["energetic", "upbeat"],
            "energy": 0.8,
            "valence": 0.7,
        }

        explanation = generate_explanation(
            track_info,
            "similarity",
            similarity_score=0.85,
            source_track="Original Song",
        )

        assert "Test Song" in explanation
        assert "Test Artist" in explanation
        assert "85%" in explanation
        assert "Original Song" in explanation
        assert "high energy" in explanation

    def test_generate_explanation_genre(self):
        """Test explanation generation for genre-based recommendations."""
        track_info = {
            "track_name": "Rock Song",
            "artist_name": "Rock Artist",
            "genre_path": ["rock", "metal"],
            "mood_tags": ["intense"],
            "energy": 0.9,
            "valence": 0.3,
        }

        explanation = generate_explanation(track_info, "genre")

        assert "Rock Song" in explanation
        assert "Rock Artist" in explanation
        assert "rock → metal" in explanation
        assert "high energy" in explanation

    def test_generate_explanation_mood(self):
        """Test explanation generation for mood-based recommendations."""
        track_info = {
            "track_name": "Happy Song",
            "artist_name": "Happy Artist",
            "genre_path": ["pop"],
            "mood_tags": ["happy", "cheerful"],
            "energy": 0.6,
            "valence": 0.9,
        }

        explanation = generate_explanation(track_info, "mood")

        assert "Happy Song" in explanation
        assert "Happy Artist" in explanation
        assert "happy, cheerful" in explanation
        assert "positive mood" in explanation

    def test_generate_explanation_empty_data(self):
        """Test explanation generation with minimal data."""
        track_info = {"track_id": "unknown123"}

        explanation = generate_explanation(track_info, "genre")

        assert "Unknown Track" in explanation
        assert "Unknown Artist" in explanation
        assert "Genre-based" in explanation

    def test_get_top_features_energetic(self):
        """Test feature extraction for energetic tracks."""
        track_info = {
            "energy": 0.9,
            "valence": 0.8,
            "tempo": 150.0,
        }

        features = get_top_features(track_info)

        assert len(features) <= 3
        assert any("energetic" in f.lower() for f in features)
        assert any("upbeat" in f.lower() for f in features)
        assert any("fast tempo" in f.lower() for f in features)

    def test_get_top_features_calm(self):
        """Test feature extraction for calm tracks."""
        track_info = {
            "energy": 0.2,
            "valence": 0.3,
            "tempo": 70.0,
        }

        features = get_top_features(track_info)

        assert len(features) <= 3
        assert any("calm" in f.lower() for f in features)
        assert any("melancholic" in f.lower() or "calm" in f.lower() for f in features)
        assert any("slow tempo" in f.lower() for f in features)


class TestMetricsCollector:
    """Test suite for metrics collection functionality."""

    def test_metrics_collector_initialization(self):
        """Test that metrics collector initializes correctly."""
        collector = MetricsCollector()
        metrics = collector.get_metrics()

        assert metrics["total_requests"] == 0
        assert metrics["successful_requests"] == 0
        assert metrics["failed_requests"] == 0
        assert metrics["success_rate_percent"] == 0.0
        assert metrics["average_latency_ms"] == 0.0

    def test_record_successful_request(self):
        """Test recording successful requests."""
        collector = MetricsCollector()

        # Simulate a request
        start_time = collector.record_request_start()
        collector.record_request_success(start_time, "test_request")

        metrics = collector.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1
        assert metrics["failed_requests"] == 0
        assert metrics["success_rate_percent"] == 100.0
        assert metrics["average_latency_ms"] >= 0
        assert "test_request" in metrics["request_types"]

    def test_record_failed_request(self):
        """Test recording failed requests."""
        collector = MetricsCollector()

        collector.record_request_failure("test_request")

        metrics = collector.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 0
        assert metrics["failed_requests"] == 1
        assert metrics["success_rate_percent"] == 0.0
        assert "test_request_failures" in metrics["request_types"]

    def test_mixed_requests_metrics(self):
        """Test metrics with both successful and failed requests."""
        collector = MetricsCollector()

        # Record mixed results
        start_time = collector.record_request_start()
        collector.record_request_success(start_time, "search")
        collector.record_request_failure("search")
        start_time2 = collector.record_request_start()
        collector.record_request_success(start_time2, "similarity")

        metrics = collector.get_metrics()
        assert metrics["total_requests"] == 3
        assert metrics["successful_requests"] == 2
        assert metrics["failed_requests"] == 1
        assert abs(metrics["success_rate_percent"] - 66.67) < 0.1

    def test_reset_metrics(self):
        """Test resetting metrics to zero."""
        collector = MetricsCollector()

        # Add some data
        collector.record_request_failure("test")
        assert collector.get_metrics()["total_requests"] == 1

        # Reset and verify
        collector.reset_metrics()
        metrics = collector.get_metrics()
        assert metrics["total_requests"] == 0
        assert metrics["successful_requests"] == 0
        assert metrics["failed_requests"] == 0


class TestAccessibilityFeatures:
    """Test suite for accessibility-related functionality."""

    def test_explanation_text_readability(self):
        """Test that explanation text is readable and informative."""
        track_info = {
            "track_name": "Complex Song Title with Special Characters & Numbers 123",
            "artist_name": "Artist Name",
            "genre_path": ["electronic", "techno", "minimal"],
            "mood_tags": ["dark", "mysterious"],
            "energy": 0.75,
            "valence": 0.4,
        }

        explanation = generate_explanation(track_info, "genre")

        # Check that explanation is reasonably concise but informative
        assert len(explanation) > 20  # Not too short
        assert len(explanation) < 200  # Not too long
        assert explanation.count("→") >= 1  # Shows hierarchy

        # Check that special characters are handled
        assert "Complex Song Title" in explanation

    def test_error_handling_in_explanations(self):
        """Test that explanation generator handles edge cases gracefully."""
        # Test with None values
        track_info = {
            "track_name": None,
            "artist_name": None,
            "genre_path": None,
            "mood_tags": None,
        }

        explanation = generate_explanation(track_info, "genre")

        # Should not crash and should provide reasonable defaults
        assert "Unknown Track" in explanation
        assert len(explanation) > 0
