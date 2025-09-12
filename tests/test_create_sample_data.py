"""Tests for create_sample_data function error handling and validation."""

import pytest
import pandas as pd
from src.musicrec.main import create_sample_data


class TestCreateSampleDataValidation:
    """Test parameter validation for create_sample_data function."""

    def test_invalid_num_genres_type(self):
        """Test that non-integer num_genres raises ValueError."""
        with pytest.raises(ValueError, match="num_genres must be an integer"):
            create_sample_data(num_genres="4", tracks_per_genre=5)

        with pytest.raises(ValueError, match="num_genres must be an integer"):
            create_sample_data(num_genres=4.5, tracks_per_genre=5)

        with pytest.raises(ValueError, match="num_genres must be an integer"):
            create_sample_data(num_genres=None, tracks_per_genre=5)

    def test_invalid_tracks_per_genre_type(self):
        """Test that non-integer tracks_per_genre raises ValueError."""
        with pytest.raises(ValueError, match="tracks_per_genre must be an integer"):
            create_sample_data(num_genres=2, tracks_per_genre="10")

        with pytest.raises(ValueError, match="tracks_per_genre must be an integer"):
            create_sample_data(num_genres=2, tracks_per_genre=10.5)

        with pytest.raises(ValueError, match="tracks_per_genre must be an integer"):
            create_sample_data(num_genres=2, tracks_per_genre=None)

    def test_num_genres_too_small(self):
        """Test that num_genres < 1 raises ValueError."""
        with pytest.raises(ValueError, match="num_genres must be at least 1, got 0"):
            create_sample_data(num_genres=0, tracks_per_genre=5)

        with pytest.raises(ValueError, match="num_genres must be at least 1, got -1"):
            create_sample_data(num_genres=-1, tracks_per_genre=5)

        with pytest.raises(ValueError, match="num_genres must be at least 1, got -10"):
            create_sample_data(num_genres=-10, tracks_per_genre=5)

    def test_num_genres_too_large(self):
        """Test that num_genres > 100 raises ValueError."""
        with pytest.raises(ValueError, match="num_genres cannot exceed 100, got 101"):
            create_sample_data(num_genres=101, tracks_per_genre=5)

        with pytest.raises(ValueError, match="num_genres cannot exceed 100, got 1000"):
            create_sample_data(num_genres=1000, tracks_per_genre=5)

    def test_tracks_per_genre_too_small(self):
        """Test that tracks_per_genre < 1 raises ValueError."""
        with pytest.raises(
            ValueError, match="tracks_per_genre must be at least 1, got 0"
        ):
            create_sample_data(num_genres=2, tracks_per_genre=0)

        with pytest.raises(
            ValueError, match="tracks_per_genre must be at least 1, got -1"
        ):
            create_sample_data(num_genres=2, tracks_per_genre=-1)

        with pytest.raises(
            ValueError, match="tracks_per_genre must be at least 1, got -5"
        ):
            create_sample_data(num_genres=2, tracks_per_genre=-5)

    def test_tracks_per_genre_too_large(self):
        """Test that tracks_per_genre > 1000 raises ValueError."""
        with pytest.raises(
            ValueError, match="tracks_per_genre cannot exceed 1000, got 1001"
        ):
            create_sample_data(num_genres=2, tracks_per_genre=1001)

        with pytest.raises(
            ValueError, match="tracks_per_genre cannot exceed 1000, got 5000"
        ):
            create_sample_data(num_genres=2, tracks_per_genre=5000)


class TestCreateSampleDataHappyPath:
    """Test successful data generation scenarios."""

    def test_default_parameters(self):
        """Test that default parameters generate valid data."""
        df = create_sample_data()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) > 0

        # Check required columns exist
        required_columns = [
            "track_id",
            "track_name",
            "artist_name",
            "genre_tags",
            "mood_tags",
            "duration",
            "energy",
            "valence",
            "tempo",
            "genre_hierarchy",
        ]
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"

    def test_minimal_parameters(self):
        """Test generation with minimal valid parameters."""
        df = create_sample_data(num_genres=1, tracks_per_genre=1)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) >= 1  # At least 1 track + subgenres

        # Check data integrity
        assert df["track_id"].duplicated().sum() == 0
        assert all(df["energy"] >= 0) and all(df["energy"] <= 1)
        assert all(df["valence"] >= 0) and all(df["valence"] <= 1)
        assert all(df["tempo"] > 0)
        assert all(df["duration"] > 0)

    def test_boundary_parameters(self):
        """Test generation with boundary valid parameters."""
        df = create_sample_data(num_genres=100, tracks_per_genre=1000)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty

        # Check data ranges
        assert all(df["energy"] >= 0) and all(df["energy"] <= 1)
        assert all(df["valence"] >= 0) and all(df["valence"] <= 1)
        assert all(df["tempo"] > 0)
        assert all(df["duration"] > 0)
        assert df["track_id"].duplicated().sum() == 0

    def test_various_genre_counts(self):
        """Test that different genre counts generate appropriate data."""
        for num_genres in [1, 2, 3, 4, 5]:
            df = create_sample_data(num_genres=num_genres, tracks_per_genre=2)

            # Should have tracks from requested genres plus subgenres
            unique_main_genres = df["genre_hierarchy"].apply(lambda x: x[0]).nunique()
            assert unique_main_genres >= min(
                num_genres, 4
            )  # Max 4 main genres in current impl

    def test_data_consistency(self):
        """Test that generated data has consistent structure."""
        df = create_sample_data(num_genres=3, tracks_per_genre=5)

        # Check that all rows have required data types
        assert df["track_id"].dtype == "object"
        assert df["track_name"].dtype == "object"
        assert df["artist_name"].dtype == "object"
        assert pd.api.types.is_numeric_dtype(df["energy"])
        assert pd.api.types.is_numeric_dtype(df["valence"])
        assert pd.api.types.is_numeric_dtype(df["tempo"])
        assert pd.api.types.is_numeric_dtype(df["duration"])

        # Check that lists are properly structured
        assert all(isinstance(tags, list) for tags in df["genre_tags"])
        assert all(isinstance(tags, list) for tags in df["mood_tags"])
        assert all(isinstance(hierarchy, list) for hierarchy in df["genre_hierarchy"])

        # Check that no essential fields are empty
        assert not df["track_id"].isna().any()
        assert not df["track_name"].isna().any()
        assert not df["artist_name"].isna().any()


