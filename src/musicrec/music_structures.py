"""CSC111 Winter 2025: A Mood-Driven Music Recommender with Genre Hierarchies

Module for defining the core data structures of the music recommender system.
This module contains the implementation of the Genre Tree and Song Similarity Graph.

Copyright and Usage Information
===============================
This file is Copyright (c) 2025 Qian (Angela) Su & Mengxuan (Connie) Guo.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from sklearn.metrics.pairwise import cosine_similarity
import python_ta


class MusicNode:
    """A node in the genre hierarchy tree.

    Instance Attributes:
        - name: The name of the node (genre or track_id)
        - node_type: Either 'genre' or 'track'
        - parent: The parent node in the hierarchy
        - children: List of child nodes
        - data: Dictionary for storing track attributes (for track nodes)

    Representation Invariants:
        - self.node_type in {'genre', 'track'}
        - if self.node_type == 'track' and self.parent is not None:
              self.parent.node_type == 'genre'
        - if self.node_type == 'genre':
              all(child.parent is self for child in self.children)
    """

    name: str
    node_type: str
    parent: Optional['MusicNode']
    children: List['MusicNode']
    data: Dict[str, Any]

    def __init__(self, name: str, node_type: str = 'genre', parent: Optional['MusicNode'] = None) -> None:
        """Initialize a music node.

        Args:
            name: The name of the node (genre or track_id)
            node_type: Either 'genre' or 'track'
            parent: The parent node in the hierarchy

        Preconditions:
            - node_type in {'genre', 'track'}
        """
        self.name = name
        self.node_type = node_type
        self.parent = parent
        self.children = []
        self.data = {}  # For storing track attributes like mood, valence, etc.

    def add_child(self, child: 'MusicNode') -> None:
        """Add a child node to this node.

        Args:
            child: The child node to add
        """
        self.children.append(child)
        child.parent = self

    def __repr__(self) -> str:
        """Return a string representation of this node."""
        return f"MusicNode({self.name}, {self.node_type})"


class GenreTree:
    """A tree representation of genre hierarchy with tracks as leaves.

    Instance Attributes:
        - root: The root node of the tree (typically 'music')
        - tracks: Dictionary mapping track_ids to their nodes for quick access
    """

    root: MusicNode
    tracks: Dict[str, MusicNode]

    def __init__(self) -> None:
        """Initialize the genre tree with a root 'music' node."""
        self.root = MusicNode('music', 'genre')
        self.tracks = {}  # Maps track_id to its node for quick access

    def add_genre(self, genre_path: List[str]) -> MusicNode:
        """Add a genre hierarchy path to the tree.

        Args:
            genre_path: List of genres in hierarchical order (e.g., ['rock', 'alternative'])

        Returns:
            The leaf genre node

        >>> tree = GenreTree()
        >>> rock_node = tree.add_genre(['rock'])
        >>> rock_node.name
        'rock'
        >>> alt_rock_node = tree.add_genre(['rock', 'alternative'])
        >>> alt_rock_node.name
        'alternative'
        >>> alt_rock_node.parent.name
        'rock'
        """
        current = self.root

        for genre in genre_path:
            # Check if this genre already exists as a child
            found = False
            for child in current.children:
                if child.name == genre and child.node_type == 'genre':
                    current = child
                    found = True
                    break

            # If not found, create a new genre node
            if not found:
                new_node = MusicNode(genre, 'genre', current)
                current.add_child(new_node)
                current = new_node

        return current

    def add_track(self, track_id: str, genre_path: List[str], track_data: Dict[str, Any]) -> MusicNode:
        """Add a track to the tree under the specified genre path.

        Args:
            track_id: The unique identifier for the track
            genre_path: The genre hierarchy path (e.g., ['rock', 'alternative'])
            track_data: Dictionary of track attributes (mood, audio features, etc.)

        Returns:
            The track node

        >>> tree = GenreTree()
        >>> track_node = tree.add_track('track_001', ['rock', 'alternative'], {'mood_tags': ['energetic']})
        >>> track_node.name
        'track_001'
        >>> track_node.node_type
        'track'
        >>> track_node.data['mood_tags']
        ['energetic']
        >>> tree.get_genre_path(track_node)
        ['rock', 'alternative']
        """
        # First ensure the genre path exists
        genre_node = self.add_genre(genre_path)

        # Create the track node
        new_track_node = MusicNode(track_id, 'track', genre_node)
        new_track_node.data = track_data

        # Add the track as a child of the genre
        genre_node.add_child(new_track_node)

        # Store reference to the track
        self.tracks[track_id] = new_track_node

        return new_track_node

    def get_track_node(self, track_id: str) -> Optional[MusicNode]:
        """Get a track node by its ID.

        Args:
            track_id: The track ID to look up

        Returns:
            The track node if found, None otherwise
        """
        return self.tracks.get(track_id)

    def get_genre_path(self, node: MusicNode) -> List[str]:
        """Get the full genre path for a node.

        Args:
            node: The node to get the genre path for

        Returns:
            List of genre names from root to the node's parent genre
        """
        path = []
        current = node

        # Traverse up to the root, collecting genre names
        while current and current.parent:
            if current.node_type == 'genre':
                path.append(current.name)
            current = current.parent

        # Reverse to get from root to leaf
        path.reverse()
        return path

    def search_by_genre(self, genre: str) -> List[MusicNode]:
        """Find all tracks under a specified genre (at any level).

        Args:
            genre: The genre to search for

        Returns:
            List of track nodes
        """
        results = []

        def dfs(node: MusicNode) -> None:
            """Depth-first search helper to find genre nodes."""
            if node.node_type == 'genre' and node.name == genre:
                # Found the genre, collect all track descendants
                collect_tracks(node, results)
            else:
                # Continue searching
                for child in node.children:
                    dfs(child)

        def collect_tracks(node: MusicNode, track_list: List[MusicNode]) -> None:
            """Helper function to collect all track nodes beneath a given node."""
            if node.node_type == 'track':
                track_list.append(node)
            else:
                for child in node.children:
                    collect_tracks(child, track_list)

        dfs(self.root)
        return results

    def search_by_mood(self, mood: str) -> List[MusicNode]:
        """Find all tracks with a specific mood tag.

        Args:
            mood: The mood to search for

        Returns:
            List of track nodes
        """
        results = []

        for _, node in self.tracks.items():
            # Check if the mood is in the track's mood tags
            if 'mood_tags' in node.data and mood in node.data['mood_tags']:
                results.append(node)

        return results

    def search_by_genre_and_mood(self, genre: str, mood: str) -> List[MusicNode]:
        """Find all tracks with both a specific genre and mood.

        Args:
            genre: The genre to search for
            mood: The mood to search for

        Returns:
            List of track nodes
        """
        genre_results = self.search_by_genre(genre)

        # Filter by mood
        return [node for node in genre_results
                if 'mood_tags' in node.data and mood in node.data['mood_tags']]

    def bfs_search(self, start_genre: str, mood: Optional[str] = None, max_depth: int = 2) -> List[MusicNode]:
        """Perform breadth-first search from a genre node, optionally filtering by mood.

        Args:
            start_genre: The genre to start search from
            mood: Optional mood to filter by
            max_depth: Maximum depth to search (to limit exploration breadth)

        Returns:
            List of track nodes in BFS order
        """
        # Find the start genre node
        def find_genre(curr_node: MusicNode, target: str) -> Optional[MusicNode]:
            """Find a genre node by name using recursive DFS."""
            if curr_node.node_type == 'genre' and curr_node.name == target:
                return curr_node

            for curr_child in curr_node.children:
                result = find_genre(curr_child, target)
                if result:
                    return result

            return None

        found_node = find_genre(self.root, start_genre)
        if not found_node:
            return []

        # Initialize BFS
        queue = [(found_node, 0)]  # (node, depth)
        visited = set()
        results = []

        while queue:
            curr, depth = queue.pop(0)

            if curr in visited or depth > max_depth:
                continue

            visited.add(curr)

            # If it's a track and matches the mood filter (if provided)
            if curr.node_type == 'track':
                if mood is None or ('mood_tags' in curr.data and mood in curr.data['mood_tags']):
                    results.append(curr)

            # Add children to the queue
            for next_child in curr.children:
                queue.append((next_child, depth + 1))

        return results

    def dfs_search(self, start_genre: str, mood: Optional[str] = None, max_breadth: int = 5) -> List[MusicNode]:
        """Perform depth-first search from a genre node, optionally filtering by mood.

        Args:
            start_genre: The genre to start search from
            mood: Optional mood to filter by
            max_breadth: Maximum number of siblings to explore at each level

        Returns:
            List of track nodes in DFS order
        """
        # Find the start genre node
        def find_genre(curr_node: MusicNode, target: str) -> Optional[MusicNode]:
            """Find a genre node by name using recursive DFS."""
            if curr_node.node_type == 'genre' and curr_node.name == target:
                return curr_node

            for curr_child in curr_node.children:
                result = find_genre(curr_child, target)
                if result:
                    return result

            return None

        found_node = find_genre(self.root, start_genre)
        if not found_node:
            return []

        # Initialize DFS
        stack = [found_node]
        visited = set()
        results = []

        while stack:
            curr = stack.pop()

            if curr in visited:
                continue

            visited.add(curr)

            # If it's a track and matches the mood filter (if provided)
            if curr.node_type == 'track':
                if mood is None or ('mood_tags' in curr.data and mood in curr.data['mood_tags']):
                    results.append(curr)

            # Limit breadth by taking only up to max_breadth children
            # Sort to ensure deterministic order
            sorted_children = sorted(curr.children, key=lambda x: x.name)
            for next_child in sorted_children[:max_breadth]:
                stack.append(next_child)

        return results


class SimilaritySongGraph:
    """A graph representation of song similarities based on mood and audio features.

    Instance Attributes:
        - graph: NetworkX graph where nodes are tracks and edges represent similarities
    """

    graph: nx.Graph

    def __init__(self) -> None:
        """Initialize the similarity graph."""
        self.graph = nx.Graph()

    def add_node(self, track_id: str, attributes: Dict[str, Any]) -> None:
        """Add a track node to the graph.

        Args:
            track_id: The unique identifier for the track
            attributes: Dictionary of track attributes (mood, audio features, etc.)
        """
        self.graph.add_node(track_id, **attributes)

    def add_edge(self, track_id1: str, track_id2: str, similarity: float) -> None:
        """Add an edge between two tracks with a similarity weight.

        Args:
            track_id1: First track ID
            track_id2: Second track ID
            similarity: Similarity score between the tracks
        """
        self.graph.add_edge(track_id1, track_id2, weight=similarity)

    def calculate_similarities(self, feature_keys: List[str], mood_weight: float = 0.6,
                               feature_weight: float = 0.4, similarity_threshold: float = 0.5) -> None:
        """Calculate and add similarity edges between all pairs of tracks.

        Args:
            feature_keys: List of audio feature keys to use for similarity
            mood_weight: Weight for mood similarity
            feature_weight: Weight for audio feature similarity
            similarity_threshold: Minimum similarity to create an edge

        Preconditions:
            - 0.0 <= mood_weight <= 1.0
            - 0.0 <= feature_weight <= 1.0
            - mood_weight + feature_weight == 1.0
            - 0.0 <= similarity_threshold <= 1.0
        """
        nodes = list(self.graph.nodes(data=True))
        total_nodes = len(nodes)

        if total_nodes > 500:
            print(f"Warning: Calculating similarities for {total_nodes} tracks. This might take a while.")
            print("Limiting to 500 tracks for faster processing.")
            nodes = nodes[:500]
            total_nodes = 500

        print(f"Calculating similarities between {total_nodes} tracks...")
        edge_count = 0
        comparison_count = 0
        total_comparisons = (total_nodes * (total_nodes - 1)) // 2
        last_percentage = -1

        for i in range(len(nodes)):
            track_id1, attrs1 = nodes[i]

            for j in range(i+1, len(nodes)):
                track_id2, attrs2 = nodes[j]

                # Calculate mood similarity (Jaccard similarity of mood tags)
                mood_sim = 0.0
                if 'mood_tags' in attrs1 and 'mood_tags' in attrs2:
                    mood_tags1 = set(attrs1['mood_tags'])
                    mood_tags2 = set(attrs2['mood_tags'])

                    if mood_tags1 and mood_tags2:  # Ensure non-empty sets
                        intersection = mood_tags1.intersection(mood_tags2)
                        union = mood_tags1.union(mood_tags2)
                        mood_sim = len(intersection) / len(union)

                # Calculate audio feature similarity (cosine similarity)
                feature_sim = 0.0
                valid_features = True

                feature_vector1 = []
                feature_vector2 = []

                for key in feature_keys:
                    if key in attrs1 and key in attrs2:
                        feature_vector1.append(attrs1[key])
                        feature_vector2.append(attrs2[key])
                    else:
                        valid_features = False
                        break

                if valid_features and feature_vector1 and feature_vector2:
                    feature_vec1 = np.array(feature_vector1).reshape(1, -1)
                    feature_vec2 = np.array(feature_vector2).reshape(1, -1)
                    feature_sim = cosine_similarity(feature_vec1, feature_vec2)[0][0]

                # Calculate combined similarity
                combined_sim = (mood_weight * mood_sim) + (feature_weight * feature_sim)

                # Add edge if similarity is above threshold
                if combined_sim >= similarity_threshold:
                    self.add_edge(track_id1, track_id2, combined_sim)
                    edge_count += 1

                comparison_count += 1
                current_percentage = int((comparison_count / total_comparisons) * 100)

                # Print progress every 10%
                if current_percentage % 10 == 0 and current_percentage != last_percentage:
                    print(f"  Similarity calculation: {current_percentage}% complete, {edge_count} connections found")
                    last_percentage = current_percentage

        print(f"✓ Similarity graph created with {edge_count} connections")

    def recommend_similar_tracks(self, track_id: str, n: int = 5) -> List[Tuple[str, float]]:
        """Return up to n most similar tracks to track_id.

        Args:
            track_id: The track ID to find similar tracks for
            n: Maximum number of similar tracks to return

        Returns:
            List of tuples containing (track_id, similarity_score)
        """
        if track_id not in self.graph:
            return []

        # We'll store (neighbor_id_as_str, float_weight)
        neighbors: List[Tuple[str, float]] = []

        for neighbor_id, edge_attrs in self.graph[track_id].items():
            # Cast neighbor_id to string if you are sure it is a string or can be converted
            neighbor_str = str(neighbor_id)

            # Extract the weight as a float
            weight_val = float(edge_attrs.get('weight', 0.0))

            neighbors.append((neighbor_str, weight_val))

        # Sort by similarity descending
        neighbors.sort(key=lambda x: x[1], reverse=True)

        return neighbors[:n]

    def recommend_by_mood(self, mood: str, n: int = 5) -> List[str]:
        """Recommend tracks with a specific mood, prioritizing well-connected nodes.

        Args:
            mood: The mood to filter by
            n: Number of recommendations to return

        Returns:
            List of track_ids

        Preconditions:
            - n >= 1
        """
        # Filter nodes by mood
        mood_nodes = [node for node, attrs in self.graph.nodes(data=True)
                      if 'mood_tags' in attrs and mood in attrs['mood_tags']]

        if not mood_nodes:
            return []

        # Get centrality measure (degree centrality) for all nodes
        centrality = nx.degree_centrality(self.graph)

        # Sort mood nodes by centrality
        mood_nodes_ranked = sorted(mood_nodes, key=lambda x: centrality.get(x, 0), reverse=True)

        return mood_nodes_ranked[:n]


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    python_ta.check_all(config={
        'extra-imports': ['networkx', 'numpy', 'sklearn.metrics.pairwise', 'typing'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['E1136']
    })
