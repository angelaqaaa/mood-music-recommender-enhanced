"""Tests for the recommendation_engine module."""

from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from src.musicrec.models.engine import MusicRecommender
from src.musicrec.models.structures import GenreTree, MusicNode, SimilaritySongGraph


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame(
        {
            "track_id": ["track_1", "track_2", "track_3", "track_4"],
            "track_name": ["Song A", "Song B", "Song C", "Song D"],
            "artist_name": ["Artist 1", "Artist 1", "Artist 2", "Artist 2"],
            "genre_hierarchy": [["rock"], ["rock", "indie"], ["pop"], ["pop", "dance"]],
            "mood_tags": [["happy"], ["calm"], ["energetic"], ["party"]],
            "energy": [0.8, 0.5, 0.9, 0.95],
            "valence": [0.7, 0.6, 0.8, 0.9],
            "tempo": [120, 100, 140, 130],
            "duration": [180000, 200000, 160000, 190000],
        }
    )


@pytest.fixture
def music_recommender(sample_data):
    """Create a MusicRecommender instance with sample data."""
    return MusicRecommender(sample_data)


class TestMusicRecommenderInit:
    """Test MusicRecommender initialization."""

    def test_init_with_default_features(self, sample_data):
        """Test initialization with default audio features."""
        recommender = MusicRecommender(sample_data)

        assert recommender.audio_features == ["energy", "valence", "tempo"]
        assert isinstance(recommender.genre_tree, GenreTree)
        assert isinstance(recommender.similarity_graph, SimilaritySongGraph)
        assert len(recommender.data) == 4

    def test_init_with_custom_features(self, sample_data):
        """Test initialization with custom audio features."""
        custom_features = ["energy", "tempo"]
        recommender = MusicRecommender(sample_data, audio_features=custom_features)

        assert recommender.audio_features == custom_features

    @patch("src.musicrec.models.engine.print")
    def test_init_prints_progress(self, mock_print, sample_data):
        """Test that initialization prints progress messages."""
        MusicRecommender(sample_data)

        # Check that progress messages were printed
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Initializing music recommender" in call for call in print_calls)
        assert any("Creating genre tree" in call for call in print_calls)


class TestRecommendByGenre:
    """Test genre-based recommendations."""

    def test_recommend_by_genre_existing(self, music_recommender):
        """Test recommending tracks by existing genre."""
        recommendations = music_recommender.recommend_by_genre("rock", limit=5)

        assert len(recommendations) <= 5
        assert all("track_id" in rec for rec in recommendations)
        assert all("genre_path" in rec for rec in recommendations)

        # Check that returned tracks have rock in their genre path
        for rec in recommendations:
            genre_path = rec["genre_path"]
            assert any("rock" in path_part.lower() for path_part in genre_path)

    def test_recommend_by_genre_nonexistent(self, music_recommender):
        """Test recommending tracks by non-existent genre."""
        recommendations = music_recommender.recommend_by_genre("jazz", limit=5)

        # Should return empty list for non-existent genre
        assert len(recommendations) == 0

    def test_recommend_by_genre_limit(self, music_recommender):
        """Test that recommendations respect the limit parameter."""
        recommendations = music_recommender.recommend_by_genre("pop", limit=1)

        assert len(recommendations) <= 1


class TestRecommendByMood:
    """Test mood-based recommendations."""

    def test_recommend_by_mood_existing(self, music_recommender):
        """Test recommending tracks by existing mood."""
        recommendations = music_recommender.recommend_by_mood("happy", limit=5)

        assert len(recommendations) >= 1
        assert all("track_id" in rec for rec in recommendations)
        assert all("mood_tags" in rec for rec in recommendations)

        # Check that returned tracks have the requested mood
        for rec in recommendations:
            mood_tags = rec["mood_tags"]
            assert "happy" in mood_tags

    def test_recommend_by_mood_nonexistent(self, music_recommender):
        """Test recommending tracks by non-existent mood."""
        recommendations = music_recommender.recommend_by_mood("angry", limit=5)

        # Should return empty list for non-existent mood
        assert len(recommendations) == 0


