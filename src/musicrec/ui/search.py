"""Enhanced search functionality with fuzzy matching capabilities.

This module provides advanced search features for the music recommender system,
including fuzzy string matching, trigram indexing, and performance optimizations.
"""

import re
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional, Any
import time


class SearchEngine:
    """Advanced search engine with fuzzy matching capabilities.

    Provides fast and flexible search across music tracks with support for:
    - Exact string matching
    - Fuzzy string matching with configurable thresholds
    - Trigram-based indexing for performance
    - Configurable result limits and query length requirements
    """

    def __init__(
        self,
        recommender,
        min_query_length: int = 3,
        max_results: int = 20,
        enable_fuzzy: bool = False,
        fuzzy_threshold: float = 0.6
    ):
        """Initialize the search engine.

        Args:
            recommender: The music recommender engine containing track data
            min_query_length: Minimum characters required for search queries
            max_results: Maximum number of results to return
            enable_fuzzy: Whether to enable fuzzy string matching
            fuzzy_threshold: Minimum similarity score for fuzzy matches (0.0-1.0)
        """
        self.recommender = recommender
        self.min_query_length = min_query_length
        self.max_results = max_results
        self.enable_fuzzy = enable_fuzzy
        self.fuzzy_threshold = fuzzy_threshold

        # Build search indexes for performance
        self._exact_index = self._build_exact_index()
        self._trigram_index = self._build_trigram_index() if enable_fuzzy else {}

    def _build_exact_index(self) -> Dict[str, List[str]]:
        """Build an exact string matching index for fast lookups.

        Returns:
            Dictionary mapping normalized strings to track IDs
        """
        index = defaultdict(list)

        for track_id, node in self.recommender.genre_tree.tracks.items():
            track_name = node.data.get("track_name", "")
            artist_name = node.data.get("artist_name", "")

            # Index normalized versions for case-insensitive search
            track_normalized = track_name.lower().strip()
            artist_normalized = artist_name.lower().strip()
            combined_normalized = f"{track_normalized} {artist_normalized}".strip()

            if track_normalized:
                index[track_normalized].append(track_id)
            if artist_normalized:
                index[artist_normalized].append(track_id)
            if combined_normalized:
                index[combined_normalized].append(track_id)

        return dict(index)

    def _build_trigram_index(self) -> Dict[str, Set[str]]:
        """Build trigram index for fuzzy matching.

        Returns:
            Dictionary mapping trigrams to sets of track IDs
        """
        index = defaultdict(set)

        for track_id, node in self.recommender.genre_tree.tracks.items():
            track_name = node.data.get("track_name", "")
            artist_name = node.data.get("artist_name", "")

            # Generate trigrams for track and artist names
            for text in [track_name, artist_name]:
                if text:
                    normalized = text.lower().strip()
                    trigrams = self._generate_trigrams(normalized)
                    for trigram in trigrams:
                        index[trigram].add(track_id)

        return dict(index)

    def _generate_trigrams(self, text: str) -> Set[str]:
        """Generate trigrams from a text string.

        Args:
            text: Input text string

        Returns:
            Set of trigram strings
        """
        if len(text) < 3:
            return {text}

        # Add padding for edge trigrams
        padded = f"  {text}  "
        trigrams = set()

        for i in range(len(padded) - 2):
            trigrams.add(padded[i:i+3])

        return trigrams

    def _calculate_similarity(self, query: str, target: str) -> float:
        """Calculate similarity between query and target strings.

        Uses Jaccard similarity based on trigrams.

        Args:
            query: Search query string
            target: Target string to compare against

        Returns:
            Similarity score between 0.0 and 1.0
        """
        query_trigrams = self._generate_trigrams(query.lower())
        target_trigrams = self._generate_trigrams(target.lower())

        if not query_trigrams or not target_trigrams:
            return 0.0

        intersection = len(query_trigrams & target_trigrams)
        union = len(query_trigrams | target_trigrams)

        return intersection / union if union > 0 else 0.0

    def search_tracks(self, query: str) -> List[Dict[str, Any]]:
        """Search for tracks matching the given query.

        Args:
            query: Search query string

        Returns:
            List of search results with track information
        """
        if len(query) < self.min_query_length:
            return []

        # Normalize query
        query_normalized = query.lower().strip()
        results = []
        seen_tracks = set()

        # Phase 1: Exact matches (highest priority)
        exact_matches = self._find_exact_matches(query_normalized)
        for track_id, score in exact_matches:
            if track_id not in seen_tracks:
                result = self._create_result(track_id, score, "exact")
                if result:
                    results.append(result)
                    seen_tracks.add(track_id)

        # Phase 2: Fuzzy matches (if enabled and we need more results)
        if self.enable_fuzzy and len(results) < self.max_results:
            fuzzy_matches = self._find_fuzzy_matches(query_normalized, seen_tracks)
            for track_id, score in fuzzy_matches:
                if len(results) >= self.max_results:
                    break
                result = self._create_result(track_id, score, "fuzzy")
                if result:
                    results.append(result)

        return results[:self.max_results]

    def _find_exact_matches(self, query: str) -> List[Tuple[str, float]]:
        """Find exact string matches.

        Args:
            query: Normalized search query

        Returns:
            List of (track_id, score) tuples
        """
        matches = []

        # Check for exact matches and substring matches
        for indexed_string, track_ids in self._exact_index.items():
            if query in indexed_string or indexed_string in query:
                # Score based on how close the match is
                if query == indexed_string:
                    score = 1.0  # Perfect match
                elif indexed_string.startswith(query):
                    score = 0.95  # Prefix match
                elif indexed_string.endswith(query):
                    score = 0.9   # Suffix match
                else:
                    score = 0.8   # Substring match

                for track_id in track_ids:
                    matches.append((track_id, score))

        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def _find_fuzzy_matches(self, query: str, exclude_tracks: Set[str]) -> List[Tuple[str, float]]:
        """Find fuzzy string matches using trigram similarity.

        Args:
            query: Normalized search query
            exclude_tracks: Track IDs to exclude from results

        Returns:
            List of (track_id, score) tuples
        """
        matches = []
        query_trigrams = self._generate_trigrams(query)

        # Find candidate tracks using trigram intersection
        candidates = set()
        for trigram in query_trigrams:
            if trigram in self._trigram_index:
                candidates.update(self._trigram_index[trigram])

        # Calculate similarity scores for candidates
        for track_id in candidates:
            if track_id in exclude_tracks:
                continue

            node = self.recommender.genre_tree.tracks.get(track_id)
            if not node:
                continue

            track_name = node.data.get("track_name", "")
            artist_name = node.data.get("artist_name", "")

            # Calculate max similarity against track name and artist
            max_score = 0.0
            for target in [track_name.lower(), artist_name.lower()]:
                if target:
                    score = self._calculate_similarity(query, target)
                    max_score = max(max_score, score)

            if max_score >= self.fuzzy_threshold:
                matches.append((track_id, max_score))

        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def _create_result(self, track_id: str, score: float, match_type: str) -> Optional[Dict[str, Any]]:
        """Create a search result dictionary for a track.

        Args:
            track_id: Track identifier
            score: Match score (0.0-1.0)
            match_type: Type of match ("exact" or "fuzzy")

        Returns:
            Search result dictionary or None if track not found
        """
        node = self.recommender.genre_tree.tracks.get(track_id)
        if not node:
            return None

        track_name = node.data.get("track_name", track_id)
        artist_name = node.data.get("artist_name", "Unknown")

        return {
            "track_id": track_id,
            "track_name": track_name,
            "artist_name": artist_name,
            "display_name": f"{track_name} - {artist_name}",
            "score": score,
            "match_type": match_type
        }


