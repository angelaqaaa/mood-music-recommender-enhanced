"""Utility functions for generating recommendation explanations.

This module provides functions to generate user-friendly explanations for
why specific tracks were recommended.
"""

from typing import Any, Dict, List, Optional


def generate_explanation(
    track_info: Dict[str, Any],
    recommendation_type: str,
    similarity_score: Optional[float] = None,
    source_track: Optional[str] = None,
) -> str:
    """Generate a user-friendly explanation for a recommendation.

    Args:
        track_info: Track information dictionary
        recommendation_type: Type of recommendation (genre, mood, similarity, etc.)
        similarity_score: Similarity score if applicable
        source_track: Source track name for similarity recommendations

    Returns:
        Human-readable explanation string
    """
    track_name = track_info.get("track_name") or "Unknown Track"
    artist_name = track_info.get("artist_name") or "Unknown Artist"
    genre_path = track_info.get("genre_path") or []
    mood_tags = track_info.get("mood_tags") or []

    # Base track identifier
    base_text = f'"{track_name}" by {artist_name}'

    # Build explanation based on type
    if recommendation_type == "similarity" and similarity_score is not None:
        similarity_percent = int(similarity_score * 100)
        explanation = f"{base_text} ({similarity_percent}% similar"
        if source_track:
            explanation += f" to {source_track}"
        explanation += ")"

    elif recommendation_type in ["genre", "bfs", "dfs"]:
        if genre_path:
            genre_str = " → ".join(genre_path)
            explanation = f"{base_text} (Genre: {genre_str})"
        else:
            explanation = f"{base_text} (Genre-based)"

    elif recommendation_type == "mood":
        if mood_tags:
            mood_str = ", ".join(mood_tags[:2])  # Show up to 2 moods
            explanation = f"{base_text} (Mood: {mood_str})"
        else:
            explanation = f"{base_text} (Mood-based)"

    elif recommendation_type == "genre_mood":
        parts = []
        if genre_path:
            parts.append(f"Genre: {' → '.join(genre_path)}")
        if mood_tags:
            parts.append(f"Mood: {', '.join(mood_tags[:2])}")

        if parts:
            explanation = f"{base_text} ({'; '.join(parts)})"
        else:
            explanation = f"{base_text} (Genre & mood match)"

    else:
        explanation = f"{base_text} (Recommended)"

    # Add audio features if available
    features = []
    if "energy" in track_info and track_info["energy"] is not None:
        energy = track_info["energy"]
        if energy > 0.7:
            features.append("high energy")
        elif energy < 0.3:
            features.append("low energy")

    if "valence" in track_info and track_info["valence"] is not None:
        valence = track_info["valence"]
        if valence > 0.7:
            features.append("positive mood")
        elif valence < 0.3:
            features.append("melancholic")

    if features:
        explanation += f" • {', '.join(features)}"

    return explanation


def get_top_features(track_info: Dict[str, Any], limit: int = 3) -> List[str]:
    """Get top contributing features for a track.

    Args:
        track_info: Track information dictionary
        limit: Maximum number of features to return

    Returns:
        List of feature descriptions
    """
    features = []

    # Check audio features
    if "energy" in track_info and track_info["energy"] is not None:
        energy = track_info["energy"]
        if energy > 0.8:
            features.append(f"Very energetic ({energy:.2f})")
        elif energy > 0.6:
            features.append(f"Energetic ({energy:.2f})")
        elif energy < 0.3:
            features.append(f"Calm ({energy:.2f})")

    if "valence" in track_info and track_info["valence"] is not None:
        valence = track_info["valence"]
        if valence > 0.7:
            features.append(f"Upbeat mood ({valence:.2f})")
        elif valence < 0.3:
            features.append(f"Melancholic ({valence:.2f})")

    if "tempo" in track_info and track_info["tempo"] is not None:
        tempo = track_info["tempo"]
        if tempo > 140:
            features.append(f"Fast tempo ({tempo:.0f} BPM)")
        elif tempo < 80:
            features.append(f"Slow tempo ({tempo:.0f} BPM)")

    return features[:limit]
