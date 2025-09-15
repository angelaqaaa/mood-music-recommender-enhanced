"""
Test suite for search functionality.

Tests core search features including exact matching, fuzzy matching,
and basic performance characteristics.
"""

# Add src to path for imports
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import time
import unittest
from unittest.mock import MagicMock, Mock, patch

from musicrec.ui.search import SearchEngine


class TestSearchFunctionality(unittest.TestCase):
    """Test core search functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock recommender with sample data
        self.mock_recommender = Mock()
        self.mock_recommender.genre_tree.tracks = {
            "track1": Mock(
                data={"track_name": "Shape of You", "artist_name": "Ed Sheeran"}
            ),
            "track2": Mock(
                data={"track_name": "Blinding Lights", "artist_name": "The Weeknd"}
            ),
            "track3": Mock(
                data={"track_name": "Watermelon Sugar", "artist_name": "Harry Styles"}
            ),
            "track4": Mock(
                data={"track_name": "Don't Start Now", "artist_name": "Dua Lipa"}
            ),
            "track5": Mock(
                data={"track_name": "Levitating", "artist_name": "Dua Lipa"}
            ),
        }

        # Create search engine with default settings
        self.search_engine = SearchEngine(
            self.mock_recommender, enable_fuzzy=True, fuzzy_threshold=0.6
        )

    def test_exact_match_search(self):
        """Test exact string matching."""
        results = self.search_engine.search_tracks("Shape")

        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["track_name"], "Shape of You")
        self.assertEqual(results[0]["match_type"], "exact")

    def test_artist_name_search(self):
        """Test searching by artist name."""
        results = self.search_engine.search_tracks("Dua")

        self.assertEqual(len(results), 2)
        for result in results:
            self.assertEqual(result["artist_name"], "Dua Lipa")

    def test_case_insensitive_search(self):
        """Test case-insensitive searching."""
        results_lower = self.search_engine.search_tracks("shape")
        results_upper = self.search_engine.search_tracks("SHAPE")
        results_mixed = self.search_engine.search_tracks("ShApE")

        self.assertEqual(len(results_lower), len(results_upper))
        self.assertEqual(len(results_upper), len(results_mixed))
        self.assertGreater(len(results_lower), 0)

    def test_minimum_query_length(self):
        """Test minimum query length requirement."""
        results = self.search_engine.search_tracks("ab")  # Too short
        self.assertEqual(len(results), 0)

        results = self.search_engine.search_tracks("abc")  # Just right
        # Results depend on matches, but shouldn't error

    def test_max_results_limit(self):
        """Test maximum results limit."""
        # Create search engine with small max_results
        limited_engine = SearchEngine(
            self.mock_recommender, max_results=2, enable_fuzzy=True
        )

        # Search for something that matches multiple tracks
        results = limited_engine.search_tracks("a")  # Should match multiple
        self.assertLessEqual(len(results), 2)

    def test_empty_query_handling(self):
        """Test handling of empty queries."""
        results = self.search_engine.search_tracks("")
        self.assertEqual(len(results), 0)

        results = self.search_engine.search_tracks("   ")  # Whitespace only
        self.assertEqual(len(results), 0)

    def test_no_matches_found(self):
        """Test handling when no matches are found."""
        results = self.search_engine.search_tracks("xyzzzzz")
        self.assertEqual(len(results), 0)

    def test_result_structure(self):
        """Test the structure of search results."""
        results = self.search_engine.search_tracks("Shape")

        self.assertGreater(len(results), 0)
        result = results[0]

        # Check required fields
        self.assertIn("track_id", result)
        self.assertIn("track_name", result)
        self.assertIn("artist_name", result)
        self.assertIn("display_name", result)
        self.assertIn("score", result)
        self.assertIn("match_type", result)

        # Check score is valid
        self.assertIsInstance(result["score"], float)
        self.assertGreaterEqual(result["score"], 0.0)
        self.assertLessEqual(result["score"], 1.0)

    def test_score_ordering(self):
        """Test that results are ordered by score (descending)."""
        results = self.search_engine.search_tracks("a")  # Get multiple results

        if len(results) > 1:
            for i in range(1, len(results)):
                self.assertGreaterEqual(
                    results[i - 1]["score"],
                    results[i]["score"],
                    "Results should be ordered by score descending",
                )

    def test_display_name_format(self):
        """Test display name formatting."""
        results = self.search_engine.search_tracks("Shape")

        self.assertGreater(len(results), 0)
        result = results[0]

        expected_format = f"{result['track_name']} - {result['artist_name']}"
        self.assertEqual(result["display_name"], expected_format)


class TestFuzzyMatching(unittest.TestCase):
    """Test fuzzy matching functionality."""

    def setUp(self):
        """Set up test fixtures for fuzzy matching."""
        self.mock_recommender = Mock()
        self.mock_recommender.genre_tree.tracks = {
            "track1": Mock(
                data={"track_name": "Shape of You", "artist_name": "Ed Sheeran"}
            ),
            "track2": Mock(
                data={"track_name": "Blinding Lights", "artist_name": "The Weeknd"}
            ),
            "track3": Mock(
                data={"track_name": "Watermelon Sugar", "artist_name": "Harry Styles"}
            ),
        }

    def test_trigram_fuzzy_matching(self):
        """Test trigram-based fuzzy matching."""
        search_engine = SearchEngine(
            self.mock_recommender,
            enable_fuzzy=True,
            fuzzy_method="trigram",
            fuzzy_threshold=0.3,
        )

        # Test with typo
        results = search_engine.search_tracks("Shap")  # Missing 'e'
        self.assertGreater(len(results), 0)

        # Should find "Shape of You"
        found_shape = any(r["track_name"] == "Shape of You" for r in results)
        self.assertTrue(found_shape)

    def test_difflib_fuzzy_matching(self):
        """Test difflib-based fuzzy matching."""
        search_engine = SearchEngine(
            self.mock_recommender,
            enable_fuzzy=True,
            fuzzy_method="difflib",
            fuzzy_threshold=0.6,
        )

        # Test with typo
        results = search_engine.search_tracks("Blindng")  # Missing 'i'
        self.assertGreater(len(results), 0)

    def test_fuzzy_threshold_filtering(self):
        """Test that fuzzy threshold filters out poor matches."""
        high_threshold_engine = SearchEngine(
            self.mock_recommender,
            enable_fuzzy=True,
            fuzzy_threshold=0.9,  # Very high threshold
        )

        low_threshold_engine = SearchEngine(
            self.mock_recommender,
            enable_fuzzy=True,
            fuzzy_threshold=0.3,  # Low threshold
        )

        # Test with significant typo
        query = "Shp"  # Very different from "Shape"

        high_results = high_threshold_engine.search_tracks(query)
        low_results = low_threshold_engine.search_tracks(query)

        # Low threshold should find more matches
        self.assertGreaterEqual(len(low_results), len(high_results))

    def test_fuzzy_disabled(self):
        """Test behavior when fuzzy matching is disabled."""
        search_engine = SearchEngine(self.mock_recommender, enable_fuzzy=False)

        # Exact match should work
        exact_results = search_engine.search_tracks("Shape")
        self.assertGreater(len(exact_results), 0)

        # Typo should not work with fuzzy disabled
        typo_results = search_engine.search_tracks("Shap")
        # Should only find exact/substring matches, not fuzzy


if __name__ == "__main__":
    unittest.main()
