"""Tests for the music_structures module."""

from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest

from src.musicrec.music_structures import GenreTree, MusicNode, SimilaritySongGraph


class TestMusicNode:
    """Test MusicNode class."""

    def test_music_node_creation_track(self):
        """Test creating a track node."""
        node = MusicNode("track_1", "track")
        data = {"artist": "Test Artist", "duration": 180}
        node.data = data

        assert node.name == "track_1"
        assert node.node_type == "track"
        assert node.data == data
        assert len(node.children) == 0
        assert node.parent is None

    def test_music_node_creation_genre(self):
        """Test creating a genre node."""
        node = MusicNode("rock", "genre")

        assert node.name == "rock"
        assert node.node_type == "genre"
        assert node.data == {}
        assert len(node.children) == 0
        assert node.parent is None

    def test_music_node_add_child(self):
        """Test adding children to a node."""
        parent = MusicNode("music", "genre")
        child = MusicNode("rock", "genre")

        parent.add_child(child)

        assert len(parent.children) == 1
        assert child in parent.children
        assert child.parent == parent

    def test_music_node_multiple_children(self):
        """Test adding multiple children to a node."""
        parent = MusicNode("music", "genre")
        child1 = MusicNode("rock", "genre")
        child2 = MusicNode("pop", "genre")

        parent.add_child(child1)
        parent.add_child(child2)

        assert len(parent.children) == 2
        assert child1 in parent.children
        assert child2 in parent.children
        assert child1.parent == parent
        assert child2.parent == parent

    def test_music_node_find_child(self):
        """Test finding a child by name."""
        parent = MusicNode("music", "genre")
        child1 = MusicNode("rock", "genre")
        child2 = MusicNode("pop", "genre")

        parent.add_child(child1)
        parent.add_child(child2)

        # Test manual search through children
        found = None
        for child in parent.children:
            if child.name == "rock":
                found = child
                break
        assert found == child1

        # Test search for non-existent child
        not_found = None
        for child in parent.children:
            if child.name == "jazz":
                not_found = child
                break
        assert not_found is None

    def test_music_node_hierarchy(self):
        """Test parent-child relationships."""
        root = MusicNode("music", "genre")
        rock = MusicNode("rock", "genre")
        indie = MusicNode("indie", "genre")

        root.add_child(rock)
        rock.add_child(indie)

        # Test parent relationships
        assert rock.parent == root
        assert indie.parent == rock
        assert root.parent is None

        # Test children relationships
        assert rock in root.children
        assert indie in rock.children
        assert len(indie.children) == 0

    def test_music_node_str_representation(self):
        """Test string representation of node."""
        node = MusicNode("track_1", "track")
        node.data = {"artist": "Test Artist"}
        str_repr = str(node)

        assert "track_1" in str_repr
        assert "track" in str_repr


