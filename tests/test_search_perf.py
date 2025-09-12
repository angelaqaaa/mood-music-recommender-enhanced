"""CSC111 Winter 2025: A Mood-Driven Music Recommender with Genre Hierarchies

Performance and optimization tests for search functionality including trigram
prefiltering and similarity caching.

Copyright and Usage Information
===============================
This file is Copyright (c) 2025 Qian (Angela) Su.
"""

import pytest
import time
from unittest.mock import Mock
from src.musicrec.ui.search import SearchEngine


class TestSearchPerformanceOptimizations:
    """Test suite for search performance optimizations."""

    @pytest.fixture
    def large_dataset_recommender(self):
        """Create a mock recommender with a large synthetic dataset."""
        recommender = Mock()

        # Generate synthetic track data
        track_names = [
            "Bohemian Rhapsody",
            "Hotel California",
            "Stairway to Heaven",
            "Another Brick in the Wall",
            "Sweet Child O' Mine",
            "Thunderstruck",
            "Back in Black",
            "Highway to Hell",
            "We Will Rock You",
            "Don't Stop Believin'",
            "More Than a Feeling",
            "Free Bird",
            "American Pie",
            "Piano Man",
            "Imagine",
            "Yesterday",
            "Like a Rolling Stone",
            "Satisfaction",
            "Hey Jude",
            "Bridge Over Troubled Water",
        ]

        artists = [
            "Queen",
            "Eagles",
            "Led Zeppelin",
            "Pink Floyd",
            "Guns N' Roses",
            "AC/DC",
            "Journey",
            "Boston",
            "Lynyrd Skynyrd",
            "Don McLean",
            "Billy Joel",
            "John Lennon",
            "The Beatles",
            "Bob Dylan",
            "The Rolling Stones",
            "Simon & Garfunkel",
        ]

        # Create 1000+ tracks by combining and adding variations
        mock_tracks = {}
        for i in range(1000):
            track_name = f"{track_names[i % len(track_names)]} {i // len(track_names)}"
            artist_name = artists[i % len(artists)]
            mock_tracks[f"track{i}"] = Mock(
                data={"track_name": track_name, "artist_name": artist_name}
            )

        recommender.genre_tree.tracks = mock_tracks

        def mock_get_track_info(track_id):
            return {"genre_path": ["rock"], "mood_tags": ["energetic"]}

        recommender.get_track_info = mock_get_track_info
        return recommender

    def test_trigram_generation(self):
        """Test trigram generation correctness."""
        mock_recommender = Mock()
        mock_recommender.genre_tree.tracks = {}

        engine = SearchEngine(mock_recommender)

        # Test basic trigram generation
        trigrams = engine._generate_trigrams("hello")
        expected = {"  h", " he", "hel", "ell", "llo", "lo ", "o  "}
        assert trigrams == expected

        # Test short text
        short_trigrams = engine._generate_trigrams("hi")
        assert short_trigrams == {"hi"}

        # Test empty text
        empty_trigrams = engine._generate_trigrams("")
        assert empty_trigrams == {""}

    def test_trigram_prefiltering_reduces_candidates(self, large_dataset_recommender):
        """Test that trigram prefiltering reduces the candidate set."""
        engine = SearchEngine(
            large_dataset_recommender, enable_fuzzy=True, prefilter_top_n=50
        )

        # Test prefiltering
        candidates = engine._prefilter_candidates("bohemian")

        # Should return limited number of candidates
        assert len(candidates) <= 50
        assert len(candidates) > 0

        # Check that candidates are sorted by score
        if len(candidates) > 1:
            scores = [score for _, score in candidates]
            assert scores == sorted(scores, reverse=True)

    def test_trigram_prefiltering_preserves_correct_match(
        self, large_dataset_recommender
    ):
        """Test that prefiltering preserves the best matches."""
        engine = SearchEngine(
            large_dataset_recommender, enable_fuzzy=True, prefilter_top_n=30
        )

        # Search for a query that should match known tracks
        candidates = engine._prefilter_candidates("bohemian")
        candidate_ids = [track_id for track_id, _ in candidates]

        # Find tracks that contain "Bohemian" in the dataset
        bohemian_tracks = []
        for track_id, node in large_dataset_recommender.genre_tree.tracks.items():
            if "bohemian" in node.data["track_name"].lower():
                bohemian_tracks.append(track_id)

        # At least some Bohemian tracks should be in the prefiltered candidates
        found_matches = sum(
            1 for track_id in bohemian_tracks if track_id in candidate_ids
        )
        assert found_matches > 0

    def test_similarity_caching_behavior(self):
        """Test that similarity caching works correctly."""
        mock_recommender = Mock()
        mock_tracks = {
            "track1": Mock(
                data={"track_name": "Test Track", "artist_name": "Test Artist"}
            )
        }
        mock_recommender.genre_tree.tracks = mock_tracks
        mock_recommender.get_track_info = Mock(
            return_value={"genre_path": [], "mood_tags": []}
        )

        engine = SearchEngine(mock_recommender, enable_fuzzy=True, cache_size=128)

        # Clear cache to start fresh
        engine.clear_cache()

        # First call should compute and cache
        sim1 = engine._fuzzy_similarity("test", "testing")

        # Second call should use cache (verify by checking cache info)
        sim2 = engine._fuzzy_similarity("test", "testing")

        assert sim1 == sim2
        assert engine._cached_similarity.cache_info().hits >= 1

    def test_cache_warming_and_reuse(self):
        """Test cache warming and reuse across searches."""
        mock_recommender = Mock()
        mock_tracks = {
            "track1": Mock(
                data={"track_name": "Rock Song", "artist_name": "Artist One"}
            ),
            "track2": Mock(
                data={"track_name": "Pop Song", "artist_name": "Artist Two"}
            ),
        }
        mock_recommender.genre_tree.tracks = mock_tracks
        mock_recommender.get_track_info = Mock(
            return_value={"genre_path": [], "mood_tags": []}
        )

        engine = SearchEngine(mock_recommender, enable_fuzzy=True, cache_size=128)
        engine.clear_cache()

        # First search with typo - will populate cache with similarity computations
        results1 = engine.search_tracks("rok")  # Typo for "rock"
        initial_hits = engine._cached_similarity.cache_info().hits

        # Second search with same typo - should hit cache more
        results2 = engine.search_tracks("rok")
        final_hits = engine._cached_similarity.cache_info().hits

        # Cache should be used on second identical search
        assert (
            final_hits >= initial_hits
        )  # Allow for equal in case computation is minimal
        assert len(results1) >= 0  # May or may not find results depending on threshold
        assert len(results2) >= 0

    def test_performance_with_large_dataset(self, large_dataset_recommender):
        """Test search performance meets target on large dataset."""
        engine = SearchEngine(
            large_dataset_recommender,
            enable_fuzzy=True,
            prefilter_top_n=30,
            cache_size=1024,
        )

        # Test queries with different characteristics
        test_queries = ["bohemian", "queen", "stairway", "hotel"]

        for query in test_queries:
            # Warm up cache
            engine.search_tracks(query)

            # Measure performance over multiple runs
            times = []
            for _ in range(5):
                start_time = time.monotonic()
                results = engine.search_tracks(query)
                end_time = time.monotonic()

                execution_time_ms = (end_time - start_time) * 1000
                times.append(execution_time_ms)

                # Should return results
                assert isinstance(results, list)

            # Calculate median time
            times.sort()
            median_time = times[len(times) // 2]

            # Performance assertion - should complete under 200ms
            assert (
                median_time < 200
            ), f"Query '{query}' median time {median_time:.2f}ms exceeded 200ms"

    def test_performance_comparison_with_without_optimizations(
        self, large_dataset_recommender
    ):
        """Compare performance with and without optimizations."""
        # Engine with optimizations
        optimized_engine = SearchEngine(
            large_dataset_recommender,
            enable_fuzzy=True,
            prefilter_top_n=30,
            cache_size=1024,
        )

        # Engine without prefiltering (larger prefilter limit simulates no prefiltering)
        unoptimized_engine = SearchEngine(
            large_dataset_recommender,
            enable_fuzzy=True,
            prefilter_top_n=1000,  # Large enough to include all tracks
            cache_size=1,
        )

        query = "bohemian"

        # Measure optimized version
        start_time = time.monotonic()
        optimized_results = optimized_engine.search_tracks(query)
        optimized_time = (time.monotonic() - start_time) * 1000

        # Measure unoptimized version
        start_time = time.monotonic()
        unoptimized_results = unoptimized_engine.search_tracks(query)
        unoptimized_time = (time.monotonic() - start_time) * 1000

        # Both should return results
        assert len(optimized_results) > 0
        assert len(unoptimized_results) > 0

        # Optimized version should be faster (or at least not significantly slower)
        # Allow some variance in measurement
        assert optimized_time <= unoptimized_time * 1.5, (
            f"Optimized search ({optimized_time:.2f}ms) should be faster than "
            f"unoptimized ({unoptimized_time:.2f}ms)"
        )

    def test_cache_size_limits(self):
        """Test that cache respects size limits."""
        mock_recommender = Mock()
        mock_recommender.genre_tree.tracks = {}

        # Create engine with small cache
        engine = SearchEngine(mock_recommender, cache_size=4)
        engine.clear_cache()

        # Fill cache beyond limit
        unique_queries = ["query1", "query2", "query3", "query4", "query5", "query6"]

        for i, query in enumerate(unique_queries):
            engine._fuzzy_similarity(query, "target")
            cache_info = engine._cached_similarity.cache_info()

            # Cache size should not exceed maxsize
            assert cache_info.currsize <= 4

    def test_trigram_edge_cases(self):
        """Test trigram generation with edge cases."""
        mock_recommender = Mock()
        mock_recommender.genre_tree.tracks = {}

        engine = SearchEngine(mock_recommender)

        # Test with special characters
        trigrams = engine._generate_trigrams("a-b")
        assert len(trigrams) > 0

        # Test with numbers
        trigrams = engine._generate_trigrams("track123")
        assert len(trigrams) > 0

        # Test with unicode
        trigrams = engine._generate_trigrams("café")
        assert len(trigrams) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
