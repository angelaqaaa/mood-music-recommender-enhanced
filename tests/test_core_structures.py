"""Unit tests for core data structures in models/structures.py.

This module tests the MusicNode, GenreTree, and SimilaritySongGraph classes
with both happy path scenarios and edge cases.
"""

import pytest
import pandas as pd
import numpy as np
from src.musicrec.models.structures import MusicNode, GenreTree, SimilaritySongGraph


class TestMusicNode:
    """Test suite for MusicNode class."""

    def test_node_creation_genre(self):
        """Test creating a genre node."""
        node = MusicNode("rock", "genre")
        
        assert node.name == "rock"
        assert node.node_type == "genre"
        assert node.parent is None
        assert node.children == []
        assert node.data == {}

    def test_node_creation_track(self):
        """Test creating a track node."""
        node = MusicNode("track_123", "track")
        
        assert node.name == "track_123"
        assert node.node_type == "track"
        assert node.parent is None
        assert node.children == []
        assert node.data == {}

    def test_node_with_parent(self):
        """Test creating a node with parent relationship."""
        parent = MusicNode("rock", "genre")
        child = MusicNode("metal", "genre", parent=parent)
        
        assert child.parent == parent
        assert child in parent.children

    def test_add_child(self):
        """Test adding children to a node."""
        parent = MusicNode("rock", "genre")
        child1 = MusicNode("metal", "genre")
        child2 = MusicNode("punk", "genre")
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        assert len(parent.children) == 2
        assert child1 in parent.children
        assert child2 in parent.children
        assert child1.parent == parent
        assert child2.parent == parent

    def test_get_path_to_root(self):
        """Test getting path from node to root."""
        root = MusicNode("music", "genre")
        rock = MusicNode("rock", "genre", parent=root)
        metal = MusicNode("metal", "genre", parent=rock)
        
        path = metal.get_path_to_root()
        expected_path = ["metal", "rock", "music"]
        
        assert path == expected_path

    def test_node_str_representation(self):
        """Test string representation of nodes."""
        node = MusicNode("rock", "genre")
        
        assert str(node) == "rock (genre)"


class TestGenreTree:
    """Test suite for GenreTree class."""

    @pytest.fixture
    def sample_data(self):
        """Create sample track data for testing."""
        return pd.DataFrame([
            {
                "track_id": "track_1",
                "track_name": "Song A",
                "artist_name": "Artist 1",
                "genre_hierarchy": ["rock"],
                "mood_tags": ["energetic"],
                "energy": 0.8,
                "valence": 0.6
            },
            {
                "track_id": "track_2", 
                "track_name": "Song B",
                "artist_name": "Artist 2",
                "genre_hierarchy": ["rock", "metal"],
                "mood_tags": ["intense"],
                "energy": 0.9,
                "valence": 0.3
            },
            {
                "track_id": "track_3",
                "track_name": "Song C", 
                "artist_name": "Artist 3",
                "genre_hierarchy": ["electronic"],
                "mood_tags": ["upbeat"],
                "energy": 0.7,
                "valence": 0.8
            }
        ])

    def test_tree_creation(self, sample_data):
        """Test basic tree creation from data."""
        tree = GenreTree(sample_data)
        
        assert tree.root is not None
        assert tree.root.name == "music"
        assert tree.root.node_type == "genre"
        
        # Check that genres were added
        genre_names = [child.name for child in tree.root.children]
        assert "rock" in genre_names
        assert "electronic" in genre_names

    def test_build_hierarchy(self, sample_data):
        """Test that genre hierarchy is built correctly."""
        tree = GenreTree(sample_data)
        
        # Find rock node
        rock_node = None
        for child in tree.root.children:
            if child.name == "rock":
                rock_node = child
                break
        
        assert rock_node is not None
        
        # Check that metal is a child of rock
        metal_node = None
        for child in rock_node.children:
            if child.name == "metal":
                metal_node = child
                break
                
        assert metal_node is not None
        assert metal_node.parent == rock_node

    def test_get_available_genres(self, sample_data):
        """Test retrieving all available genres."""
        tree = GenreTree(sample_data)
        genres = tree.get_available_genres()
        
        assert "rock" in genres
        assert "metal" in genres
        assert "electronic" in genres
        assert "music" not in genres  # Root should not be included

    def test_find_genre_node(self, sample_data):
        """Test finding specific genre nodes."""
        tree = GenreTree(sample_data)
        
        rock_node = tree.find_genre_node("rock")
        assert rock_node is not None
        assert rock_node.name == "rock"
        
        metal_node = tree.find_genre_node("metal")
        assert metal_node is not None
        assert metal_node.name == "metal"
        
        # Non-existent genre
        fake_node = tree.find_genre_node("nonexistent")
        assert fake_node is None

    def test_get_tracks_by_genre(self, sample_data):
        """Test retrieving tracks by genre."""
        tree = GenreTree(sample_data)
        
        # Get tracks from rock genre (should include metal subgenre)
        rock_tracks = tree.get_tracks_by_genre("rock")
        assert len(rock_tracks) == 2  # track_1 (rock) and track_2 (rock->metal)
        
        # Get tracks from electronic genre
        electronic_tracks = tree.get_tracks_by_genre("electronic")
        assert len(electronic_tracks) == 1
        assert electronic_tracks[0].name == "track_3"

    def test_empty_data(self):
        """Test tree creation with empty data."""
        empty_data = pd.DataFrame(columns=["track_id", "genre_hierarchy"])
        tree = GenreTree(empty_data)
        
        assert tree.root is not None
        assert tree.root.name == "music"
        assert len(tree.root.children) == 0


