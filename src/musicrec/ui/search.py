"""CSC111 Winter 2025: A Mood-Driven Music Recommender with Genre Hierarchies

Search functionality module for real-time track/artist search with debounced input
and accessible dropdown interface.

Copyright and Usage Information
===============================
This file is Copyright (c) 2025 Qian (Angela) Su.
"""

import difflib
from functools import lru_cache
from typing import Any, Dict, List, Set, Tuple

# Performance optimization constants
FUZZY_PREFILTER_TOP_N = 30
FUZZY_CACHE_SIZE = 4096


class SearchEngine:
    """Handles real-time search functionality for tracks and artists.

    This class provides debounced search capabilities with configurable
    parameters and supports filtering tracks by name, artist, and genre.

    Instance Attributes:
        - recommender: The music recommender engine
        - min_query_length: Minimum characters required for search (default: 3)
        - max_results: Maximum number of results to return (default: 20)
    """

    def __init__(
        self,
        recommender,
        min_query_length: int = 3,
        max_results: int = 20,
        enable_fuzzy: bool = False,
        fuzzy_threshold: float = 0.6,
        prefilter_top_n: int = FUZZY_PREFILTER_TOP_N,
        cache_size: int = FUZZY_CACHE_SIZE,
    ):
        """Initialize the search engine.

        Args:
            recommender: The music recommender engine
            min_query_length: Minimum characters required for search
            max_results: Maximum number of results to return
            enable_fuzzy: Whether to enable fuzzy matching for typos
            fuzzy_threshold: Minimum similarity ratio for fuzzy matches (0.0-1.0)
            prefilter_top_n: Number of top candidates to consider after trigram prefiltering
            cache_size: Size of the LRU cache for similarity computations
        """
        self.recommender = recommender
        self.min_query_length = min_query_length
        self.max_results = max_results
        self.enable_fuzzy = enable_fuzzy
        self.fuzzy_threshold = fuzzy_threshold
        self.prefilter_top_n = prefilter_top_n
        self.cache_size = cache_size

        # Build trigram index for fuzzy matching optimization
        self._trigram_index = self._build_trigram_index()

        # Initialize cached similarity function
        self._cached_similarity = lru_cache(maxsize=cache_size)(
            self._compute_similarity
        )

    def search_tracks(self, query: str) -> List[Dict[str, Any]]:
        """Search for tracks by name, artist, or combined query.

        Args:
            query: Search string (track name, artist name, or combination)

        Returns:
            List of matching track dictionaries with display information
        """
        if not query or len(query.strip()) < self.min_query_length:
            return []

        query = query.strip().lower()
        matches = []

        # Use trigram prefiltering for fuzzy search if enabled
        candidate_tracks = None
        if self.enable_fuzzy and len(query) >= 3:
            candidate_tracks = self._prefilter_candidates(query)
            candidate_ids = {track_id for track_id, _ in candidate_tracks}

        # Search through tracks (all tracks or prefiltered candidates)
        tracks_to_search = (
            self.recommender.genre_tree.tracks.items()
            if not candidate_tracks
            else [
                (tid, self.recommender.genre_tree.tracks[tid])
                for tid, _ in candidate_tracks
            ]
        )

        for track_id, node in tracks_to_search:
            track_data = node.data
            track_name = track_data.get("track_name", "").lower()
            artist_name = track_data.get("artist_name", "").lower()

            # Check if query matches track name, artist name, or both
            exact_match = query in track_name or query in artist_name
            fuzzy_match = False

            if not exact_match:
                # Always check word-based fuzzy matching (backward compatibility)
                word_match = self._fuzzy_match(query, f"{track_name} {artist_name}")

                # Check similarity-based fuzzy matching if enabled
                similarity_match = False
                if self.enable_fuzzy:
                    # If we used prefiltering, we already know this candidate has potential
                    if candidate_tracks and track_id in candidate_ids:
                        similarity_match = (
                            self._fuzzy_similarity(query, track_name)
                            >= self.fuzzy_threshold
                            or self._fuzzy_similarity(query, artist_name)
                            >= self.fuzzy_threshold
                        )
                    elif not candidate_tracks:
                        # Fallback to full similarity check if no prefiltering
                        similarity_match = (
                            self._fuzzy_similarity(query, track_name)
                            >= self.fuzzy_threshold
                            or self._fuzzy_similarity(query, artist_name)
                            >= self.fuzzy_threshold
                        )

                fuzzy_match = word_match or similarity_match

            if exact_match or fuzzy_match:

                # Create search result with proper display names
                result = {
                    "track_id": track_id,
                    "track_name": track_data.get("track_name", track_id),
                    "artist_name": track_data.get("artist_name", "Unknown"),
                    "display_name": (
                        f"{track_data.get('track_name', track_id)} - "
                        f"{track_data.get('artist_name', 'Unknown')}"
                    ),
                    "genre_path": self._get_genre_path(track_id),
                    "mood_tags": self._get_mood_tags(track_id),
                    "match_score": self._calculate_match_score(
                        query,
                        track_name,
                        artist_name,
                        exact_match,
                        fuzzy_match and not exact_match,
                    ),
                }

                matches.append(result)

                # Stop if we have enough matches for performance
                if len(matches) >= self.max_results * 2:  # Get extra for sorting
                    break

        # Sort by match score (descending) and limit results
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[: self.max_results]

    def is_fuzzy_enabled(self) -> bool:
        """Check if fuzzy search is enabled.

        Returns:
            True if fuzzy search is enabled, False otherwise
        """
        return self.enable_fuzzy

    def _build_trigram_index(self) -> Dict[str, Set[str]]:
        """Build trigram index for all tracks for fast prefiltering.

        Returns:
            Dictionary mapping track_id to set of trigrams from track_name and artist_name
        """
        index = {}
        for track_id, node in self.recommender.genre_tree.tracks.items():
            track_data = node.data
            track_name = track_data.get("track_name", "").lower()
            artist_name = track_data.get("artist_name", "").lower()

            # Combine track and artist for trigram generation
            combined_text = f"{track_name} {artist_name}".strip()
            trigrams = self._generate_trigrams(combined_text)
            index[track_id] = trigrams

        return index

    def _generate_trigrams(self, text: str) -> Set[str]:
        """Generate trigrams from text.

        Args:
            text: Input text

        Returns:
            Set of trigrams (3-character substrings)
        """
        if len(text) < 3:
            return {text}

        trigrams = set()
        # Add padding for start and end of text
        padded_text = f"  {text}  "

        for i in range(len(padded_text) - 2):
            trigram = padded_text[i : i + 3]
            trigrams.add(trigram)

        return trigrams

    def _prefilter_candidates(self, query: str) -> List[Tuple[str, float]]:
        """Use trigram overlap to prefilter candidates before expensive similarity computation.

        Args:
            query: Search query

        Returns:
            List of (track_id, trigram_score) tuples, sorted by trigram score descending
        """
        query_trigrams = self._generate_trigrams(query.lower())
        candidates = []

        for track_id, track_trigrams in self._trigram_index.items():
            # Calculate Jaccard similarity between trigram sets
            intersection = len(query_trigrams & track_trigrams)
            union = len(query_trigrams | track_trigrams)

            if union > 0:
                jaccard_score = intersection / union
                if jaccard_score > 0:  # Only consider candidates with some overlap
                    candidates.append((track_id, jaccard_score))

        # Sort by trigram score and take top N
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[: self.prefilter_top_n]

    def _compute_similarity(self, query: str, text: str) -> float:
        """Compute similarity score (for caching).

        Args:
            query: Search query
            text: Text to compare against

        Returns:
            Similarity ratio between 0.0 and 1.0
        """
        if not query or not text:
            return 0.0
        return difflib.SequenceMatcher(None, query.lower(), text.lower()).ratio()

    def clear_cache(self) -> None:
        """Clear the similarity computation cache."""
        self._cached_similarity.cache_clear()

    def _fuzzy_similarity(self, query: str, text: str) -> float:
        """Calculate fuzzy similarity between query and text using cached computation.

        Args:
            query: Search query
            text: Text to compare against

        Returns:
            Similarity ratio between 0.0 and 1.0
        """
        return self._cached_similarity(query, text)

    def _fuzzy_match(self, query: str, text: str) -> bool:
        """Perform fuzzy matching for better search results.

        Args:
            query: Search query
            text: Text to search in

        Returns:
            True if fuzzy match found, False otherwise
        """
        # Simple fuzzy matching: check if all query words are present
        query_words = query.split()
        return all(word in text for word in query_words if len(word) > 2)

    def _calculate_match_score(
        self,
        query: str,
        track_name: str,
        artist_name: str,
        exact_match: bool = True,
        fuzzy_match: bool = False,
    ) -> float:
        """Calculate relevance score for search result.

        Args:
            query: Original search query
            track_name: Track name to score
            artist_name: Artist name to score
            exact_match: Whether this was an exact substring match
            fuzzy_match: Whether this was a fuzzy match

        Returns:
            Match score (higher is better)
        """
        score = 0.0

        if exact_match:
            # Exact match bonuses (highest priority)
            if query == track_name:
                score += 10.0
            elif query == artist_name:
                score += 8.0
            elif track_name.startswith(query):
                score += 5.0
            elif artist_name.startswith(query):
                score += 4.0

            # Partial match bonuses
            if query in track_name:
                score += 3.0
            if query in artist_name:
                score += 2.0

            # Word match bonuses
            query_words = query.split()
            for word in query_words:
                if word in track_name:
                    score += 1.0
                if word in artist_name:
                    score += 0.8

        elif fuzzy_match:
            # Fuzzy match bonuses (lower than exact but still relevant)
            track_similarity = self._fuzzy_similarity(query, track_name)
            artist_similarity = self._fuzzy_similarity(query, artist_name)

            # Scale fuzzy scores to be lower than exact matches
            score += track_similarity * 2.0  # Max 2.0 for perfect fuzzy track match
            score += artist_similarity * 1.5  # Max 1.5 for perfect fuzzy artist match

            # Bonus for high similarity
            max_similarity = max(track_similarity, artist_similarity)
            if max_similarity >= 0.8:
                score += 0.5

        return score

    def _get_genre_path(self, track_id: str) -> List[str]:
        """Get genre path for a track.

        Args:
            track_id: Track identifier

        Returns:
            List of genres in hierarchical order
        """
        try:
            track_info = self.recommender.get_track_info(track_id)
            return track_info.get("genre_path", []) if track_info else []
        except Exception:
            return []

    def _get_mood_tags(self, track_id: str) -> List[str]:
        """Get mood tags for a track.

        Args:
            track_id: Track identifier

        Returns:
            List of mood tags
        """
        try:
            track_info = self.recommender.get_track_info(track_id)
            return track_info.get("mood_tags", []) if track_info else []
        except Exception:
            return []


