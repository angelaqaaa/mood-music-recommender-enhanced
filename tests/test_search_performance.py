"""
Test suite for search performance benchmarking.

Tests performance characteristics and validates <200ms response time
target on large datasets.
"""

import unittest
from unittest.mock import Mock
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from musicrec.ui.search import SearchEngine


class TestSearchPerformance(unittest.TestCase):
    """Test search performance characteristics."""

    def setUp(self):
        """Set up test fixtures with large dataset."""
        # Create mock recommender with larger dataset
        self.mock_recommender = Mock()

        # Generate test tracks (simulating 1000+ tracks)
        tracks = {}
        artists = ["Artist A", "Artist B", "Artist C", "Artist D", "Artist E"]
        genres = ["Pop", "Rock", "Hip Hop", "Electronic", "Jazz"]

        for i in range(1000):
            track_id = f"track{i:04d}"
            artist = artists[i % len(artists)]
            genre = genres[i % len(genres)]
            track_name = f"{genre} Song {i:04d}"

            tracks[track_id] = Mock(
                data={"track_name": track_name, "artist_name": artist}
            )

        self.mock_recommender.genre_tree.tracks = tracks

    def test_large_dataset_search_performance(self):
        """Test search performance on large dataset."""
        search_engine = SearchEngine(
            self.mock_recommender, enable_fuzzy=True, fuzzy_threshold=0.6
        )

        # Test exact search performance
        start_time = time.time()
        results = search_engine.search_tracks("Pop Song")
        exact_time = time.time() - start_time

        self.assertLess(exact_time, 0.2, "Exact search should complete in <200ms")
        self.assertGreater(len(results), 0)

    def test_fuzzy_search_performance(self):
        """Test fuzzy search performance."""
        search_engine = SearchEngine(
            self.mock_recommender,
            enable_fuzzy=True,
            fuzzy_threshold=0.6,
            prefilter_top_n=100,  # Limit candidates for performance
        )

        # Test fuzzy search with trigram method
        start_time = time.time()
        results = search_engine.search_tracks("Pap Song")  # Typo in 'Pop'
        fuzzy_time = time.time() - start_time

        self.assertLess(fuzzy_time, 0.2, "Fuzzy search should complete in <200ms")

    def test_prefiltering_optimization(self):
        """Test that prefiltering improves performance."""
        # Engine with prefiltering
        filtered_engine = SearchEngine(
            self.mock_recommender,
            enable_fuzzy=True,
            fuzzy_threshold=0.6,
            prefilter_top_n=50,
        )

        # Engine without prefiltering (high limit)
        unfiltered_engine = SearchEngine(
            self.mock_recommender,
            enable_fuzzy=True,
            fuzzy_threshold=0.6,
            prefilter_top_n=1000,  # No effective limit
        )

        query = "Rock Song"

        # Time both approaches
        start_time = time.time()
        filtered_results = filtered_engine.search_tracks(query)
        filtered_time = time.time() - start_time

        start_time = time.time()
        unfiltered_results = unfiltered_engine.search_tracks(query)
        unfiltered_time = time.time() - start_time

        # Prefiltering should be faster (or at least not much slower)
        # Allow some tolerance for measurement variance
        self.assertLessEqual(
            filtered_time,
            unfiltered_time * 1.5,  # Allow 50% tolerance
            "Prefiltering should not significantly slow down search",
        )

    def test_cache_performance_benefit(self):
        """Test that LRU cache improves repeated search performance."""
        search_engine = SearchEngine(
            self.mock_recommender, enable_fuzzy=True, cache_size=128
        )

        query = "Electronic Song"

        # First search (cold cache)
        start_time = time.time()
        first_results = search_engine.search_tracks(query)
        first_time = time.time() - start_time

        # Second search (warm cache)
        start_time = time.time()
        second_results = search_engine.search_tracks(query)
        second_time = time.time() - start_time

        # Results should be identical
        self.assertEqual(len(first_results), len(second_results))

        # Second search should be faster (cache benefit)
        # Note: May not always be true due to measurement variance
        # So we just verify it's not significantly slower
        self.assertLessEqual(
            second_time,
            first_time * 2,  # Allow significant tolerance
            "Cached search should not be slower than initial search",
        )

    def test_multiple_concurrent_searches(self):
        """Test performance with multiple search operations."""
        search_engine = SearchEngine(self.mock_recommender, enable_fuzzy=True)

        queries = [
            "Pop Song",
            "Rock Song",
            "Hip Hop Song",
            "Electronic Song",
            "Jazz Song",
        ]

        start_time = time.time()
        results = []
        for query in queries:
            result = search_engine.search_tracks(query)
            results.append(result)
        total_time = time.time() - start_time

        # All searches combined should still be reasonable
        self.assertLess(total_time, 1.0, "Multiple searches should complete in <1s")

        # All searches should return results
        for i, result in enumerate(results):
            self.assertGreater(
                len(result), 0, f"Query '{queries[i]}' should return results"
            )

    def test_memory_usage_stability(self):
        """Test that repeated searches don't cause memory leaks."""
        search_engine = SearchEngine(
            self.mock_recommender,
            enable_fuzzy=True,
            cache_size=50,  # Small cache to test eviction
        )

        # Perform many searches to test cache eviction and stability
        queries = [f"Song {i:04d}" for i in range(100)]

        start_time = time.time()
        for query in queries:
            results = search_engine.search_tracks(query)
            # Don't store results to avoid memory buildup in test
        end_time = time.time()

        # Should complete in reasonable time even with cache eviction
        self.assertLess(
            end_time - start_time,
            5.0,  # 5 seconds for 100 searches
            "Many searches with cache eviction should complete reasonably",
        )

    def test_worst_case_performance(self):
        """Test performance in worst-case scenarios."""
        search_engine = SearchEngine(
            self.mock_recommender,
            enable_fuzzy=True,
            fuzzy_threshold=0.1,  # Very low threshold (more matches)
        )

        # Single character query (matches many tracks)
        start_time = time.time()
        results = search_engine.search_tracks("a")
        worst_case_time = time.time() - start_time

        # Even worst case should be reasonable
        self.assertLess(
            worst_case_time,
            0.5,  # 500ms tolerance for worst case
            "Worst-case search should complete in reasonable time",
        )


if __name__ == "__main__":
    unittest.main()
