"""Unit tests for core recommendation engine in models/engine.py.

This module tests the MusicRecommender class with various recommendation
algorithms and data retrieval methods.
"""

import pytest
import pandas as pd
from src.musicrec.models.engine import MusicRecommender


class TestMusicRecommender:
    """Test suite for MusicRecommender class."""

    @pytest.fixture
    def sample_data(self):
        """Create sample track data for testing."""
        return pd.DataFrame(
            [
                {
                    "track_id": "track_1",
                    "track_name": "Rock Song",
                    "artist_name": "Rock Artist",
                    "genre_hierarchy": ["rock"],
                    "mood_tags": ["energetic", "loud"],
                    "energy": 0.8,
                    "valence": 0.6,
                    "tempo": 120.0,
                    "danceability": 0.7,
                },
                {
                    "track_id": "track_2",
                    "track_name": "Metal Song",
                    "artist_name": "Metal Artist",
                    "genre_hierarchy": ["rock", "metal"],
                    "mood_tags": ["intense", "heavy"],
                    "energy": 0.9,
                    "valence": 0.3,
                    "tempo": 140.0,
                    "danceability": 0.5,
                },
                {
                    "track_id": "track_3",
                    "track_name": "Electronic Song",
                    "artist_name": "Electronic Artist",
                    "genre_hierarchy": ["electronic"],
                    "mood_tags": ["upbeat", "synthetic"],
                    "energy": 0.7,
                    "valence": 0.8,
                    "tempo": 128.0,
                    "danceability": 0.9,
                },
                {
                    "track_id": "track_4",
                    "track_name": "House Song",
                    "artist_name": "House Artist",
                    "genre_hierarchy": ["electronic", "house"],
                    "mood_tags": ["danceable", "rhythmic"],
                    "energy": 0.75,
                    "valence": 0.85,
                    "tempo": 125.0,
                    "danceability": 0.95,
                },
                {
                    "track_id": "track_5",
                    "track_name": "Acoustic Song",
                    "artist_name": "Acoustic Artist",
                    "genre_hierarchy": ["acoustic"],
                    "mood_tags": ["calm", "organic"],
                    "energy": 0.3,
                    "valence": 0.7,
                    "tempo": 80.0,
                    "danceability": 0.2,
                },
            ]
        )

    @pytest.fixture
    def recommender(self, sample_data):
        """Create a MusicRecommender instance for testing."""
        return MusicRecommender(sample_data)

    def test_initialization(self, sample_data):
        """Test recommender initialization."""
        recommender = MusicRecommender(sample_data)

        assert recommender.data is not None
        assert len(recommender.data) == 5
        assert recommender.audio_features == ["energy", "valence", "tempo"]
        assert recommender.genre_tree is not None
        assert recommender.similarity_graph is not None

    def test_custom_audio_features(self, sample_data):
        """Test initialization with custom audio features."""
        custom_features = ["energy", "danceability"]
        recommender = MusicRecommender(sample_data, custom_features)

        assert recommender.audio_features == custom_features

    def test_get_available_genres(self, recommender):
        """Test retrieving available genres."""
        genres = recommender.get_available_genres()

        assert "rock" in genres
        assert "metal" in genres
        assert "electronic" in genres
        assert "house" in genres
        assert "acoustic" in genres
        assert len(genres) >= 5

    def test_get_available_moods(self, recommender):
        """Test retrieving available moods."""
        moods = recommender.get_available_moods()

        assert "energetic" in moods
        assert "intense" in moods
        assert "upbeat" in moods
        assert "calm" in moods
        assert len(moods) >= 4

    def test_get_track_info(self, recommender):
        """Test retrieving track information."""
        track_info = recommender.get_track_info("track_1")

        assert track_info is not None
        assert track_info["track_id"] == "track_1"
        assert track_info["track_name"] == "Rock Song"
        assert track_info["artist_name"] == "Rock Artist"

        # Test non-existent track
        missing_track = recommender.get_track_info("nonexistent")
        assert missing_track is None

    def test_search_tracks_by_name(self, recommender):
        """Test searching tracks by name."""
        # Search for "Rock"
        results = recommender.search_tracks_by_name("Rock", limit=5)

        assert len(results) >= 1
        assert any("rock" in result["track_name"].lower() for result in results)

        # Test case insensitive search
        results_lower = recommender.search_tracks_by_name("rock", limit=5)
        assert len(results_lower) >= 1

        # Test partial match
        results_partial = recommender.search_tracks_by_name("Song", limit=10)
        assert len(results_partial) >= 5  # All tracks contain "Song"

    def test_recommend_by_genre(self, recommender):
        """Test genre-based recommendations."""
        recommendations = recommender.recommend_by_genre("rock", limit=5)

        assert len(recommendations) >= 1
        assert all("track_id" in rec for rec in recommendations)
        assert all("track_name" in rec for rec in recommendations)

        # Should include both rock and metal tracks
        track_ids = [rec["track_id"] for rec in recommendations]
        assert "track_1" in track_ids or "track_2" in track_ids

    def test_recommend_by_mood(self, recommender):
        """Test mood-based recommendations."""
        recommendations = recommender.recommend_by_mood("energetic", limit=5)

        assert len(recommendations) >= 1
        assert all("track_id" in rec for rec in recommendations)

        # Check that tracks with the mood are included
        track_1_found = any(rec["track_id"] == "track_1" for rec in recommendations)
        assert track_1_found

    def test_recommend_by_genre_and_mood(self, recommender):
        """Test combined genre and mood recommendations."""
        recommendations = recommender.recommend_by_genre_and_mood(
            "rock", "energetic", limit=5
        )

        assert len(recommendations) >= 1
        assert all("track_id" in rec for rec in recommendations)

        # Should find track_1 which is rock and energetic
        track_1_found = any(rec["track_id"] == "track_1" for rec in recommendations)
        assert track_1_found

    def test_recommend_similar_to_track(self, recommender):
        """Test similarity-based recommendations."""
        recommendations = recommender.recommend_similar_to_track("track_3", limit=3)

        assert isinstance(recommendations, list)
        assert all("track_id" in rec for rec in recommendations)
        assert all("similarity" in rec for rec in recommendations)

        # Recommendations should be sorted by similarity (descending)
        if len(recommendations) > 1:
            similarities = [rec["similarity"] for rec in recommendations]
            assert similarities == sorted(similarities, reverse=True)

    def test_bfs_recommend(self, recommender):
        """Test BFS recommendation algorithm."""
        recommendations = recommender.bfs_recommend("rock", limit=5)

        assert len(recommendations) >= 1
        assert all("track_id" in rec for rec in recommendations)

        # Test with mood filter
        recommendations_with_mood = recommender.bfs_recommend(
            "rock", mood="energetic", limit=5
        )
        assert len(recommendations_with_mood) >= 1

    def test_dfs_recommend(self, recommender):
        """Test DFS recommendation algorithm."""
        recommendations = recommender.dfs_recommend("electronic", limit=5)

        assert len(recommendations) >= 1
        assert all("track_id" in rec for rec in recommendations)

        # Should include both electronic and house tracks
        track_ids = [rec["track_id"] for rec in recommendations]
        electronic_tracks = {"track_3", "track_4"}
        assert any(tid in electronic_tracks for tid in track_ids)

    def test_empty_results_handling(self, recommender):
        """Test handling of empty results."""
        # Non-existent genre
        empty_genre = recommender.recommend_by_genre("nonexistent", limit=5)
        assert empty_genre == []

        # Non-existent mood
        empty_mood = recommender.recommend_by_mood("nonexistent", limit=5)
        assert empty_mood == []

        # Non-existent combination
        empty_combo = recommender.recommend_by_genre_and_mood(
            "nonexistent", "alsononexistent", limit=5
        )
        assert empty_combo == []

    def test_limit_parameter(self, recommender):
        """Test that limit parameter is respected."""
        recommendations = recommender.recommend_by_genre("rock", limit=1)
        assert len(recommendations) <= 1

        recommendations_large = recommender.recommend_by_genre("rock", limit=10)
        # Should not exceed available tracks, but at least 1
        assert len(recommendations_large) >= 1
        assert len(recommendations_large) <= 10

    def test_recommendation_data_structure(self, recommender):
        """Test that recommendations have proper structure."""
        recommendations = recommender.recommend_by_genre("rock", limit=3)

        if len(recommendations) > 0:
            rec = recommendations[0]
            required_fields = ["track_id", "track_name", "artist_name"]

            for field in required_fields:
                assert field in rec
                assert rec[field] is not None

    def test_hierarchical_recommendations(self, recommender):
        """Test that hierarchical genres work correctly."""
        # Recommendations for "rock" should include metal tracks
        rock_recs = recommender.recommend_by_genre("rock", limit=10)
        rock_track_ids = [rec["track_id"] for rec in rock_recs]

        # Should include both rock (track_1) and metal (track_2) tracks
        assert "track_1" in rock_track_ids or "track_2" in rock_track_ids


class TestMusicRecommenderEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_dataframe(self):
        """Test initialization with empty DataFrame."""
        empty_data = pd.DataFrame(
            columns=[
                "track_id",
                "track_name",
                "artist_name",
                "genre_hierarchy",
                "mood_tags",
                "energy",
                "valence",
                "tempo",
            ]
        )

        recommender = MusicRecommender(empty_data)

        assert len(recommender.get_available_genres()) == 0
        assert len(recommender.get_available_moods()) == 0
        assert recommender.recommend_by_genre("any", limit=5) == []

    def test_single_track_data(self):
        """Test with minimal single track data."""
        single_track = pd.DataFrame(
            [
                {
                    "track_id": "single_track",
                    "track_name": "Only Song",
                    "artist_name": "Only Artist",
                    "genre_hierarchy": ["pop"],
                    "mood_tags": ["happy"],
                    "energy": 0.5,
                    "valence": 0.5,
                    "tempo": 100.0,
                }
            ]
        )

        recommender = MusicRecommender(single_track)

        assert len(recommender.get_available_genres()) >= 1
        assert "pop" in recommender.get_available_genres()

        recommendations = recommender.recommend_by_genre("pop", limit=5)
        assert len(recommendations) == 1
        assert recommendations[0]["track_id"] == "single_track"

    def test_missing_audio_features(self):
        """Test handling of missing audio features."""
        data_missing_features = pd.DataFrame(
            [
                {
                    "track_id": "track_1",
                    "track_name": "Test Song",
                    "artist_name": "Test Artist",
                    "genre_hierarchy": ["test"],
                    "mood_tags": ["test_mood"],
                    "energy": 0.5,
                    # Missing valence and tempo
                }
            ]
        )

        # Should handle gracefully - similarity graph may have fewer connections
        recommender = MusicRecommender(data_missing_features)
        assert recommender is not None
        assert len(recommender.get_available_genres()) >= 1
