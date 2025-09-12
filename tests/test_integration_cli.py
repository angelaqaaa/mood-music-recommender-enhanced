"""Integration tests for CLI functionality and end-to-end flows."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.musicrec.main import create_sample_data, load_data, main
from src.musicrec.models.engine import MusicRecommender


class TestEndToEndSampleDataFlow:
    """Test complete end-to-end flow with sample data."""

    def test_create_sample_data_integration(self):
        """Test creating sample data and using it for recommendations."""
        # Create sample data
        sample_df = create_sample_data(num_genres=3, tracks_per_genre=5)

        # Verify sample data structure
        assert len(sample_df) == 15  # 3 genres × 5 tracks
        required_columns = [
            "track_id",
            "genre_hierarchy",
            "mood_tags",
            "energy",
            "valence",
            "tempo",
        ]
        for col in required_columns:
            assert col in sample_df.columns

        # Create recommender with sample data
        recommender = MusicRecommender(sample_df)

        # Test various recommendation methods
        genres = recommender.get_available_genres()
        assert len(genres) >= 3

        moods = recommender.get_available_moods()
        assert len(moods) >= 3

        # Test genre-based recommendations
        if len(genres) > 0:
            genre_recs = recommender.recommend_by_genre(genres[0], limit=3)
            assert len(genre_recs) <= 3
            assert all("track_id" in rec for rec in genre_recs)

        # Test mood-based recommendations
        if len(moods) > 0:
            mood_recs = recommender.recommend_by_mood(moods[0], limit=3)
            assert len(mood_recs) <= 3
            assert all("track_id" in rec for rec in mood_recs)

    def test_load_data_fallback_to_sample(self):
        """Test that load_data falls back to sample data when files don't exist."""
        # Use non-existent file paths
        nonexistent_paths = {
            "spotify_path": "/nonexistent/spotify.csv",
            "genre_path": "/nonexistent/genre.tsv",
            "mood_path": "/nonexistent/mood.tsv",
            "metadata_path": "/nonexistent/metadata.tsv",
        }

        # Should fall back to sample data
        df = load_data(**nonexistent_paths)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        # Should have expected columns from sample data
        required_columns = ["track_id", "genre_hierarchy", "mood_tags"]
        for col in required_columns:
            assert col in df.columns

    def test_recommendation_engine_with_sample_data(self):
        """Test complete recommendation engine workflow with sample data."""
        # Load sample data
        df = load_data()  # Should fall back to sample data

        # Create recommender
        recommender = MusicRecommender(df, audio_features=["energy", "valence"])

        # Test all recommendation methods
        genres = recommender.get_available_genres()
        moods = recommender.get_available_moods()

        assert len(genres) > 0
        assert len(moods) > 0

        # Test each recommendation method
        test_cases = [
            lambda: recommender.recommend_by_genre(genres[0], limit=5),
            lambda: recommender.recommend_by_mood(moods[0], limit=5),
            lambda: recommender.bfs_recommend(genres[0], max_depth=2, limit=5),
            lambda: recommender.dfs_recommend(genres[0], max_breadth=3, limit=5),
        ]

        for test_case in test_cases:
            results = test_case()
            assert isinstance(results, list)
            assert all(isinstance(rec, dict) for rec in results)

            # Check that each recommendation has required fields
            for rec in results:
                assert "track_id" in rec
                assert "genre_path" in rec
                assert "mood_tags" in rec

        # Test similarity-based recommendations if tracks exist
        if len(df) > 0:
            first_track_id = df.iloc[0]["track_id"]
            similar_tracks = recommender.recommend_similar_to_track(
                first_track_id, limit=3
            )
            assert isinstance(similar_tracks, list)

            for rec in similar_tracks:
                assert "track_id" in rec
                assert "similarity" in rec
                assert isinstance(rec["similarity"], (int, float))

    def test_search_functionality_integration(self):
        """Test search functionality with sample data."""
        df = load_data()
        recommender = MusicRecommender(df)

        # Test track search
        if len(df) > 0 and "track_name" in df.columns:
            # Get a track name from sample data
            sample_track = df.iloc[0]
            if "track_name" in sample_track and sample_track["track_name"]:
                search_term = sample_track["track_name"][:5]  # Search partial name
                results = recommender.search_tracks_by_name(search_term, limit=5)
                assert isinstance(results, list)

        # Test track info retrieval
        first_track_id = df.iloc[0]["track_id"]
        track_info = recommender.get_track_info(first_track_id)

        assert track_info is not None
        assert track_info["track_id"] == first_track_id
        assert "genre_path" in track_info
        assert "mood_tags" in track_info


class TestCLIIntegration:
    """Test CLI functionality integration."""

    @patch("src.musicrec.visualization.MusicRecommenderDashApp")
    def test_main_function_sample_mode(self, mock_dash_app):
        """Test main function in sample mode."""
        mock_app_instance = MagicMock()
        mock_dash_app.return_value = mock_app_instance

        # Mock command line arguments for sample mode
        test_args = ["--sample", "--port", "8050"]

        with patch("sys.argv", ["main.py"] + test_args):
            try:
                main()

                # Verify Dash app was created and run
                mock_dash_app.assert_called_once()
                mock_app_instance.run_server.assert_called_once_with(
                    debug=True, host="0.0.0.0", port=8050
                )

            except SystemExit as e:
                # main() may call sys.exit(), which is expected
                pass

    @patch("src.musicrec.main.create_sample_data")
    @patch("src.musicrec.main.build_dataset")
    def test_main_function_save_mode(self, mock_build_dataset, mock_create_sample):
        """Test main function in save mode."""
        mock_df = pd.DataFrame(
            {
                "track_id": ["track_1", "track_2"],
                "genre_hierarchy": [["rock"], ["pop"]],
                "mood_tags": [["happy"], ["energetic"]],
            }
        )
        mock_create_sample.return_value = mock_df
        mock_build_dataset.return_value = mock_df

        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            test_args = ["--sample", "--save", temp_path]

            with patch("sys.argv", ["main.py"] + test_args):
                try:
                    main()
                except SystemExit:
                    pass  # Expected

            # Verify file was created
            assert Path(temp_path).exists()

            # Verify file contains data
            saved_df = pd.read_pickle(temp_path)
            assert len(saved_df) == 2

        finally:
            # Cleanup
            if Path(temp_path).exists():
                os.unlink(temp_path)

    def test_cli_error_handling(self):
        """Test CLI error handling with invalid arguments."""
        test_args = ["--port", "invalid_port"]

        with patch("sys.argv", ["main.py"] + test_args):
            # Should handle invalid port gracefully
            try:
                main()
            except (SystemExit, ValueError):
                # Expected behavior for invalid arguments
                pass


