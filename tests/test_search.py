"""CSC111 Winter 2025: A Mood-Driven Music Recommender with Genre Hierarchies

Test suite for search functionality including debounced search, dropdown behavior,
ARIA attributes, and selection mechanisms.

Copyright and Usage Information
===============================
This file is Copyright (c) 2025 Qian (Angela) Su.
"""

import pytest
from unittest.mock import Mock
from src.musicrec.ui.search import (
    SearchEngine,
    create_search_suggestions_html,
    generate_search_styles,
)


class TestSearchEngine:
    """Test suite for the SearchEngine class."""

    @pytest.fixture
    def mock_recommender(self):
        """Create a mock recommender with sample data."""
        recommender = Mock()

        # Mock genre_tree with sample tracks
        mock_tracks = {
            "track1": Mock(
                data={"track_name": "Bohemian Rhapsody", "artist_name": "Queen"}
            ),
            "track2": Mock(
                data={"track_name": "Stairway to Heaven", "artist_name": "Led Zeppelin"}
            ),
            "track3": Mock(
                data={"track_name": "Hotel California", "artist_name": "Eagles"}
            ),
            "track4": Mock(
                data={"track_name": "Imagine", "artist_name": "John Lennon"}
            ),
            "track5": Mock(
                data={
                    "track_name": "Another Brick in the Wall",
                    "artist_name": "Pink Floyd",
                }
            ),
        }

        recommender.genre_tree.tracks = mock_tracks

        # Mock get_track_info method
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

    @pytest.fixture
    def search_engine(self, mock_recommender):
        """Create a SearchEngine instance with mock data."""
        return SearchEngine(mock_recommender)

    def test_search_tracks_minimum_query_length(self, search_engine):
        """Test that search requires minimum query length."""
        # Empty query
        assert search_engine.search_tracks("") == []

        # Query too short
        assert search_engine.search_tracks("a") == []
        assert search_engine.search_tracks("ab") == []

        # Query at minimum length should work
        results = search_engine.search_tracks("abc")
        assert isinstance(results, list)

    def test_search_tracks_by_track_name(self, search_engine):
        """Test searching by track name."""
        # Exact match
        results = search_engine.search_tracks("Bohemian Rhapsody")
        assert len(results) >= 1
        assert any(r["track_name"] == "Bohemian Rhapsody" for r in results)

        # Partial match
        results = search_engine.search_tracks("bohemian")
        assert len(results) >= 1
        assert any(r["track_name"] == "Bohemian Rhapsody" for r in results)

        # Case insensitive
        results = search_engine.search_tracks("BOHEMIAN")
        assert len(results) >= 1
        assert any(r["track_name"] == "Bohemian Rhapsody" for r in results)

    def test_search_tracks_by_artist_name(self, search_engine):
        """Test searching by artist name."""
        # Exact match
        results = search_engine.search_tracks("Queen")
        assert len(results) >= 1
        assert any(r["artist_name"] == "Queen" for r in results)

        # Partial match
        results = search_engine.search_tracks("queen")
        assert len(results) >= 1
        assert any(r["artist_name"] == "Queen" for r in results)

    def test_search_tracks_combined_query(self, search_engine):
        """Test searching with combined track and artist names."""
        results = search_engine.search_tracks("Bohemian Queen")
        assert len(results) >= 1
        assert any(
            r["track_name"] == "Bohemian Rhapsody" and r["artist_name"] == "Queen"
            for r in results
        )

    def test_search_tracks_result_structure(self, search_engine):
        """Test that search results have the correct structure."""
        results = search_engine.search_tracks("Queen")
        assert len(results) >= 1

        result = results[0]
        required_fields = [
            "track_id",
            "track_name",
            "artist_name",
            "display_name",
            "genre_path",
            "mood_tags",
            "match_score",
        ]

        for field in required_fields:
            assert field in result

        # Test display_name format
        assert " - " in result["display_name"]
        assert result["track_name"] in result["display_name"]
        assert result["artist_name"] in result["display_name"]

    def test_search_tracks_limit_results(self, search_engine):
        """Test that search respects max_results limit."""
        # Set a small limit
        search_engine.max_results = 2

        # Search for something that might match many tracks
        results = search_engine.search_tracks("the")
        assert len(results) <= 2

    def test_search_tracks_no_results(self, search_engine):
        """Test search with no matching results."""
        results = search_engine.search_tracks("nonexistenttrack12345")
        assert results == []

    def test_fuzzy_match(self, search_engine):
        """Test fuzzy matching functionality."""
        # Test private method directly
        assert search_engine._fuzzy_match("queen rock", "queen rock music")
        assert search_engine._fuzzy_match("queen", "queen")
        assert not search_engine._fuzzy_match("xyz abc", "queen rock music")

        # Single character words should be ignored
        assert search_engine._fuzzy_match("a queen", "queen music")

    def test_calculate_match_score(self, search_engine):
        """Test match score calculation."""
        # Exact matches should have higher scores
        exact_score = search_engine._calculate_match_score("queen", "queen", "artist")
        partial_score = search_engine._calculate_match_score("que", "queen", "artist")

        assert exact_score > partial_score

        # Track name matches should score higher than artist matches
        track_score = search_engine._calculate_match_score("test", "test", "artist")
        artist_score = search_engine._calculate_match_score("test", "track", "test")

        assert track_score > artist_score

    def test_get_genre_path_and_mood_tags(self, search_engine, mock_recommender):
        """Test genre path and mood tags retrieval."""
        # Test successful retrieval
        genre_path = search_engine._get_genre_path("track1")
        mood_tags = search_engine._get_mood_tags("track1")

        assert genre_path == ["rock", "classic rock"]
        assert mood_tags == ["energetic", "uplifting"]

        # Test with nonexistent track
        genre_path = search_engine._get_genre_path("nonexistent")
        mood_tags = search_engine._get_mood_tags("nonexistent")

        assert genre_path == []
        assert mood_tags == []


