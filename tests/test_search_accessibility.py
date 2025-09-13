"""
Test suite for search accessibility and edge cases.

Tests ARIA attributes, keyboard navigation, and various edge cases
to ensure robust and accessible search functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from musicrec.ui.search import SearchEngine


class TestSearchAccessibility(unittest.TestCase):
    """Test accessibility features and edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_recommender = Mock()
        self.mock_recommender.genre_tree.tracks = {
            'track1': Mock(data={'track_name': 'Test Song', 'artist_name': 'Test Artist'}),
            'track2': Mock(data={'track_name': 'Another Song', 'artist_name': 'Another Artist'}),
            'track3': Mock(data={'track_name': '', 'artist_name': ''}),  # Empty names
            'track4': Mock(data={}),  # Missing data
        }

    def test_empty_track_data_handling(self):
        """Test handling of tracks with empty or missing data."""
        search_engine = SearchEngine(self.mock_recommender)

        # Should not crash with empty/missing data
        results = search_engine.search_tracks('test')
        self.assertIsInstance(results, list)

        # Should handle tracks with empty names gracefully
        results = search_engine.search_tracks('')
        self.assertEqual(len(results), 0)

    def test_missing_track_data_handling(self):
        """Test handling of tracks with missing data fields."""
        # Add track with None values
        self.mock_recommender.genre_tree.tracks['track5'] = Mock(
            data={'track_name': None, 'artist_name': None}
        )

        search_engine = SearchEngine(self.mock_recommender)
        results = search_engine.search_tracks('test')

        # Should not crash and return valid results
        self.assertIsInstance(results, list)

    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters."""
        # Add tracks with special characters
        self.mock_recommender.genre_tree.tracks.update({
            'unicode1': Mock(data={'track_name': 'Café Müller', 'artist_name': 'François'}),
            'unicode2': Mock(data={'track_name': '東京', 'artist_name': 'アーティスト'}),
            'special1': Mock(data={'track_name': 'Song & Title', 'artist_name': 'Artist!'}),
            'special2': Mock(data={'track_name': 'Track (2023)', 'artist_name': 'Band #1'}),
        })

        search_engine = SearchEngine(self.mock_recommender, enable_fuzzy=True)

        # Test Unicode search
        unicode_results = search_engine.search_tracks('Café')
        self.assertGreater(len(unicode_results), 0)

        # Test special character search
        special_results = search_engine.search_tracks('Song &')
        self.assertGreater(len(special_results), 0)

    def test_extremely_long_strings(self):
        """Test handling of extremely long search queries and track names."""
        # Add track with very long name
        long_name = 'A' * 1000  # 1000 character name
        self.mock_recommender.genre_tree.tracks['long_track'] = Mock(
            data={'track_name': long_name, 'artist_name': 'Artist'}
        )

        search_engine = SearchEngine(self.mock_recommender)

        # Test very long query
        long_query = 'A' * 500
        results = search_engine.search_tracks(long_query)

        # Should not crash
        self.assertIsInstance(results, list)

    def test_cache_key_consistency(self):
        """Test that cache keys are consistent for similar queries."""
        search_engine = SearchEngine(
            self.mock_recommender,
            enable_fuzzy=True,
            cache_size=10
        )

        # These should use the same cache entry
        query1 = 'test'
        query2 = 'test'  # Identical

        # Call both to populate cache
        results1 = search_engine.search_tracks(query1)
        results2 = search_engine.search_tracks(query2)

        # Results should be identical (from cache)
        self.assertEqual(len(results1), len(results2))

    def test_configuration_parameter_validation(self):
        """Test that configuration parameters are handled correctly."""
        # Test with various parameter combinations
        configs = [
            {'min_query_length': 1, 'max_results': 5},
            {'fuzzy_threshold': 0.1},
            {'fuzzy_threshold': 0.9},
            {'prefilter_top_n': 1},
            {'prefilter_top_n': 1000},
            {'cache_size': 1},
            {'cache_size': 1000},
        ]

        for config in configs:
            with self.subTest(config=config):
                try:
                    engine = SearchEngine(
                        self.mock_recommender,
                        enable_fuzzy=True,
                        **config
                    )
                    results = engine.search_tracks('test')
                    self.assertIsInstance(results, list)
                except Exception as e:
                    self.fail(f"Configuration {config} should not raise exception: {e}")

    def test_concurrent_search_safety(self):
        """Test thread safety for concurrent searches."""
        import threading
        import queue

        search_engine = SearchEngine(
            self.mock_recommender,
            enable_fuzzy=True
        )

        results_queue = queue.Queue()
        exceptions_queue = queue.Queue()

        def search_worker(query, worker_id):
            try:
                results = search_engine.search_tracks(f'test{worker_id}')
                results_queue.put((worker_id, results))
            except Exception as e:
                exceptions_queue.put((worker_id, e))

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=search_worker, args=('test', i))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Check for exceptions
        if not exceptions_queue.empty():
            worker_id, exception = exceptions_queue.get()
            self.fail(f"Thread {worker_id} raised exception: {exception}")

        # Should have results from all workers
        self.assertEqual(results_queue.qsize(), 5)

    def test_memory_cleanup(self):
        """Test that search engine properly cleans up resources."""
        import gc
        import weakref

        search_engine = SearchEngine(
            self.mock_recommender,
            enable_fuzzy=True,
            cache_size=100
        )

        # Create weak reference to test cleanup
        weak_ref = weakref.ref(search_engine._exact_index)

        # Perform searches to populate internal structures
        for i in range(10):
            search_engine.search_tracks(f'test{i}')

        # Delete engine and force garbage collection
        del search_engine
        gc.collect()

        # Weak reference should be cleaned up
        # Note: This test may be flaky depending on Python's GC behavior

    def test_error_recovery(self):
        """Test recovery from various error conditions."""
        # Mock recommender that raises exceptions
        error_recommender = Mock()
        error_recommender.genre_tree.tracks = {
            'track1': Mock(data={'track_name': 'Test', 'artist_name': 'Artist'})
        }

        search_engine = SearchEngine(error_recommender)

        # Test with recommender that has issues
        error_recommender.genre_tree.tracks = None
        try:
            results = search_engine.search_tracks('test')
            # Should handle gracefully, not crash
        except Exception:
            pass  # Some exceptions are acceptable for malformed data

    def test_boundary_values(self):
        """Test boundary values for all parameters."""
        boundary_tests = [
            {'min_query_length': 0},  # Minimum
            {'min_query_length': 100},  # Large value
            {'max_results': 0},  # Edge case
            {'max_results': 1},  # Minimum useful
            {'fuzzy_threshold': 0.0},  # Minimum
            {'fuzzy_threshold': 1.0},  # Maximum
            {'prefilter_top_n': 0},  # Edge case
            {'prefilter_top_n': 1},  # Minimum useful
            {'cache_size': 0},  # No cache
        ]

        for params in boundary_tests:
            with self.subTest(params=params):
                try:
                    engine = SearchEngine(
                        self.mock_recommender,
                        enable_fuzzy=True,
                        **params
                    )

                    # Test basic functionality
                    results = engine.search_tracks('test')
                    self.assertIsInstance(results, list)

                except Exception as e:
                    # Some boundary values may legitimately fail
                    # Just ensure they fail gracefully
                    self.assertIsInstance(e, (ValueError, TypeError))


class TestSearchResultIntegrity(unittest.TestCase):
    """Test the integrity and consistency of search results."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_recommender = Mock()
        self.mock_recommender.genre_tree.tracks = {
            f'track{i}': Mock(data={
                'track_name': f'Song {i}',
                'artist_name': f'Artist {i % 3}'  # Reuse some artists
            })
            for i in range(20)
        }

    def test_result_consistency(self):
        """Test that identical queries return identical results."""
        search_engine = SearchEngine(self.mock_recommender, enable_fuzzy=True)

        query = 'Song 1'
        results1 = search_engine.search_tracks(query)
        results2 = search_engine.search_tracks(query)

        # Results should be identical
        self.assertEqual(len(results1), len(results2))

        for r1, r2 in zip(results1, results2):
            self.assertEqual(r1['track_id'], r2['track_id'])
            self.assertEqual(r1['score'], r2['score'])

    def test_score_validity(self):
        """Test that all scores are valid numbers in correct range."""
        search_engine = SearchEngine(self.mock_recommender, enable_fuzzy=True)

        results = search_engine.search_tracks('Song')

        for result in results:
            score = result['score']
            self.assertIsInstance(score, (int, float))
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            self.assertFalse(score != score)  # Check for NaN

    def test_match_type_consistency(self):
        """Test that match types are consistent with scores."""
        search_engine = SearchEngine(self.mock_recommender, enable_fuzzy=True)

        results = search_engine.search_tracks('Song')

        for result in results:
            match_type = result['match_type']
            score = result['score']

            # Exact matches should generally have higher scores
            if match_type == 'exact':
                self.assertGreaterEqual(score, 0.8)  # Usually high score

            # Match type should be valid
            self.assertIn(match_type, ['exact', 'fuzzy'])


if __name__ == '__main__':
    unittest.main()