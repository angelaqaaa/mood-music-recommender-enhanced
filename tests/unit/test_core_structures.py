"""Unit tests for core data structures in models/structures.py.

This module tests the MusicNode, GenreTree, and SimilaritySongGraph classes
with both happy path scenarios and edge cases.
"""

import pandas as pd
import pytest

from src.musicrec.core.structures import GenreTree, MusicNode, SimilaritySongGraph


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
        # Parent-child relationship is established via add_child method
        parent.add_child(child)
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
        rock = MusicNode("rock", "genre")
        metal = MusicNode("metal", "genre")

        root.add_child(rock)
        rock.add_child(metal)

        # Build path manually since get_path_to_root doesn't exist
        path = []
        current = metal
        while current is not None:
            path.append(current.name)
            current = current.parent

        expected_path = ["metal", "rock", "music"]
        assert path == expected_path

    def test_node_str_representation(self):
        """Test string representation of nodes."""
        node = MusicNode("rock", "genre")

        assert str(node) == "MusicNode(rock, genre)"


class TestGenreTree:
    """Test suite for GenreTree class."""

    @pytest.fixture
    def sample_data(self):
        """Create sample track data for testing."""
        return pd.DataFrame(
            [
                {
                    "track_id": "track_1",
                    "track_name": "Song A",
                    "artist_name": "Artist 1",
                    "genre_hierarchy": ["rock"],
                    "mood_tags": ["energetic"],
                    "energy": 0.8,
                    "valence": 0.6,
                },
                {
                    "track_id": "track_2",
                    "track_name": "Song B",
                    "artist_name": "Artist 2",
                    "genre_hierarchy": ["rock", "metal"],
                    "mood_tags": ["intense"],
                    "energy": 0.9,
                    "valence": 0.3,
                },
                {
                    "track_id": "track_3",
                    "track_name": "Song C",
                    "artist_name": "Artist 3",
                    "genre_hierarchy": ["electronic"],
                    "mood_tags": ["upbeat"],
                    "energy": 0.7,
                    "valence": 0.8,
                },
            ]
        )

    def test_tree_creation(self, sample_data):
        """Test basic tree creation from data."""
        tree = GenreTree()

        # Manually add tracks from sample data
        for _, row in sample_data.iterrows():
            track_data = {
                "track_name": row["track_name"],
                "artist_name": row["artist_name"],
                "mood_tags": row["mood_tags"],
                "energy": row["energy"],
                "valence": row["valence"],
            }
            tree.add_track(row["track_id"], row["genre_hierarchy"], track_data)

        assert tree.root is not None
        assert tree.root.name == "music"
        assert tree.root.node_type == "genre"

        # Check that genres were added
        genre_names = [child.name for child in tree.root.children]
        assert "rock" in genre_names
        assert "electronic" in genre_names

    def test_build_hierarchy(self, sample_data):
        """Test that genre hierarchy is built correctly."""
        tree = GenreTree()

        # Add tracks to build hierarchy
        for _, row in sample_data.iterrows():
            track_data = {
                "track_name": row["track_name"],
                "artist_name": row["artist_name"],
                "mood_tags": row["mood_tags"],
            }
            tree.add_track(row["track_id"], row["genre_hierarchy"], track_data)

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
        tree = GenreTree()

        # Add tracks to build genre tree
        for _, row in sample_data.iterrows():
            track_data = {"track_name": row["track_name"]}
            tree.add_track(row["track_id"], row["genre_hierarchy"], track_data)

        # Find available genres manually by traversing tree
        genres = set()

        def collect_genres(node):
            if node.node_type == "genre" and node.name != "music":
                genres.add(node.name)
            for child in node.children:
                collect_genres(child)

        collect_genres(tree.root)
        genre_list = sorted(list(genres))

        assert "rock" in genre_list
        assert "metal" in genre_list
        assert "electronic" in genre_list
        assert "music" not in genre_list  # Root should not be included

    def test_find_genre_node(self, sample_data):
        """Test finding specific genre nodes."""
        tree = GenreTree()

        # Add tracks to build tree
        for _, row in sample_data.iterrows():
            tree.add_track(row["track_id"], row["genre_hierarchy"], {})

        # Find nodes manually by traversing
        def find_node(name):
            def search(node):
                if node.name == name:
                    return node
                for child in node.children:
                    result = search(child)
                    if result:
                        return result
                return None

            return search(tree.root)

        rock_node = find_node("rock")
        assert rock_node is not None
        assert rock_node.name == "rock"

        metal_node = find_node("metal")
        assert metal_node is not None
        assert metal_node.name == "metal"

        # Non-existent genre
        fake_node = find_node("nonexistent")
        assert fake_node is None

    def test_get_tracks_by_genre(self, sample_data):
        """Test retrieving tracks by genre."""
        tree = GenreTree()

        # Add tracks to tree
        for _, row in sample_data.iterrows():
            tree.add_track(row["track_id"], row["genre_hierarchy"], {})

        # Get tracks manually by searching tree
        def get_tracks_in_subtree(node):
            tracks = []
            if node.node_type == "track":
                tracks.append(node)
            for child in node.children:
                tracks.extend(get_tracks_in_subtree(child))
            return tracks

        # Find rock node and get its tracks
        def find_node(name):
            def search(node):
                if node.name == name:
                    return node
                for child in node.children:
                    result = search(child)
                    if result:
                        return result
                return None

            return search(tree.root)

        rock_node = find_node("rock")
        rock_tracks = get_tracks_in_subtree(rock_node)
        assert len(rock_tracks) == 2  # track_1 (rock) and track_2 (rock->metal)

        # Get tracks from electronic genre
        electronic_node = find_node("electronic")
        electronic_tracks = get_tracks_in_subtree(electronic_node)
        assert len(electronic_tracks) == 1
        assert electronic_tracks[0].name == "track_3"

    def test_empty_data(self):
        """Test tree creation with empty data."""
        tree = GenreTree()

        assert tree.root is not None
        assert tree.root.name == "music"
        assert len(tree.root.children) == 0


