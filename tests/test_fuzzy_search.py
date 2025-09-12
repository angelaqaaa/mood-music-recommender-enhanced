"""CSC111 Winter 2025: A Mood-Driven Music Recommender with Genre Hierarchies

Test suite for fuzzy search functionality including typo tolerance, ranking,
and performance validation.

Copyright and Usage Information
===============================
This file is Copyright (c) 2025 Qian (Angela) Su.
"""

import pytest
import time
from unittest.mock import Mock
from src.musicrec.ui.search import SearchEngine


class TestFuzzySearchEngine:
    """Test suite for fuzzy search functionality."""

    @pytest.fixture
    def mock_recommender_with_typo_data(self):
        """Create a mock recommender with data suitable for fuzzy testing."""
        recommender = Mock()

        mock_tracks = {
            "track1": Mock(
                data={"track_name": "Bohemian Rhapsody", "artist_name": "Queen"}
            ),
            "track2": Mock(
                data={"track_name": "Hotel California", "artist_name": "Eagles"}
            ),
            "track3": Mock(
                data={"track_name": "Stairway to Heaven", "artist_name": "Led Zeppelin"}
            ),
            "track4": Mock(
                data={
                    "track_name": "Another Brick in the Wall",
                    "artist_name": "Pink Floyd",
                }
            ),
            "track5": Mock(
                data={
                    "track_name": "Sweet Child O' Mine",
                    "artist_name": "Guns N' Roses",
                }
            ),
        }

        recommender.genre_tree.tracks = mock_tracks

        def mock_get_track_info(track_id):
            track_data = mock_tracks.get(track_id)
            if track_data:
                return {
                    "track_name": track_data.data["track_name"],
                    "artist_name": track_data.data["artist_name"],
                    "genre_path": ["rock", "classic rock"],
                    "mood_tags": ["energetic", "uplifting"],
                }
            return None

        recommender.get_track_info = mock_get_track_info
        return recommender

    def test_fuzzy_search_disabled_by_default(self, mock_recommender_with_typo_data):
        """Test that fuzzy search is disabled by default."""
        engine = SearchEngine(mock_recommender_with_typo_data)
        assert not engine.is_fuzzy_enabled()

        # With fuzzy disabled, typos should not match
        results = engine.search_tracks("bohemiam")  # Typo: missing 'n'
        assert len(results) == 0

    def test_fuzzy_search_enabled(self, mock_recommender_with_typo_data):
        """Test that fuzzy search can be enabled."""
        engine = SearchEngine(mock_recommender_with_typo_data, enable_fuzzy=True)
        assert engine.is_fuzzy_enabled()

    def test_exact_match_beats_fuzzy_match(self, mock_recommender_with_typo_data):
        """Test that exact matches rank higher than fuzzy matches."""
        engine = SearchEngine(
            mock_recommender_with_typo_data, enable_fuzzy=True, fuzzy_threshold=0.5
        )

        # Add a track that would fuzzy-match but exact match should win
        mock_recommender_with_typo_data.genre_tree.tracks["track6"] = Mock(
            data={
                "track_name": "Queen",  # Exact match for "Queen"
                "artist_name": "Various Artists",
            }
        )

        results = engine.search_tracks("queen")

        # Should have results
        assert len(results) > 0

        # First result should be exact match (track with "Queen" in name or the artist "Queen")
        top_result = results[0]
        has_exact_match = (
            "queen" in top_result["track_name"].lower()
            or "queen" in top_result["artist_name"].lower()
        )
        assert has_exact_match

        # Exact match should have higher score than any fuzzy match
        if len(results) > 1:
            assert results[0]["match_score"] > results[1]["match_score"]

    def test_typo_tolerance(self, mock_recommender_with_typo_data):
        """Test that fuzzy search handles common typos."""
        engine = SearchEngine(
            mock_recommender_with_typo_data, enable_fuzzy=True, fuzzy_threshold=0.5
        )

        # Test various typo scenarios
        typo_tests = [
            ("bohemiam", "Bohemian Rhapsody"),  # Missing letter
            ("califronia", "Hotel California"),  # Misspelled
            ("stariway", "Stairway to Heaven"),  # Letter substitution
            ("qeen", "Queen"),  # Missing letter in artist
        ]

        for typo, expected_match in typo_tests:
            results = engine.search_tracks(typo)

            # Should find at least one result
            assert len(results) > 0, f"No results found for typo: {typo}"

            # Should contain the expected track
            found_expected = any(
                expected_match.lower() in result["track_name"].lower()
                or expected_match.lower() in result["artist_name"].lower()
                for result in results
            )
            assert (
                found_expected
            ), f"Expected '{expected_match}' not found in results for typo '{typo}'"

    def test_partial_match_behavior(self, mock_recommender_with_typo_data):
        """Test fuzzy matching with partial queries."""
        engine = SearchEngine(
            mock_recommender_with_typo_data, enable_fuzzy=True, fuzzy_threshold=0.4
        )

        # Test partial matches that should work with fuzzy
        results = engine.search_tracks("bohemia")  # Partial of "Bohemian"
        assert len(results) > 0

        # Should find Bohemian Rhapsody
        found_bohemian = any(
            "bohemian" in result["track_name"].lower() for result in results
        )
        assert found_bohemian

    def test_fuzzy_similarity_calculation(self, mock_recommender_with_typo_data):
        """Test the fuzzy similarity calculation method."""
        engine = SearchEngine(mock_recommender_with_typo_data, enable_fuzzy=True)

        # Test exact match
        assert engine._fuzzy_similarity("queen", "queen") == 1.0

        # Test complete mismatch
        assert engine._fuzzy_similarity("abc", "xyz") < 0.3

        # Test similar strings
        similarity = engine._fuzzy_similarity("queen", "qeen")
        assert 0.7 < similarity < 1.0  # Should be high but not perfect

        # Test empty strings
        assert engine._fuzzy_similarity("", "") == 0.0
        assert engine._fuzzy_similarity("test", "") == 0.0
        assert engine._fuzzy_similarity("", "test") == 0.0

    def test_fuzzy_threshold_filtering(self, mock_recommender_with_typo_data):
        """Test that fuzzy threshold properly filters results."""
        # High threshold should be more strict
        strict_engine = SearchEngine(
            mock_recommender_with_typo_data, enable_fuzzy=True, fuzzy_threshold=0.8
        )
        strict_results = strict_engine.search_tracks("xyz123")  # Very different query

        # Loose threshold should be more permissive
        loose_engine = SearchEngine(
            mock_recommender_with_typo_data, enable_fuzzy=True, fuzzy_threshold=0.3
        )
        loose_results = loose_engine.search_tracks("xyz123")

        # Loose threshold should return more results
        assert len(loose_results) >= len(strict_results)

    def test_edge_cases(self, mock_recommender_with_typo_data):
        """Test edge cases for fuzzy search."""
        engine = SearchEngine(mock_recommender_with_typo_data, enable_fuzzy=True)

        # Empty query
        results = engine.search_tracks("")
        assert len(results) == 0

        # Very short query (below minimum length)
        results = engine.search_tracks("a")
        assert len(results) == 0

        results = engine.search_tracks("ab")
        assert len(results) == 0

        # Query at minimum length
        results = engine.search_tracks("abc")
        assert isinstance(results, list)  # Should not crash

    def test_non_ascii_characters(self, mock_recommender_with_typo_data):
        """Test fuzzy search with non-ASCII characters."""
        # Add a track with accented characters
        mock_recommender_with_typo_data.genre_tree.tracks["track7"] = Mock(
            data={"track_name": "Café de la Paix", "artist_name": "Édith Piaf"}
        )

        engine = SearchEngine(
            mock_recommender_with_typo_data, enable_fuzzy=True, fuzzy_threshold=0.6
        )

        # Should handle non-ASCII input gracefully
        results = engine.search_tracks("cafe")
        assert isinstance(results, list)  # Should not crash

        results = engine.search_tracks("edith")
        assert isinstance(results, list)  # Should not crash

    def test_performance_benchmark(self, mock_recommender_with_typo_data):
        """Test that fuzzy search completes within reasonable time."""
        engine = SearchEngine(
            mock_recommender_with_typo_data, enable_fuzzy=True, fuzzy_threshold=0.6
        )

        # Test with various query lengths
        queries = ["abc", "queen", "bohemian", "stairway to heaven"]

        for query in queries:
            start_time = time.perf_counter()
            results = engine.search_tracks(query)
            end_time = time.perf_counter()

            execution_time_ms = (end_time - start_time) * 1000

            # Should complete within a few milliseconds on small dataset
            assert (
                execution_time_ms < 50
            ), f"Query '{query}' took {execution_time_ms:.2f}ms, too slow"
            assert isinstance(results, list)