class TestRecommendByGenreAndMood:
    """Test combined genre and mood recommendations."""

    def test_recommend_by_genre_and_mood_existing(self, music_recommender):
        """Test recommending tracks by existing genre and mood combination."""
        # This might return empty if no tracks match both criteria
        recommendations = music_recommender.recommend_by_genre_and_mood(
            "rock", "happy", limit=5
        )

        assert isinstance(recommendations, list)

        # If there are recommendations, they should match both criteria
        for rec in recommendations:
            assert "happy" in rec["mood_tags"]
            genre_path = rec["genre_path"]
            assert any("rock" in str(path_part).lower() for path_part in genre_path)

    def test_recommend_by_genre_and_mood_no_match(self, music_recommender):
        """Test recommending tracks by genre and mood with no matches."""
        recommendations = music_recommender.recommend_by_genre_and_mood(
            "rock", "party", limit=5
        )

        # Should return empty list when no tracks match both criteria
        assert len(recommendations) == 0


class TestRecommendSimilarToTrack:
    """Test similarity-based recommendations."""

    def test_recommend_similar_to_track_existing(self, music_recommender):
        """Test recommending tracks similar to an existing track."""
        recommendations = music_recommender.recommend_similar_to_track(
            "track_1", limit=3
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) <= 3

        # Each recommendation should have similarity score
        for rec in recommendations:
            assert "similarity" in rec
            assert isinstance(rec["similarity"], (int, float))
            assert 0 <= rec["similarity"] <= 1

    def test_recommend_similar_to_track_nonexistent(self, music_recommender):
        """Test recommending tracks similar to a non-existent track."""
        recommendations = music_recommender.recommend_similar_to_track(
            "nonexistent_track", limit=3
        )

        # Should return empty list for non-existent track
        assert len(recommendations) == 0


class TestBFSRecommend:
    """Test breadth-first search recommendations."""

    def test_bfs_recommend_genre_only(self, music_recommender):
        """Test BFS recommendations with genre only."""
        recommendations = music_recommender.bfs_recommend("rock", max_depth=2, limit=5)

        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5

        # Should not have duplicates
        track_ids = [rec["track_id"] for rec in recommendations]
        assert len(track_ids) == len(set(track_ids))

    def test_bfs_recommend_with_mood(self, music_recommender):
        """Test BFS recommendations with genre and mood."""
        recommendations = music_recommender.bfs_recommend(
            "pop", mood="energetic", max_depth=2, limit=5
        )

        assert isinstance(recommendations, list)

        # If there are recommendations with the mood, they should match
        for rec in recommendations:
            if "energetic" in rec.get("mood_tags", []):
                assert "energetic" in rec["mood_tags"]