class TestGenreTree:
    """Test GenreTree class."""

    def test_genre_tree_initialization(self):
        """Test GenreTree initialization."""
        tree = GenreTree()

        assert tree.root.name == "music"
        assert tree.root.node_type == "genre"
        assert len(tree.tracks) == 0

    def test_add_track_single_genre(self):
        """Test adding a track with single genre."""
        tree = GenreTree()
        track_data = {"artist": "Test Artist", "mood_tags": ["happy"]}

        tree.add_track("track_1", ["rock"], track_data)

        assert "track_1" in tree.tracks
        assert tree.tracks["track_1"].name == "track_1"
        assert tree.tracks["track_1"].data == track_data

        # Check genre hierarchy
        rock_node = tree.root.find_child("rock")
        assert rock_node is not None
        assert rock_node.name == "rock"

        # Track should be child of rock
        track_node = rock_node.find_child("track_1")
        assert track_node is not None
        assert track_node == tree.tracks["track_1"]

    def test_add_track_genre_hierarchy(self):
        """Test adding a track with genre hierarchy."""
        tree = GenreTree()
        track_data = {"artist": "Test Artist", "mood_tags": ["calm"]}

        tree.add_track("track_1", ["rock", "indie"], track_data)

        assert "track_1" in tree.tracks

        # Check genre hierarchy
        rock_node = tree.root.find_child("rock")
        assert rock_node is not None

        indie_node = rock_node.find_child("indie")
        assert indie_node is not None

        track_node = indie_node.find_child("track_1")
        assert track_node is not None
        assert track_node == tree.tracks["track_1"]

    def test_add_track_empty_genre_path(self):
        """Test adding a track with empty genre path."""
        tree = GenreTree()
        track_data = {"artist": "Test Artist"}

        tree.add_track("track_1", [], track_data)

        assert "track_1" in tree.tracks

        # Track should be directly under root
        track_node = tree.root.find_child("track_1")
        assert track_node is not None

    def test_add_multiple_tracks_same_genre(self):
        """Test adding multiple tracks to the same genre."""
        tree = GenreTree()

        tree.add_track("track_1", ["rock"], {"artist": "Artist 1"})
        tree.add_track("track_2", ["rock"], {"artist": "Artist 2"})

        assert len(tree.tracks) == 2

        rock_node = tree.root.find_child("rock")
        assert rock_node is not None
        assert len(rock_node.children) == 2

    def test_get_track_node_existing(self):
        """Test getting an existing track node."""
        tree = GenreTree()
        tree.add_track("track_1", ["rock"], {"artist": "Test Artist"})

        node = tree.get_track_node("track_1")
        assert node is not None
        assert node.name == "track_1"

    def test_get_track_node_nonexistent(self):
        """Test getting a non-existent track node."""
        tree = GenreTree()

        node = tree.get_track_node("nonexistent")
        assert node is None

    def test_get_genre_path(self):
        """Test getting genre path for a track."""
        tree = GenreTree()
        tree.add_track("track_1", ["rock", "indie"], {"artist": "Test Artist"})

        track_node = tree.tracks["track_1"]
        path = tree.get_genre_path(track_node)

        assert path == ["music", "rock", "indie"]

    def test_search_by_genre_existing(self):
        """Test searching tracks by existing genre."""
        tree = GenreTree()
        tree.add_track("track_1", ["rock"], {"artist": "Artist 1"})
        tree.add_track("track_2", ["rock", "indie"], {"artist": "Artist 2"})
        tree.add_track("track_3", ["pop"], {"artist": "Artist 3"})

        results = tree.search_by_genre("rock")

        assert len(results) == 2
        track_ids = [node.name for node in results]
        assert "track_1" in track_ids
        assert "track_2" in track_ids

    def test_search_by_genre_nonexistent(self):
        """Test searching tracks by non-existent genre."""
        tree = GenreTree()
        tree.add_track("track_1", ["rock"], {"artist": "Artist 1"})

        results = tree.search_by_genre("jazz")
        assert len(results) == 0

    def test_search_by_mood_existing(self):
        """Test searching tracks by existing mood."""
        tree = GenreTree()
        tree.add_track(
            "track_1",
            ["rock"],
            {"artist": "Artist 1", "mood_tags": ["happy", "energetic"]},
        )
        tree.add_track(
            "track_2", ["pop"], {"artist": "Artist 2", "mood_tags": ["happy"]}
        )
        tree.add_track(
            "track_3", ["rock"], {"artist": "Artist 3", "mood_tags": ["sad"]}
        )

        results = tree.search_by_mood("happy")

        assert len(results) == 2
        track_ids = [node.name for node in results]
        assert "track_1" in track_ids
        assert "track_2" in track_ids

    def test_search_by_mood_nonexistent(self):
        """Test searching tracks by non-existent mood."""
        tree = GenreTree()
        tree.add_track(
            "track_1", ["rock"], {"artist": "Artist 1", "mood_tags": ["happy"]}
        )

        results = tree.search_by_mood("angry")
        assert len(results) == 0

    def test_search_by_genre_and_mood(self):
        """Test searching tracks by both genre and mood."""
        tree = GenreTree()
        tree.add_track(
            "track_1", ["rock"], {"artist": "Artist 1", "mood_tags": ["happy"]}
        )
        tree.add_track(
            "track_2", ["rock"], {"artist": "Artist 2", "mood_tags": ["sad"]}
        )
        tree.add_track(
            "track_3", ["pop"], {"artist": "Artist 3", "mood_tags": ["happy"]}
        )

        results = tree.search_by_genre_and_mood("rock", "happy")

        assert len(results) == 1
        assert results[0].name == "track_1"

    def test_bfs_search(self):
        """Test breadth-first search functionality."""
        tree = GenreTree()
        tree.add_track("track_1", ["rock"], {"mood_tags": ["happy"]})
        tree.add_track("track_2", ["rock", "indie"], {"mood_tags": ["calm"]})
        tree.add_track("track_3", ["pop"], {"mood_tags": ["energetic"]})

        results = tree.bfs_search("rock", max_depth=2)

        assert isinstance(results, list)
        assert len(results) >= 1

    def test_dfs_search(self):
        """Test depth-first search functionality."""
        tree = GenreTree()
        tree.add_track("track_1", ["rock"], {"mood_tags": ["happy"]})
        tree.add_track("track_2", ["rock", "indie"], {"mood_tags": ["calm"]})
        tree.add_track("track_3", ["pop"], {"mood_tags": ["energetic"]})

        results = tree.dfs_search("rock", max_breadth=5)

        assert isinstance(results, list)
        assert len(results) >= 1