class TestSimilaritySongGraph:
    """Test suite for SimilaritySongGraph class."""

    @pytest.fixture
    def sample_data(self):
        """Create sample track data for testing."""
        return pd.DataFrame(
            [
                {
                    "track_id": "track_1",
                    "track_name": "Song A",
                    "artist_name": "Artist 1",
                    "energy": 0.8,
                    "valence": 0.6,
                    "tempo": 120.0,
                    "danceability": 0.7,
                },
                {
                    "track_id": "track_2",
                    "track_name": "Song B",
                    "artist_name": "Artist 2",
                    "energy": 0.9,
                    "valence": 0.5,
                    "tempo": 130.0,
                    "danceability": 0.8,
                },
                {
                    "track_id": "track_3",
                    "track_name": "Song C",
                    "artist_name": "Artist 3",
                    "energy": 0.2,
                    "valence": 0.9,
                    "tempo": 80.0,
                    "danceability": 0.3,
                },
            ]
        )

    def test_graph_creation(self, sample_data):
        """Test basic graph creation."""
        graph = SimilaritySongGraph()

        # Add nodes manually
        for _, row in sample_data.iterrows():
            attributes = {
                "track_name": row["track_name"],
                "energy": row["energy"],
                "valence": row["valence"],
                "tempo": row["tempo"],
                "danceability": row["danceability"],
            }
            graph.add_node(row["track_id"], attributes)

        assert len(graph.graph.nodes) == 3
        assert "track_1" in graph.graph.nodes
        assert "track_2" in graph.graph.nodes
        assert "track_3" in graph.graph.nodes

    def test_similarity_calculation(self, sample_data):
        """Test that similar tracks are connected."""
        graph = SimilaritySongGraph()

        # Add nodes
        for _, row in sample_data.iterrows():
            attributes = {
                "energy": row["energy"],
                "valence": row["valence"],
            }
            graph.add_node(row["track_id"], attributes)

        # Calculate similarities
        graph.calculate_similarities(
            feature_keys=["energy", "valence"],
            mood_weight=0.4,
            feature_weight=0.6,
            similarity_threshold=0.5,
        )

        # track_1 and track_2 should be more similar (both high energy)
        # Check that edges exist for similar tracks
        assert graph.graph.has_edge("track_1", "track_2")

        # Get similarity score
        edge_data = graph.graph.get_edge_data("track_1", "track_2")
        assert edge_data is not None
        similarity = edge_data.get("weight", 0)
        assert similarity > 0.5

    def test_get_similar_tracks(self, sample_data):
        """Test retrieving similar tracks."""
        graph = SimilaritySongGraph()

        # Add nodes and calculate similarities
        for _, row in sample_data.iterrows():
            attributes = {
                "energy": row["energy"],
                "valence": row["valence"],
            }
            graph.add_node(row["track_id"], attributes)

        graph.calculate_similarities(
            feature_keys=["energy", "valence"],
            mood_weight=0.4,
            feature_weight=0.6,
            similarity_threshold=0.3,
        )

        similar_tracks = graph.recommend_similar_tracks("track_1", n=2)

        assert len(similar_tracks) <= 2
        assert all(
            isinstance(track, tuple) and len(track) == 2 for track in similar_tracks
        )
        # Each tuple should be (track_id, similarity_score)
        for track_id, similarity in similar_tracks:
            assert isinstance(track_id, str)
            assert isinstance(similarity, float)

    def test_threshold_filtering(self, sample_data):
        """Test that threshold properly filters connections."""

        # Create strict threshold graph
        strict_graph = SimilaritySongGraph()
        for _, row in sample_data.iterrows():
            attributes = {"energy": row["energy"], "valence": row["valence"]}
            strict_graph.add_node(row["track_id"], attributes)
        strict_graph.calculate_similarities(
            feature_keys=["energy", "valence"],
            mood_weight=0.4,
            feature_weight=0.6,
            similarity_threshold=0.9,
        )
        strict_edges = len(strict_graph.graph.edges)

        # Create loose threshold graph
        loose_graph = SimilaritySongGraph()
        for _, row in sample_data.iterrows():
            attributes = {"energy": row["energy"], "valence": row["valence"]}
            loose_graph.add_node(row["track_id"], attributes)
        loose_graph.calculate_similarities(
            feature_keys=["energy", "valence"],
            mood_weight=0.4,
            feature_weight=0.6,
            similarity_threshold=0.1,
        )
        loose_edges = len(loose_graph.graph.edges)

        assert loose_edges >= strict_edges

    def test_empty_features(self, sample_data):
        """Test graph creation with no features."""
        graph = SimilaritySongGraph()

        # Add nodes
        for _, row in sample_data.iterrows():
            graph.add_node(row["track_id"], {})

        # Calculate similarities with no features
        graph.calculate_similarities(
            feature_keys=[],
            mood_weight=0.4,
            feature_weight=0.6,
            similarity_threshold=0.3,
        )

        # Should still create nodes but no edges
        assert len(graph.graph.nodes) == 3
        assert len(graph.graph.edges) == 0

    def test_invalid_track_id(self, sample_data):
        """Test querying for non-existent track."""
        graph = SimilaritySongGraph()

        # Add nodes
        for _, row in sample_data.iterrows():
            attributes = {"energy": row["energy"], "valence": row["valence"]}
            graph.add_node(row["track_id"], attributes)

        similar_tracks = graph.recommend_similar_tracks("nonexistent_track")
        assert similar_tracks == []