class TestDataProcessingIntegration:
    """Test data processing pipeline integration."""

    def test_sample_data_to_recommender_pipeline(self):
        """Test complete pipeline from sample data creation to recommendations."""
        # Step 1: Create sample data with specific parameters
        num_genres = 4
        tracks_per_genre = 8

        df = create_sample_data(
            num_genres=num_genres, tracks_per_genre=tracks_per_genre
        )

        # Step 2: Verify data quality
        assert len(df) == num_genres * tracks_per_genre

        # Check data types and values
        assert df["energy"].dtype in ["float64", "float32"]
        assert df["valence"].dtype in ["float64", "float32"]
        assert df["tempo"].dtype in ["float64", "float32"]

        assert df["energy"].min() >= 0 and df["energy"].max() <= 1
        assert df["valence"].min() >= 0 and df["valence"].max() <= 1
        assert df["tempo"].min() > 0

        # Step 3: Create recommender and test functionality
        recommender = MusicRecommender(df)

        # Test that all expected genres are present
        available_genres = recommender.get_available_genres()
        assert len(available_genres) == num_genres

        # Test that all expected moods are present
        available_moods = recommender.get_available_moods()
        assert len(available_moods) >= 3  # Should have at least a few different moods

        # Step 4: Test recommendation quality
        for genre in available_genres:
            genre_recs = recommender.recommend_by_genre(genre, limit=10)

            # Should get some recommendations for each genre
            assert len(genre_recs) > 0

            # All recommendations should have the requested genre in their path
            for rec in genre_recs:
                genre_path = rec["genre_path"]
                assert any(
                    genre.lower() in str(path_part).lower() for path_part in genre_path
                )

        # Step 5: Test similarity recommendations
        first_track = df.iloc[0]["track_id"]
        similar_tracks = recommender.recommend_similar_to_track(first_track, limit=5)

        # Should find similar tracks
        assert isinstance(similar_tracks, list)

        # Similarities should be reasonable
        for rec in similar_tracks:
            assert 0 <= rec["similarity"] <= 1

    def test_configuration_integration(self):
        """Test configuration system integration with data loading."""
        from src.musicrec.config.settings import get_data_paths, load_config

        # Test default configuration loading
        config = load_config()

        assert "data" in config
        assert "retry" in config
        assert "app" in config

        # Test data paths extraction
        data_paths = get_data_paths(config)

        required_paths = ["spotify_path", "genre_path", "mood_path", "metadata_path"]
        for path_key in required_paths:
            assert path_key in data_paths
            assert isinstance(data_paths[path_key], str)

        # Test that load_data uses configuration
        with patch("src.musicrec.main.load_config") as mock_load_config:
            mock_load_config.return_value = config

            df = load_data()  # Should fall back to sample data

            assert isinstance(df, pd.DataFrame)
            mock_load_config.assert_called()


class TestPerformanceIntegration:
    """Test performance aspects of integration."""

    def test_large_sample_data_performance(self):
        """Test performance with larger sample datasets."""
        # Create larger sample data
        df = create_sample_data(num_genres=10, tracks_per_genre=20)

        assert len(df) == 200

        # Creating recommender should complete in reasonable time
        import time

        start_time = time.time()

        recommender = MusicRecommender(df)

        creation_time = time.time() - start_time
        assert creation_time < 10  # Should complete within 10 seconds

        # Recommendations should be fast
        start_time = time.time()

        genres = recommender.get_available_genres()
        if genres:
            recommendations = recommender.recommend_by_genre(genres[0], limit=10)

        recommendation_time = time.time() - start_time
        assert recommendation_time < 2  # Should complete within 2 seconds

        # Similarity search should be reasonable
        if len(df) > 0:
            start_time = time.time()

            first_track = df.iloc[0]["track_id"]
            similar = recommender.recommend_similar_to_track(first_track, limit=5)

            similarity_time = time.time() - start_time
            assert similarity_time < 5  # Should complete within 5 seconds

    def test_memory_usage_integration(self):
        """Test that memory usage stays reasonable."""
        import gc

        # Force garbage collection before test
        gc.collect()

        # Create multiple recommenders to test memory usage
        recommenders = []

        for i in range(5):
            df = create_sample_data(num_genres=5, tracks_per_genre=10)
            recommender = MusicRecommender(df)
            recommenders.append(recommender)

        # Should be able to create multiple instances without issues
        assert len(recommenders) == 5

        # Test that they all work
        for recommender in recommenders:
            genres = recommender.get_available_genres()
            assert len(genres) > 0

            if genres:
                recs = recommender.recommend_by_genre(genres[0], limit=3)
                assert isinstance(recs, list)

        # Cleanup
        del recommenders
        gc.collect()


if __name__ == "__main__":
    pytest.main([__file__])