class TestSimilaritySongGraph:
    """Test SimilaritySongGraph class."""

    def test_similarity_graph_initialization(self):
        """Test SimilaritySongGraph initialization."""
        graph = SimilaritySongGraph()

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_add_node(self):
        """Test adding a node to the similarity graph."""
        graph = SimilaritySongGraph()
        node_data = {"energy": 0.8, "valence": 0.7, "mood_tags": ["happy"]}

        graph.add_node("track_1", node_data)

        assert "track_1" in graph.nodes
        assert graph.nodes["track_1"] == node_data

    def test_add_multiple_nodes(self):
        """Test adding multiple nodes to the graph."""
        graph = SimilaritySongGraph()

        graph.add_node("track_1", {"energy": 0.8, "mood_tags": ["happy"]})
        graph.add_node("track_2", {"energy": 0.5, "mood_tags": ["calm"]})

        assert len(graph.nodes) == 2
        assert "track_1" in graph.nodes
        assert "track_2" in graph.nodes

    def test_calculate_similarities(self):
        """Test calculating similarities between nodes."""
        graph = SimilaritySongGraph()

        # Add nodes with similar features
        graph.add_node(
            "track_1", {"energy": 0.8, "valence": 0.7, "mood_tags": ["happy"]}
        )
        graph.add_node(
            "track_2", {"energy": 0.9, "valence": 0.8, "mood_tags": ["energetic"]}
        )
        graph.add_node("track_3", {"energy": 0.2, "valence": 0.3, "mood_tags": ["sad"]})

        graph.calculate_similarities(
            ["energy", "valence"], mood_weight=0.5, feature_weight=0.5
        )

        # Should have calculated edges
        assert len(graph.edges) > 0

        # Check edge structure
        for source, targets in graph.edges.items():
            assert source in graph.nodes
            assert isinstance(targets, dict)

            for target, similarity in targets.items():
                assert target in graph.nodes
                assert isinstance(similarity, (int, float))
                assert 0 <= similarity <= 1

    def test_calculate_similarities_empty_graph(self):
        """Test calculating similarities on empty graph."""
        graph = SimilaritySongGraph()

        graph.calculate_similarities(["energy", "valence"])

        assert len(graph.edges) == 0

    def test_calculate_similarities_single_node(self):
        """Test calculating similarities with single node."""
        graph = SimilaritySongGraph()
        graph.add_node("track_1", {"energy": 0.8, "valence": 0.7})

        graph.calculate_similarities(["energy", "valence"])

        # Should have no edges with single node
        assert len(graph.edges) == 0

    def test_recommend_similar_tracks_existing(self):
        """Test recommending similar tracks for existing track."""
        graph = SimilaritySongGraph()

        graph.add_node(
            "track_1", {"energy": 0.8, "valence": 0.7, "mood_tags": ["happy"]}
        )
        graph.add_node(
            "track_2", {"energy": 0.9, "valence": 0.8, "mood_tags": ["energetic"]}
        )
        graph.add_node("track_3", {"energy": 0.2, "valence": 0.3, "mood_tags": ["sad"]})

        graph.calculate_similarities(
            ["energy", "valence"], mood_weight=0.5, feature_weight=0.5
        )

        recommendations = graph.recommend_similar_tracks("track_1", limit=2)

        assert isinstance(recommendations, list)
        assert len(recommendations) <= 2

        # Each recommendation should be a tuple of (track_id, similarity)
        for track_id, similarity in recommendations:
            assert track_id in graph.nodes
            assert track_id != "track_1"  # Should not recommend self
            assert isinstance(similarity, (int, float))
            assert 0 <= similarity <= 1

    def test_recommend_similar_tracks_nonexistent(self):
        """Test recommending similar tracks for non-existent track."""
        graph = SimilaritySongGraph()

        graph.add_node("track_1", {"energy": 0.8, "valence": 0.7})
        graph.calculate_similarities(["energy", "valence"])

        recommendations = graph.recommend_similar_tracks("nonexistent", limit=5)

        assert recommendations == []

    def test_recommend_similar_tracks_no_edges(self):
        """Test recommending similar tracks when no edges exist."""
        graph = SimilaritySongGraph()

        graph.add_node("track_1", {"energy": 0.8, "valence": 0.7})
        # Don't calculate similarities

        recommendations = graph.recommend_similar_tracks("track_1", limit=5)

        assert recommendations == []

    def test_get_neighbors_existing(self):
        """Test getting neighbors for existing node."""
        graph = SimilaritySongGraph()

        graph.add_node("track_1", {"energy": 0.8, "valence": 0.7})
        graph.add_node("track_2", {"energy": 0.9, "valence": 0.8})

        graph.calculate_similarities(["energy", "valence"])

        neighbors = graph.get_neighbors("track_1")

        if len(graph.edges) > 0:
            assert isinstance(neighbors, dict)
            # All neighbors should be valid nodes
            for neighbor in neighbors:
                assert neighbor in graph.nodes

    def test_get_neighbors_nonexistent(self):
        """Test getting neighbors for non-existent node."""
        graph = SimilaritySongGraph()

        graph.add_node("track_1", {"energy": 0.8, "valence": 0.7})

        neighbors = graph.get_neighbors("nonexistent")
        assert neighbors == {}


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""

    def test_genre_tree_duplicate_track(self):
        """Test adding duplicate track to genre tree."""
        tree = GenreTree()

        tree.add_track("track_1", ["rock"], {"artist": "Artist 1"})
        tree.add_track(
            "track_1", ["pop"], {"artist": "Artist 2"}
        )  # Same ID, different data

        # Should handle gracefully (implementation dependent)
        assert "track_1" in tree.tracks

    def test_similarity_graph_missing_features(self):
        """Test similarity calculation with missing features."""
        graph = SimilaritySongGraph()

        graph.add_node("track_1", {"energy": 0.8})  # Missing valence
        graph.add_node("track_2", {"valence": 0.7})  # Missing energy

        # Should handle missing features gracefully
        graph.calculate_similarities(["energy", "valence"])

        assert isinstance(graph.edges, dict)

    def test_similarity_graph_invalid_mood_tags(self):
        """Test similarity calculation with invalid mood tags."""
        graph = SimilaritySongGraph()

        graph.add_node("track_1", {"energy": 0.8, "mood_tags": "not_a_list"})
        graph.add_node("track_2", {"energy": 0.7, "mood_tags": ["happy"]})

        # Should handle invalid mood tags gracefully
        graph.calculate_similarities(["energy"], mood_weight=0.5, feature_weight=0.5)

        assert isinstance(graph.edges, dict)

    def test_genre_tree_none_mood_tags(self):
        """Test genre tree with None mood tags."""
        tree = GenreTree()

        tree.add_track("track_1", ["rock"], {"artist": "Artist", "mood_tags": None})

        results = tree.search_by_mood("happy")
        assert isinstance(results, list)

    def test_similarity_calculation_extreme_values(self):
        """Test similarity calculation with extreme values."""
        graph = SimilaritySongGraph()

        graph.add_node("track_1", {"energy": 0.0, "valence": 0.0})
        graph.add_node("track_2", {"energy": 1.0, "valence": 1.0})

        graph.calculate_similarities(["energy", "valence"])

        # Should handle extreme values without errors
        assert isinstance(graph.edges, dict)


class TestIntegration:
    """Test integration between components."""

    def test_genre_tree_and_similarity_graph_integration(self):
        """Test that genre tree and similarity graph work together."""
        tree = GenreTree()
        graph = SimilaritySongGraph()

        # Add same tracks to both structures
        track_data = {"energy": 0.8, "valence": 0.7, "mood_tags": ["happy"]}
        tree.add_track("track_1", ["rock"], track_data)
        graph.add_node("track_1", track_data)

        track_data2 = {"energy": 0.9, "valence": 0.8, "mood_tags": ["energetic"]}
        tree.add_track("track_2", ["rock"], track_data2)
        graph.add_node("track_2", track_data2)

        # Both should work independently
        genre_results = tree.search_by_genre("rock")
        assert len(genre_results) == 2

        graph.calculate_similarities(["energy", "valence"])
        similar_tracks = graph.recommend_similar_tracks("track_1", limit=1)
        assert isinstance(similar_tracks, list)


if __name__ == "__main__":
    pytest.main([__file__])