class TestSimilaritySongGraph:
    """Test suite for SimilaritySongGraph class."""

    @pytest.fixture
    def sample_data(self):
        """Create sample track data for testing."""
        return pd.DataFrame([
            {
                "track_id": "track_1",
                "track_name": "Song A",
                "artist_name": "Artist 1", 
                "energy": 0.8,
                "valence": 0.6,
                "tempo": 120.0,
                "danceability": 0.7
            },
            {
                "track_id": "track_2",
                "track_name": "Song B", 
                "artist_name": "Artist 2",
                "energy": 0.9,
                "valence": 0.5,
                "tempo": 130.0,
                "danceability": 0.8
            },
            {
                "track_id": "track_3",
                "track_name": "Song C",
                "artist_name": "Artist 3",
                "energy": 0.2,
                "valence": 0.9,
                "tempo": 80.0,
                "danceability": 0.3
            }
        ])

    def test_graph_creation(self, sample_data):
        """Test basic graph creation."""
        features = ["energy", "valence", "tempo", "danceability"]
        graph = SimilaritySongGraph(sample_data, features)
        
        assert len(graph.nodes) == 3
        assert "track_1" in graph.nodes
        assert "track_2" in graph.nodes  
        assert "track_3" in graph.nodes

    def test_similarity_calculation(self, sample_data):
        """Test that similar tracks are connected."""
        features = ["energy", "valence"]
        graph = SimilaritySongGraph(sample_data, features, threshold=0.5)
        
        # track_1 and track_2 should be more similar (both high energy)
        # than track_1 and track_3 (very different energy levels)
        
        # Check that edges exist for similar tracks
        assert graph.has_edge("track_1", "track_2")
        
        # Get similarity score
        similarity = graph.get_edge_similarity("track_1", "track_2")
        assert similarity is not None
        assert similarity > 0.5

    def test_get_similar_tracks(self, sample_data):
        """Test retrieving similar tracks."""
        features = ["energy", "valence"]
        graph = SimilaritySongGraph(sample_data, features, threshold=0.3)
        
        similar_tracks = graph.get_similar_tracks("track_1", limit=2)
        
        assert len(similar_tracks) <= 2
        assert all(isinstance(track, dict) for track in similar_tracks)
        assert all("track_id" in track for track in similar_tracks)
        assert all("similarity" in track for track in similar_tracks)

    def test_threshold_filtering(self, sample_data):
        """Test that threshold properly filters connections."""
        features = ["energy", "valence"]
        
        # High threshold - fewer connections
        strict_graph = SimilaritySongGraph(sample_data, features, threshold=0.9)
        strict_edges = len(strict_graph.edges)
        
        # Low threshold - more connections
        loose_graph = SimilaritySongGraph(sample_data, features, threshold=0.1)
        loose_edges = len(loose_graph.edges)
        
        assert loose_edges >= strict_edges

    def test_empty_features(self, sample_data):
        """Test graph creation with no features."""
        graph = SimilaritySongGraph(sample_data, [])
        
        # Should still create nodes but no edges
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 0

    def test_invalid_track_id(self, sample_data):
        """Test querying for non-existent track."""
        features = ["energy", "valence"]
        graph = SimilaritySongGraph(sample_data, features)
        
        similar_tracks = graph.get_similar_tracks("nonexistent_track")
        assert similar_tracks == []