class TestFuzzySearchIntegration:
    """Integration tests for fuzzy search with larger datasets."""

    def test_larger_dataset_performance(self):
        """Test fuzzy search performance with a larger mock dataset."""
        mock_recommender = Mock()

        # Create a larger dataset
        mock_tracks = {}
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
        ] * 10  # Multiply to create larger dataset

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
        ] * 10

        for i, (track_name, artist) in enumerate(zip(track_names, artists)):
            mock_tracks[f"track{i}"] = Mock(
                data={
                    "track_name": f"{track_name} {i//10}",  # Add variation
                    "artist_name": artist,
                }
            )

        mock_recommender.genre_tree.tracks = mock_tracks

        def mock_get_track_info(track_id):
            return {"genre_path": ["rock"], "mood_tags": ["energetic"]}

        mock_recommender.get_track_info = mock_get_track_info

        engine = SearchEngine(
            mock_recommender, enable_fuzzy=True, fuzzy_threshold=0.5, max_results=20
        )

        # Test performance with larger dataset
        start_time = time.perf_counter()
        results = engine.search_tracks("qeen")  # Typo that should match "Queen" artist
        end_time = time.perf_counter()

        execution_time_ms = (end_time - start_time) * 1000

        # Should still be reasonably fast
        assert (
            execution_time_ms < 100
        ), f"Large dataset search took {execution_time_ms:.2f}ms, too slow"
        assert len(results) <= 20  # Should respect max_results
        assert len(results) > 0  # Should find fuzzy matches


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
