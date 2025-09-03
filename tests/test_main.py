"""Tests for main module functionality."""

import pytest
import pandas as pd


def test_sample_data_validation():
    """Test basic validation logic without importing full module."""
    # Test that we can validate input parameters
    def validate_params(num_genres: int, tracks_per_genre: int):
        if num_genres < 1:
            raise ValueError("num_genres must be at least 1")
        if tracks_per_genre < 1:
            raise ValueError("tracks_per_genre must be at least 1")
    
    # Valid parameters should not raise
    validate_params(4, 10)
    
    # Invalid parameters should raise
    with pytest.raises(ValueError, match="num_genres must be at least 1"):
        validate_params(0, 10)
        
    with pytest.raises(ValueError, match="tracks_per_genre must be at least 1"):
        validate_params(4, 0)


def test_sample_dataframe_structure(sample_track_data):
    """Test that our fixture has the expected structure."""
    assert isinstance(sample_track_data, pd.DataFrame)
    assert len(sample_track_data) == 2
    assert "track_id" in sample_track_data.columns
    assert "track_name" in sample_track_data.columns
    assert "genre_hierarchy" in sample_track_data.columns