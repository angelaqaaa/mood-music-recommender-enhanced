"""Pytest configuration and fixtures."""

import pytest
import pandas as pd


@pytest.fixture
def sample_track_data():
    """Create minimal sample track data for testing."""
    return pd.DataFrame(
        [
            {
                "track_id": "test_001",
                "track_name": "Test Song 1",
                "artist_name": "Test Artist 1",
                "genre_hierarchy": ["rock"],
                "mood_tags": ["energetic", "happy"],
                "energy": 0.8,
                "valence": 0.7,
                "tempo": 120,
            },
            {
                "track_id": "test_002",
                "track_name": "Test Song 2",
                "artist_name": "Test Artist 2",
                "genre_hierarchy": ["electronic"],
                "mood_tags": ["upbeat"],
                "energy": 0.9,
                "valence": 0.8,
                "tempo": 128,
            },
        ]
    )