def generate_search_styles() -> str:
    """Generate CSS styles for the search interface.

    Returns:
        CSS style string
    """
    return """
    .search-container {
        position: relative;
        width: 100%;
    }

    .search-input {
        width: 100%;
        padding: 8px 12px;
        font-size: 14px;
        border: 2px solid #ddd;
        border-radius: 6px;
        transition: border-color 0.2s ease;
    }

    .search-input:focus {
        outline: none;
        border-color: #0066cc;
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
    }

    .search-suggestions {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-top: none;
        border-radius: 0 0 6px 6px;
        max-height: 300px;
        overflow-y: auto;
        z-index: 1000;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .search-suggestion {
        padding: 12px 16px;
        cursor: pointer;
        border-bottom: 1px solid #f0f0f0;
        transition: background-color 0.15s ease;
    }

    .search-suggestion:hover,
    .search-suggestion:focus {
        background-color: #f8f9fa;
    }

    .search-suggestion:last-child {
        border-bottom: none;
    }

    .search-loading {
        padding: 12px 16px;
        text-align: center;
        color: #666;
        font-style: italic;
    }

    .search-no-results {
        padding: 12px 16px;
        text-align: center;
        color: #999;
        font-style: italic;
    }

    /* Accessibility improvements */
    @media (prefers-reduced-motion: reduce) {
        .search-input,
        .search-suggestion {
            transition: none;
        }
    }

    @media (prefers-contrast: high) {
        .search-input {
            border-color: #000;
        }

        .search-input:focus {
            border-color: #0066cc;
            box-shadow: 0 0 0 3px #0066cc;
        }
    }
    """