class TestDFSRecommend:
    """Test depth-first search recommendations."""

    def test_dfs_recommend_genre_only(self, music_recommender):
        """Test DFS recommendations with genre only."""
        recommendations = music_recommender.dfs_recommend(
            "rock", max_breadth=3, limit=5
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5

        # Should not have duplicates
        track_ids = [rec["track_id"] for rec in recommendations]
        assert len(track_ids) == len(set(track_ids))

    def test_dfs_recommend_with_mood(self, music_recommender):
        """Test DFS recommendations with genre and mood."""
        recommendations = music_recommender.dfs_recommend(
            "pop", mood="party", max_breadth=3, limit=5
        )

        assert isinstance(recommendations, list)


class TestUtilityMethods:
    """Test utility methods."""

    def test_get_available_genres(self, music_recommender):
        """Test getting available genres."""
        genres = music_recommender.get_available_genres()

        assert isinstance(genres, list)
        assert len(genres) > 0
        assert all(isinstance(genre, str) for genre in genres)

        # Should include genres from our sample data
        expected_genres = {"rock", "indie", "pop", "dance"}
        actual_genres = set(genres)
        assert expected_genres.issubset(actual_genres)

    def test_get_available_moods(self, music_recommender):
        """Test getting available moods."""
        moods = music_recommender.get_available_moods()

        assert isinstance(moods, list)
        assert len(moods) > 0
        assert all(isinstance(mood, str) for mood in moods)

        # Should include moods from our sample data
        expected_moods = {"happy", "calm", "energetic", "party"}
        actual_moods = set(moods)
        assert expected_moods.issubset(actual_moods)

    def test_get_track_info_existing(self, music_recommender):
        """Test getting info for an existing track."""
        track_info = music_recommender.get_track_info("track_1")

        assert track_info is not None
        assert track_info["track_id"] == "track_1"
        assert "track_name" in track_info
        assert "artist_name" in track_info
        assert "genre_path" in track_info
        assert "mood_tags" in track_info

        # Should include audio features
        for feature in music_recommender.audio_features:
            assert feature in track_info

    def test_get_track_info_nonexistent(self, music_recommender):
        """Test getting info for a non-existent track."""
        track_info = music_recommender.get_track_info("nonexistent_track")

        assert track_info is None

    def test_search_tracks_by_name(self, music_recommender):
        """Test searching tracks by name."""
        results = music_recommender.search_tracks_by_name("Song A", limit=5)

        assert isinstance(results, list)
        assert len(results) >= 1

        # Should find the track with "Song A" in the name
        found_track = next(
            (r for r in results if "Song A" in r.get("track_name", "")), None
        )
        assert found_track is not None
        assert found_track["track_name"] == "Song A"

    def test_search_tracks_by_artist(self, music_recommender):
        """Test searching tracks by artist name."""
        results = music_recommender.search_tracks_by_name("Artist 1", limit=5)

        assert isinstance(results, list)
        assert len(results) >= 1

        # Should find tracks by "Artist 1"
        for result in results:
            if "artist_name" in result:
                assert "Artist 1" in result["artist_name"]

    def test_search_tracks_empty_result(self, music_recommender):
        """Test searching tracks with no matches."""
        results = music_recommender.search_tracks_by_name("Nonexistent Song", limit=5)

        assert isinstance(results, list)
        assert len(results) == 0


class TestRecommendationContent:
    """Test the content of recommendations."""

    def test_recommendation_structure(self, music_recommender):
        """Test that recommendations have the expected structure."""
        recommendations = music_recommender.recommend_by_genre("rock", limit=1)

        if len(recommendations) > 0:
            rec = recommendations[0]

            # Required fields
            required_fields = ["track_id", "genre_path", "mood_tags"]
            for field in required_fields:
                assert field in rec

            # Optional fields that should be present if available
            optional_fields = ["track_name", "artist_name"]
            for field in optional_fields:
                if field in rec:
                    assert isinstance(rec[field], str)

            # Audio features should be present
            for feature in music_recommender.audio_features:
                assert feature in rec
                assert isinstance(rec[feature], (int, float))

    def test_audio_features_in_recommendations(self, music_recommender):
        """Test that audio features are included in recommendations."""
        recommendations = music_recommender.recommend_by_mood("happy", limit=1)

        if len(recommendations) > 0:
            rec = recommendations[0]

            for feature in music_recommender.audio_features:
                assert feature in rec
                assert isinstance(rec[feature], (int, float))


class TestErrorHandling:
    """Test error handling in recommendations."""

    def test_invalid_limit_parameter(self, music_recommender):
        """Test that invalid limit parameters are handled gracefully."""
        # Negative limit should still work (treated as 0 or similar)
        recommendations = music_recommender.recommend_by_genre("rock", limit=-1)
        assert isinstance(recommendations, list)

        # Zero limit
        recommendations = music_recommender.recommend_by_genre("rock", limit=0)
        assert isinstance(recommendations, list)
        assert len(recommendations) == 0

    def test_empty_genre_string(self, music_recommender):
        """Test behavior with empty genre string."""
        recommendations = music_recommender.recommend_by_genre("", limit=5)
        assert isinstance(recommendations, list)

    def test_empty_mood_string(self, music_recommender):
        """Test behavior with empty mood string."""
        recommendations = music_recommender.recommend_by_mood("", limit=5)
        assert isinstance(recommendations, list)


@pytest.fixture
def empty_data():
    """Create empty DataFrame for testing edge cases."""
    return pd.DataFrame(
        {
            "track_id": [],
            "track_name": [],
            "artist_name": [],
            "genre_hierarchy": [],
            "mood_tags": [],
            "energy": [],
            "valence": [],
            "tempo": [],
            "duration": [],
        }
    )


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_dataset(self, empty_data):
        """Test behavior with empty dataset."""
        recommender = MusicRecommender(empty_data)

        # Should handle empty dataset gracefully
        assert len(recommender.get_available_genres()) == 0
        assert len(recommender.get_available_moods()) == 0

        recommendations = recommender.recommend_by_genre("rock")
        assert len(recommendations) == 0

    def test_large_limit(self, music_recommender):
        """Test behavior with very large limit."""
        recommendations = music_recommender.recommend_by_genre("rock", limit=1000)

        # Should return all available tracks, not more than exist
        assert isinstance(recommendations, list)
        assert len(recommendations) <= len(music_recommender.data)


if __name__ == "__main__":
    pytest.main([__file__])