def create_search_suggestions_html(
    suggestions: List[Dict[str, Any]], search_id: str = "track-search"
) -> str:
    """Create HTML for search suggestions dropdown.

    Args:
        suggestions: List of search result dictionaries
        search_id: ID of the search input element

    Returns:
        HTML string for suggestions dropdown
    """
    if not suggestions:
        return f"""
        <div class="search-suggestions empty" 
             id="{search_id}-suggestions"
             role="listbox" 
             aria-label="No search results">
            <div class="suggestion-item empty" role="option">
                No tracks found
            </div>
        </div>
        """

    suggestions_html = f"""
    <div class="search-suggestions" 
         id="{search_id}-suggestions"
         role="listbox" 
         aria-label="{len(suggestions)} search results">
    """

    for i, suggestion in enumerate(suggestions):
        suggestions_html += f"""
        <div class="suggestion-item" 
             role="option" 
             tabindex="-1"
             data-track-id="{suggestion['track_id']}"
             data-index="{i}"
             aria-selected="false">
            <div class="suggestion-main">
                <span class="track-name">{suggestion['track_name']}</span>
                <span class="artist-name">by {suggestion['artist_name']}</span>
            </div>
            <div class="suggestion-details">
                <span class="genre">{"› ".join(suggestion['genre_path'][:2])}</span>
                {f"<span class='moods'>{', '.join(suggestion['mood_tags'][:3])}</span>" if suggestion['mood_tags'] else ""}
            </div>
        </div>
        """

    suggestions_html += "</div>"
    return suggestions_html