class TestCreateSampleDataErrorConditions:
    """Test error conditions that could occur during data generation."""

    def test_parameter_edge_cases(self):
        """Test edge cases that should work."""
        # Edge case: exactly at boundaries
        df = create_sample_data(num_genres=1, tracks_per_genre=1)
        assert not df.empty

        df = create_sample_data(num_genres=100, tracks_per_genre=1)
        assert not df.empty

        df = create_sample_data(num_genres=1, tracks_per_genre=1000)
        assert not df.empty


class TestCreateSampleDataPerformance:
    """Test performance characteristics of data generation."""

    def test_reasonable_performance_large_dataset(self):
        """Test that large datasets can be generated without issues."""
        import time

        start_time = time.time()
        df = create_sample_data(num_genres=10, tracks_per_genre=50)
        end_time = time.time()

        # Should complete in reasonable time (less than 5 seconds)
        assert end_time - start_time < 5.0
        assert not df.empty
        assert len(df) > 40  # Should have tracks from genres + subgenres


class TestCreateSampleDataSchemaValidation:
    """Test that generated data meets expected schema requirements."""

    def test_track_id_uniqueness(self):
        """Test that all track IDs are unique."""
        df = create_sample_data(num_genres=4, tracks_per_genre=10)

        track_ids = df["track_id"].tolist()
        assert len(track_ids) == len(set(track_ids)), "Track IDs must be unique"

    def test_audio_feature_ranges(self):
        """Test that audio features are within expected ranges."""
        df = create_sample_data(num_genres=2, tracks_per_genre=20)

        # Energy and valence should be 0-1
        assert df["energy"].min() >= 0, "Energy values must be non-negative"
        assert df["energy"].max() <= 1, "Energy values must not exceed 1"
        assert df["valence"].min() >= 0, "Valence values must be non-negative"
        assert df["valence"].max() <= 1, "Valence values must not exceed 1"

        # Tempo should be positive
        assert df["tempo"].min() > 0, "Tempo values must be positive"

        # Duration should be positive
        assert df["duration"].min() > 0, "Duration values must be positive"

    def test_required_columns_present(self):
        """Test that all required columns are present."""
        df = create_sample_data()

        required_columns = [
            "track_id",
            "track_name",
            "artist_name",
            "genre_tags",
            "mood_tags",
            "duration",
            "energy",
            "valence",
            "tempo",
            "genre_hierarchy",
        ]

        for column in required_columns:
            assert column in df.columns, f"Required column '{column}' is missing"

    def test_list_columns_structure(self):
        """Test that list columns have proper structure."""
        df = create_sample_data(num_genres=2, tracks_per_genre=5)

        # Check genre_tags column
        for genre_tags in df["genre_tags"]:
            assert isinstance(genre_tags, list), "genre_tags must be a list"
            assert len(genre_tags) > 0, "genre_tags must not be empty"
            assert all(
                isinstance(tag, str) for tag in genre_tags
            ), "All genre tags must be strings"

        # Check mood_tags column
        for mood_tags in df["mood_tags"]:
            assert isinstance(mood_tags, list), "mood_tags must be a list"
            assert len(mood_tags) > 0, "mood_tags must not be empty"
            assert all(
                isinstance(tag, str) for tag in mood_tags
            ), "All mood tags must be strings"

        # Check genre_hierarchy column
        for hierarchy in df["genre_hierarchy"]:
            assert isinstance(hierarchy, list), "genre_hierarchy must be a list"
            assert len(hierarchy) > 0, "genre_hierarchy must not be empty"
            assert all(
                isinstance(genre, str) for genre in hierarchy
            ), "All hierarchy items must be strings"