class TestSearchSuggestionsHTML:
    """Test suite for search suggestions HTML generation."""

    def test_create_search_suggestions_html_empty(self):
        """Test HTML generation with empty suggestions."""
        html = create_search_suggestions_html([], "test-search")

        assert "search-suggestions empty" in html
        assert "No tracks found" in html
        assert 'role="listbox"' in html
        assert 'aria-label="No search results"' in html

    def test_create_search_suggestions_html_with_results(self):
        """Test HTML generation with search results."""
        suggestions = [
            {
                "track_id": "track1",
                "track_name": "Test Track",
                "artist_name": "Test Artist",
                "genre_path": ["rock", "alternative"],
                "mood_tags": ["energetic", "uplifting"],
            },
            {
                "track_id": "track2",
                "track_name": "Another Track",
                "artist_name": "Another Artist",
                "genre_path": ["pop"],
                "mood_tags": [],
            },
        ]

        html = create_search_suggestions_html(suggestions, "test-search")

        # Check basic structure
        assert 'class="search-suggestions"' in html
        assert 'role="listbox"' in html
        assert 'aria-label="2 search results"' in html

        # Check that both tracks are included
        assert "Test Track" in html
        assert "Test Artist" in html
        assert "Another Track" in html
        assert "Another Artist" in html

        # Check genre and mood rendering
        assert "rock› alternative" in html  # The join creates "rock› alternative"
        assert "energetic, uplifting" in html

        # Check data attributes
        assert 'data-track-id="track1"' in html
        assert 'data-track-id="track2"' in html
        assert 'data-index="0"' in html
        assert 'data-index="1"' in html


class TestSearchStyles:
    """Test suite for search CSS styles generation."""

    def test_generate_search_styles(self):
        """Test that search styles are generated properly."""
        styles = generate_search_styles()

        # Check for key CSS classes
        assert ".search-container" in styles
        assert ".search-input" in styles
        assert ".search-loading" in styles
        assert ".search-suggestions" in styles
        assert ".suggestion-item" in styles

        # Check for accessibility features
        assert "focus" in styles
        assert "aria-selected" in styles

        # Check for reduced motion support
        assert "@media (prefers-reduced-motion: reduce)" in styles

        # Check for high contrast support
        assert "@media (prefers-contrast: high)" in styles

        # Check for animations
        assert "@keyframes search-spin" in styles


class TestSearchIntegration:
    """Integration tests for search functionality."""

    def test_search_engine_initialization(self):
        """Test SearchEngine initialization with different parameters."""
        mock_recommender = Mock()
        mock_recommender.genre_tree.tracks = {}

        # Default initialization
        engine1 = SearchEngine(mock_recommender)
        assert engine1.min_query_length == 3
        assert engine1.max_results == 20

        # Custom parameters
        engine2 = SearchEngine(mock_recommender, min_query_length=2, max_results=10)
        assert engine2.min_query_length == 2
        assert engine2.max_results == 10

    def test_search_with_special_characters(self):
        """Test search functionality with special characters."""
        mock_recommender = Mock()
        mock_tracks = {
            "track1": Mock(
                data={"track_name": "Don't Stop Me Now", "artist_name": "Queen"}
            )
        }
        mock_recommender.genre_tree.tracks = mock_tracks
        mock_recommender.get_track_info = Mock(
            return_value={
                "track_name": "Don't Stop Me Now",
                "artist_name": "Queen",
                "genre_path": ["rock"],
                "mood_tags": ["happy"],
            }
        )

        engine = SearchEngine(mock_recommender)

        # Test searching with apostrophes
        results = engine.search_tracks("don't stop")
        assert len(results) >= 1
        assert any(r["track_name"] == "Don't Stop Me Now" for r in results)

    def test_search_performance(self):
        """Test search performance with larger dataset."""
        mock_recommender = Mock()

        # Create a larger mock dataset
        mock_tracks = {}
        for i in range(100):
            mock_tracks[f"track{i}"] = Mock(
                data={"track_name": f"Track {i}", "artist_name": f"Artist {i}"}
            )

        mock_recommender.genre_tree.tracks = mock_tracks
        mock_recommender.get_track_info = Mock(
            return_value={"genre_path": ["pop"], "mood_tags": ["happy"]}
        )

        engine = SearchEngine(mock_recommender)

        # Search should still be reasonably fast and limit results
        import time

        start = time.time()
        results = engine.search_tracks("track")
        end = time.time()

        # Should complete within reasonable time (adjust as needed)
        assert (end - start) < 1.0  # Less than 1 second
        assert len(results) <= engine.max_results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
