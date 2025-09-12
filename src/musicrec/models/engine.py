"""CSC111 Winter 2025: A Mood-Driven Music Recommender with Genre Hierarchies

Module for managing the recommendation engine of the music recommender system.
This module builds the data structures and implements recommendation algorithms.

Copyright and Usage Information
===============================
This file is Copyright (c) 2025 Qian (Angela) Su.
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Set
# Optional import for CSC111 course linting
try:
    import python_ta
except ImportError:
    python_ta = None

# Import required classes from music_structures
from .music_structures import GenreTree, SimilaritySongGraph, MusicNode


class MusicRecommender:
    """The core recommendation engine for the mood-driven music recommender system.

    This class builds and manages the genre tree and similarity graph, and provides
    various recommendation algorithms.

    Instance Attributes:
        - genre_tree: Tree structure organizing tracks by genre hierarchy
        - similarity_graph: Graph representing track similarities
        - data: The processed DataFrame containing all track data
        - audio_features: List of audio feature column names used for similarity calculation
    """

    genre_tree: GenreTree
    similarity_graph: SimilaritySongGraph
    data: pd.DataFrame
    audio_features: List[str]

    def __init__(self, data: pd.DataFrame, audio_features: Optional[List[str]] = None) -> None:
        """Initialize the music recommender with a processed dataset.

        Args:
            data: The processed DataFrame containing track data
            audio_features: List of audio feature column names to use for similarity
        """
        print("Initializing music recommender...")
        self.data = data

        if audio_features is None:
            # Default audio features to use for similarity
            self.audio_features = ['energy', 'valence', 'tempo']
        else:
            self.audio_features = audio_features

        # Initialize data structures
        print("Creating genre tree and similarity graph...")
        self.genre_tree = GenreTree()
        self.similarity_graph = SimilaritySongGraph()

        # Build the data structures
        self._build_structures()

    def _build_structures(self) -> None:
        """Build the genre tree and similarity graph from the dataset."""
        print(f"Building genre tree with {len(self.data)} tracks...")

        # Build genre tree
        track_count = 0
        total_tracks = len(self.data)

        print_interval = max(1, total_tracks // 10)  # Print progress every 10%

        for i, (_, row) in enumerate(self.data.iterrows()):
            # Create a dictionary of track attributes
            track_data = {
                'mood_tags': row['mood_tags'] if isinstance(row['mood_tags'], list) else [],
                'duration': row['duration'] if 'duration' in row else 0
            }

            # Add track name and artist if available
            if 'track_name' in row:
                track_data['track_name'] = row['track_name']
            if 'artist_name' in row:
                track_data['artist_name'] = row['artist_name']

            # Add audio features
            for feature in self.audio_features:
                if feature in row and not pd.isna(row[feature]):
                    track_data[feature] = row[feature]

            # Get the genre hierarchy
            genre_path = row['genre_hierarchy'] if isinstance(row['genre_hierarchy'], list) else []

            # Add track to the tree
            self.genre_tree.add_track(row['track_id'], genre_path, track_data)

            # Add track to the similarity graph
            self.similarity_graph.add_node(row['track_id'], track_data)

            track_count += 1

            # Print progress
            if track_count % print_interval == 0 or track_count == total_tracks:
                print(f"  Progress: {track_count}/{total_tracks} "
                      f"tracks processed ({int(track_count/total_tracks*100)}%)")

        print("Building similarity graph...")
        # Calculate similarities between tracks
        self.similarity_graph.calculate_similarities(
            feature_keys=self.audio_features,
            mood_weight=0.6,
            feature_weight=0.4,
            similarity_threshold=0.3
        )

        print("✓ Data structures built successfully")

        # Print some summary statistics
        genre_count = len(self.get_available_genres())
        mood_count = len(self.get_available_moods())
        print(f"Summary: {track_count} tracks, {genre_count} genres, {mood_count} moods")

    def recommend_by_genre(self, genre: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recommend tracks by genre.

        Args:
            genre: The genre to recommend tracks from
            limit: Maximum number of tracks to recommend

        Returns:
            List of track dictionaries with track_id, genre_path, and other attributes
        """
        # Search for tracks in the genre
        track_nodes = self.genre_tree.search_by_genre(genre)

        # Convert to dictionaries with relevant information
        recommendations = []
        for node in track_nodes[:limit]:
            track_info = {
                'track_id': node.name,
                'genre_path': self.genre_tree.get_genre_path(node),
                'mood_tags': node.data.get('mood_tags', [])
            }

            # Add track name and artist if available
            if 'track_name' in node.data:
                track_info['track_name'] = node.data['track_name']
            if 'artist_name' in node.data:
                track_info['artist_name'] = node.data['artist_name']

            # Add audio features
            for feature in self.audio_features:
                if feature in node.data:
                    track_info[feature] = node.data[feature]

            recommendations.append(track_info)

        return recommendations

    def recommend_by_mood(self, mood: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recommend tracks by mood.

        Args:
            mood: The mood to recommend tracks for
            limit: Maximum number of tracks to recommend

        Returns:
            List of track dictionaries with track_id, genre_path, and other attributes
        """
        # Search for tracks with the mood
        track_nodes = self.genre_tree.search_by_mood(mood)

        # Convert to dictionaries with relevant information
        recommendations = []
        for node in track_nodes[:limit]:
            track_info = {
                'track_id': node.name,
                'genre_path': self.genre_tree.get_genre_path(node),
                'mood_tags': node.data.get('mood_tags', [])
            }

            # Add track name and artist if available
            if 'track_name' in node.data:
                track_info['track_name'] = node.data['track_name']
            if 'artist_name' in node.data:
                track_info['artist_name'] = node.data['artist_name']

            # Add audio features
            for feature in self.audio_features:
                if feature in node.data:
                    track_info[feature] = node.data[feature]

            recommendations.append(track_info)

        return recommendations

    def recommend_by_genre_and_mood(self, genre: str, mood: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recommend tracks by both genre and mood.

        Args:
            genre: The genre to recommend tracks from
            mood: The mood to recommend tracks for
            limit: Maximum number of tracks to recommend

        Returns:
            List of track dictionaries with track_id, genre_path, and other attributes
        """
        # Search for tracks with both genre and mood
        track_nodes = self.genre_tree.search_by_genre_and_mood(genre, mood)

        # Convert to dictionaries with relevant information
        recommendations = []
        for node in track_nodes[:limit]:
            track_info = {
                'track_id': node.name,
                'genre_path': self.genre_tree.get_genre_path(node),
                'mood_tags': node.data.get('mood_tags', [])
            }

            # Add track name and artist if available
            if 'track_name' in node.data:
                track_info['track_name'] = node.data['track_name']
            if 'artist_name' in node.data:
                track_info['artist_name'] = node.data['artist_name']

            # Add audio features
            for feature in self.audio_features:
                if feature in node.data:
                    track_info[feature] = node.data[feature]

            recommendations.append(track_info)

        return recommendations

    def recommend_similar_to_track(self, track_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recommend tracks similar to a given track.

        Args:
            track_id: The track ID to find similar tracks for
            limit: Maximum number of tracks to recommend

        Returns:
            List of track dictionaries with track_id, similarity, and other attributes
        """
        # Get similar tracks from the similarity graph
        similar_tracks = self.similarity_graph.recommend_similar_tracks(track_id, limit)

        # Convert to dictionaries with relevant information
        recommendations = []
        for similar_id, similarity in similar_tracks:
            node = self.genre_tree.get_track_node(similar_id)
            if node:
                track_info = {
                    'track_id': node.name,
                    'similarity': similarity,
                    'genre_path': self.genre_tree.get_genre_path(node),
                    'mood_tags': node.data.get('mood_tags', [])
                }

                # Add track name and artist if available
                if 'track_name' in node.data:
                    track_info['track_name'] = node.data['track_name']
                if 'artist_name' in node.data:
                    track_info['artist_name'] = node.data['artist_name']

                # Add audio features
                for feature in self.audio_features:
                    if feature in node.data:
                        track_info[feature] = node.data[feature]

                recommendations.append(track_info)

        return recommendations

    def bfs_recommend(self, genre: str, mood: Optional[str] = None,
                      max_depth: int = 2, limit: int = 10) -> List[Dict[str, Any]]:
        """Recommend tracks using breadth-first search from a genre node.

        Args:
            genre: The genre to start the search from
            mood: Optional mood to filter by
            max_depth: Maximum depth to search
            limit: Maximum number of tracks to recommend

        Returns:
            List of track dictionaries with track_id, genre_path, and other attributes
        """
        # Perform BFS search
        track_nodes = self.genre_tree.bfs_search(genre, mood, max_depth)

        # Convert to dictionaries with relevant information
        recommendations = []
        seen_tracks: Set[str] = set()  # To avoid duplicates

        for node in track_nodes:
            # Skip if we've already included this track
            if node.name in seen_tracks:
                continue

            seen_tracks.add(node.name)

            track_info = {
                'track_id': node.name,
                'genre_path': self.genre_tree.get_genre_path(node),
                'mood_tags': node.data.get('mood_tags', [])
            }

            # Add track name and artist if available
            if 'track_name' in node.data:
                track_info['track_name'] = node.data['track_name']
            if 'artist_name' in node.data:
                track_info['artist_name'] = node.data['artist_name']

            # Add audio features
            for feature in self.audio_features:
                if feature in node.data:
                    track_info[feature] = node.data[feature]

            recommendations.append(track_info)

            # Stop once we have enough recommendations
            if len(recommendations) >= limit:
                break

        return recommendations

    def dfs_recommend(self, genre: str, mood: Optional[str] = None,
                      max_breadth: int = 5, limit: int = 10) -> List[Dict[str, Any]]:
        """Recommend tracks using depth-first search from a genre node.

        Args:
            genre: The genre to start the search from
            mood: Optional mood to filter by
            max_breadth: Maximum number of siblings to explore at each level
            limit: Maximum number of tracks to recommend

        Returns:
            List of track dictionaries with track_id, genre_path, and other attributes
        """
        # Perform DFS search
        track_nodes = self.genre_tree.dfs_search(genre, mood, max_breadth)

        # Convert to dictionaries with relevant information
        recommendations = []
        seen_tracks: Set[str] = set()  # To avoid duplicates

        for node in track_nodes:
            # Skip if we've already included this track
            if node.name in seen_tracks:
                continue

            seen_tracks.add(node.name)

            track_info = {
                'track_id': node.name,
                'genre_path': self.genre_tree.get_genre_path(node),
                'mood_tags': node.data.get('mood_tags', [])
            }

            # Add track name and artist if available
            if 'track_name' in node.data:
                track_info['track_name'] = node.data['track_name']
            if 'artist_name' in node.data:
                track_info['artist_name'] = node.data['artist_name']

            # Add audio features
            for feature in self.audio_features:
                if feature in node.data:
                    track_info[feature] = node.data[feature]

            recommendations.append(track_info)

            # Stop once we have enough recommendations
            if len(recommendations) >= limit:
                break

        return recommendations

    def get_available_genres(self) -> List[str]:
        """Get a list of all available genres in the dataset.

        Returns:
            List of unique genre names
        """
        genres = set()

        def collect_genres(node: MusicNode) -> None:
            """Recursively collect genre names from the tree."""
            if node.node_type == 'genre' and node.name != 'music':
                genres.add(node.name)

            for child in node.children:
                collect_genres(child)

        # Start collection from the root
        collect_genres(self.genre_tree.root)

        return sorted(list(genres))

    def get_available_moods(self) -> List[str]:
        """Get a list of all available moods in the dataset.

        Returns:
            List of unique mood tags
        """
        moods = set()

        # Collect mood tags from all tracks
        for track_id, node in self.genre_tree.tracks.items():
            if 'mood_tags' in node.data:
                moods.update(node.data['mood_tags'])

        return sorted(list(moods))

    def get_track_info(self, track_id_to_find: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific track.

        Args:
            track_id_to_find: The track ID to get information for

        Returns:
            Dictionary with track information or None if not found
        """
        node = self.genre_tree.get_track_node(track_id_to_find)
        if not node:
            return None

        track_info = {
            'track_id': node.name,
            'genre_path': self.genre_tree.get_genre_path(node),
            'mood_tags': node.data.get('mood_tags', [])
        }

        # Add track name and artist if available
        if 'track_name' in node.data:
            track_info['track_name'] = node.data['track_name']
        if 'artist_name' in node.data:
            track_info['artist_name'] = node.data['artist_name']

        # Add audio features
        for feature in self.audio_features:
            if feature in node.data:
                track_info[feature] = node.data[feature]

        # Add duration if available
        if 'duration' in node.data:
            track_info['duration'] = node.data['duration']

        return track_info

    def search_tracks_by_name(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for tracks by name or artist.

        Args:
            search_term: The term to search for
            limit: Maximum number of tracks to return

        Returns:
            List of track dictionaries
        """
        results = []

        for track_id, node in self.genre_tree.tracks.items():
            track_name = node.data.get('track_name', '')
            artist_name = node.data.get('artist_name', '')

            # Skip if track or artist name is missing
            if not track_name and not artist_name:
                continue

            # Check if search term is in track name or artist name
            if (search_term.lower() in track_name.lower() or
                    search_term.lower() in artist_name.lower()):

                # Create track info dictionary
                track_info = {
                    'track_id': track_id,
                    'track_name': track_name,
                    'artist_name': artist_name,
                    'genre_path': self.genre_tree.get_genre_path(node),
                    'mood_tags': node.data.get('mood_tags', [])
                }

                # Add audio features
                for feature in self.audio_features:
                    if feature in node.data:
                        track_info[feature] = node.data[feature]

                results.append(track_info)

                # Stop once we have enough results
                if len(results) >= limit:
                    break

        return results


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    if python_ta:
        python_ta.check_all(config={
            'extra-imports': ['pandas', 'typing', 'music_structures'],
            'allowed-io': [],
            'max-line-length': 100,
            'disable': ['E1136']
        })