def generate_search_styles() -> str:
    """Generate CSS styles for search components.

    Returns:
        CSS string for search styling
    """
    return """
    .search-container {
        position: relative;
        width: 100%;
    }
    
    .search-input {
        width: 100%;
        padding: 12px 16px;
        border: 2px solid #ddd;
        border-radius: 8px;
        font-size: 16px;
        transition: border-color 0.2s ease;
    }
    
    .search-input:focus {
        outline: none;
        border-color: #4CAF50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
    }
    
    .search-loading {
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-left: 8px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #4CAF50;
        border-radius: 50%;
        animation: search-spin 1s linear infinite;
    }
    
    @keyframes search-spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .search-suggestions {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        max-height: 300px;
        overflow-y: auto;
        z-index: 1000;
        margin-top: 4px;
    }
    
    .search-suggestions.empty .suggestion-item {
        color: #999;
        font-style: italic;
        text-align: center;
        padding: 16px;
    }
    
    .suggestion-item {
        padding: 12px 16px;
        cursor: pointer;
        border-bottom: 1px solid #f5f5f5;
        transition: background-color 0.2s ease;
    }
    
    .suggestion-item:last-child {
        border-bottom: none;
    }
    
    .suggestion-item:hover,
    .suggestion-item[aria-selected="true"] {
        background-color: #f8f9fa;
    }
    
    .suggestion-item:focus {
        background-color: #e3f2fd;
        outline: 2px solid #2196F3;
        outline-offset: -2px;
    }
    
    .suggestion-main {
        margin-bottom: 4px;
    }
    
    .track-name {
        font-weight: 600;
        color: #333;
        margin-right: 8px;
    }
    
    .artist-name {
        color: #666;
        font-size: 0.9em;
    }
    
    .suggestion-details {
        font-size: 0.8em;
        color: #999;
    }
    
    .genre {
        margin-right: 12px;
    }
    
    .moods {
        color: #2196F3;
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .search-input {
            border-color: #000;
        }
        
        .search-input:focus {
            border-color: #000;
            box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.3);
        }
        
        .suggestion-item:hover,
        .suggestion-item[aria-selected="true"] {
            background-color: #000;
            color: #fff;
        }
    }
    
    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        .search-input,
        .suggestion-item {
            transition: none;
        }
        
        .search-loading {
            animation: none;
        }
    }
    """
