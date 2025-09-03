"""CSC111 Winter 2025: A Mood-Driven Music Recommender with Genre Hierarchies

Main module for running the music recommender system.
This module connects all components and runs the complete application.

Copyright and Usage Information
===============================
This file is Copyright (c) 2025 Qian (Angela) Su & Mengxuan (Connie) Guo.
"""

import os
import argparse
import pandas as pd
from typing import Optional
import html

from data_processor import build_dataset, save_processed_data, load_processed_data
from recommendation_engine import MusicRecommender
from visualization import MusicRecommenderDashApp
from logging import setup_logging


def create_sample_data() -> pd.DataFrame:
    """Create a sample dataset for testing when real data files are not available.

    Returns:
        Sample DataFrame for testing
    """
    # Create sample tracks
    sample_data = []

    # Rock genre tracks
    for i in range(1, 11):
        track_id = f"track_100{i}"
        track_name = f"Rock Song {i}"
        artist_name = f"Rock Artist {i//3 + 1}"
        genre = "rock"
        mood_tags = ["energetic"] if i % 2 == 0 else ["calm"]

        if i % 3 == 0:
            mood_tags.append("happy")

        energy = 0.7 + (i % 10) / 50
        valence = 0.6 + (i % 10) / 50
        tempo = 120 + i

        sample_data.append({
            "track_id": track_id,
            "track_name": track_name,
            "artist_name": artist_name,
            "genre_tags": [genre],
            "mood_tags": mood_tags,
            "duration": 180 + i * 10,
            "energy": energy,
            "valence": valence,
            "tempo": tempo,
            "genre_hierarchy": ["rock"]
        })

    # Metal genre tracks
    for i in range(1, 11):
        track_id = f"track_200{i}"
        track_name = f"Metal Song {i}"
        artist_name = f"Metal Artist {i//3 + 1}"
        genre = "metal"
        mood_tags = ["intense"] if i % 2 == 0 else ["melodic"]

        if i % 3 == 0:
            mood_tags.append("energetic")

        energy = 0.8 + (i % 10) / 50
        valence = 0.4 + (i % 10) / 50
        tempo = 140 + i

        sample_data.append({
            "track_id": track_id,
            "track_name": track_name,
            "artist_name": artist_name,
            "genre_tags": [genre],
            "mood_tags": mood_tags,
            "duration": 210 + i * 10,
            "energy": energy,
            "valence": valence,
            "tempo": tempo,
            "genre_hierarchy": ["metal"]
        })

    # Electronic genre tracks
    for i in range(1, 11):
        track_id = f"track_300{i}"
        track_name = f"Electronic Song {i}"
        artist_name = f"DJ Artist {i//3 + 1}"
        genre = "electronic"
        mood_tags = ["upbeat"] if i % 2 == 0 else ["chill"]

        if i % 3 == 0:
            mood_tags.append("energetic")

        energy = 0.6 + (i % 10) / 50
        valence = 0.7 + (i % 10) / 50
        tempo = 130 + i

        sample_data.append({
            "track_id": track_id,
            "track_name": track_name,
            "artist_name": artist_name,
            "genre_tags": [genre],
            "mood_tags": mood_tags,
            "duration": 200 + i * 10,
            "energy": energy,
            "valence": valence,
            "tempo": tempo,
            "genre_hierarchy": ["electronic"]
        })

    # Acoustic genre tracks
    for i in range(1, 11):
        track_id = f"track_400{i}"
        track_name = f"Acoustic Song {i}"
        artist_name = f"Folk Artist {i//3 + 1}"
        genre = "acoustic"
        mood_tags = ["calm"] if i % 2 == 0 else ["melancholic"]

        if i % 3 == 0:
            mood_tags.append("peaceful")

        energy = 0.3 + (i % 10) / 50
        valence = 0.5 + (i % 10) / 50
        tempo = 90 + i

        sample_data.append({
            "track_id": track_id,
            "track_name": track_name,
            "artist_name": artist_name,
            "genre_tags": [genre],
            "mood_tags": mood_tags,
            "duration": 190 + i * 10,
            "energy": energy,
            "valence": valence,
            "tempo": tempo,
            "genre_hierarchy": ["acoustic"]
        })

    # Add some subgenres
    # Punkrock (subgenre of rock)
    for i in range(1, 6):
        track_id = f"track_500{i}"
        track_name = f"Punk Song {i}"
        artist_name = f"Punk Artist {i//2 + 1}"
        genre = "punkrock"
        mood_tags = ["energetic", "intense"]

        energy = 0.8 + (i % 5) / 50
        valence = 0.5 + (i % 5) / 50
        tempo = 150 + i

        sample_data.append({
            "track_id": track_id,
            "track_name": track_name,
            "artist_name": artist_name,
            "genre_tags": [genre],
            "mood_tags": mood_tags,
            "duration": 150 + i * 10,
            "energy": energy,
            "valence": valence,
            "tempo": tempo,
            "genre_hierarchy": ["rock", "punkrock"]
        })

    # Death metal (subgenre of metal)
    for i in range(1, 6):
        track_id = f"track_600{i}"
        track_name = f"Death Metal Song {i}"
        artist_name = f"Death Metal Artist {i//2 + 1}"
        genre = "deathmetal"
        mood_tags = ["intense", "angry"]

        energy = 0.9 + (i % 5) / 100
        valence = 0.2 + (i % 5) / 50
        tempo = 160 + i

        sample_data.append({
            "track_id": track_id,
            "track_name": track_name,
            "artist_name": artist_name,
            "genre_tags": [genre],
            "mood_tags": mood_tags,
            "duration": 220 + i * 10,
            "energy": energy,
            "valence": valence,
            "tempo": tempo,
            "genre_hierarchy": ["metal", "deathmetal"]
        })

    # Create a DataFrame
    df = pd.DataFrame(sample_data)

    return df


def load_data(spotify_path: Optional[str] = None,
              genre_path: Optional[str] = None,
              mood_path: Optional[str] = None,
              metadata_path: Optional[str] = None,
              processed_path: Optional[str] = None,
              use_sample: bool = False) -> pd.DataFrame:
    """Load and process the music dataset.

    Args:
        spotify_path: Path to the Spotify features CSV
        genre_path: Path to the Jamendo genre TSV
        mood_path: Path to the Jamendo mood TSV
        metadata_path: Path to the metadata TSV with track names
        processed_path: Path to a previously processed dataset
        use_sample: Whether to use sample data for testing

    Returns:
        Processed DataFrame for the recommender system
    """
    # Check if we should use a previously processed dataset
    if processed_path and os.path.exists(processed_path):
        print(f"Loading processed dataset from {processed_path}")
        return load_processed_data(processed_path)

    # Check if we should use sample data
    if use_sample:
        print("Using sample dataset for testing")
        return create_sample_data()

    # Otherwise, build the dataset from source files
    files_exist = all(
        os.path.exists(path) for path in [spotify_path, genre_path, mood_path]
        if path is not None
    )

    if files_exist and spotify_path and genre_path and mood_path:
        print("Building dataset from source files")
        return build_dataset(spotify_path, genre_path, mood_path, metadata_path)
    else:
        missing = []
        if spotify_path and not os.path.exists(spotify_path):
            missing.append(spotify_path)
        if genre_path and not os.path.exists(genre_path):
            missing.append(genre_path)
        if mood_path and not os.path.exists(mood_path):
            missing.append(mood_path)
        if metadata_path and not os.path.exists(metadata_path):
            missing.append(metadata_path)

        if missing:
            print(f"Warning: The following files were not found: {', '.join(missing)}")

    # If no valid data sources, use sample data
    print("No valid data sources provided or files not found, using sample dataset")
    return create_sample_data()


def run_recommender_app(data: pd.DataFrame, debug: bool = False, port: int = 8040) -> None:
    """Run the music recommender Dash application.

    Args:
        data: The processed DataFrame
        debug: Whether to run in debug mode
        port: The port to run the server on
    """
    import time
    start_time = time.time()

    # Clean HTML entities in text fields for better display
    text_columns = ['track_name', 'artist_name', 'album_name']
    for col in text_columns:
        if col in data.columns:
            data[col] = data[col].apply(
                lambda x: html.unescape(str(x)) if pd.notna(x) else x
            )

    # Create the recommender engine
    print("\nInitializing recommender engine...")
    recommender = MusicRecommender(data)

    engine_time = time.time()
    print(f"✓ Recommender engine initialized in {engine_time - start_time:.2f} seconds")

    # Create and run the Dash app
    print("\nInitializing Dash application...")
    app = MusicRecommenderDashApp(recommender)
    print(f"✓ Application initialized in {time.time() - engine_time:.2f} seconds")

    print(f"\nStarting the Dash server on port {port}")
    print(f"You can access the application at http://127.0.0.1:{port}/")
    print("\nImportant features:")
    print("1. Track names are now clickable links that open in YouTube Music")
    print("2. Results are now set to 50 by default and can be scrolled")
    print("3. All songs in the dataset are available for search")
    print("4. HTML entities in track/artist names are properly displayed")
    print("\nPress Ctrl+C to stop the server")
    app.run_server(debug=debug, port=port)


def demo_recommendation(data: pd.DataFrame) -> None:
    """Run a simple demonstration of the recommendation engine.

    Args:
        data: The processed DataFrame
    """
    # Clean HTML entities in text fields for better display
    text_columns = ['track_name', 'artist_name', 'album_name']
    for col in text_columns:
        if col in data.columns:
            data[col] = data[col].apply(
                lambda x: html.unescape(str(x)) if pd.notna(x) else x
            )

    # Create the recommender engine
    recommender = MusicRecommender(data)

    # Get available genres and moods
    genres = recommender.get_available_genres()
    moods = recommender.get_available_moods()

    print("===== Music Recommender System =====")
    print(f"Loaded {len(data)} tracks with {len(genres)} genres and {len(moods)} moods")

    # Show some sample genres and moods
    print("\nSample Genres:", ", ".join(genres[:5]))
    print("Sample Moods:", ", ".join(moods[:5]))

    # Demonstrate different recommendation methods
    if genres:
        sample_genre = genres[0]
        print(f"\n----- Recommendations for genre '{sample_genre}' -----")
        genre_recs = recommender.recommend_by_genre(sample_genre, limit=5)
        for i, rec in enumerate(genre_recs, 1):
            print(f"{i}. Track: {rec.get('track_name', rec['track_id'])}")
            print(f"   Artist: {rec.get('artist_name', 'Unknown')}")
            print(f"   Genre: {', '.join(rec['genre_path'])}")
            print(f"   Mood: {', '.join(rec['mood_tags'])}")
            if 'energy' in rec and 'valence' in rec:
                print(f"   Energy: {rec['energy']:.2f}, Valence: {rec['valence']:.2f}")
            print()

    if moods:
        sample_mood = moods[0]
        print(f"\n----- Recommendations for mood '{sample_mood}' -----")
        mood_recs = recommender.recommend_by_mood(sample_mood, limit=5)
        for i, rec in enumerate(mood_recs, 1):
            print(f"{i}. Track: {rec.get('track_name', rec['track_id'])}")
            print(f"   Artist: {rec.get('artist_name', 'Unknown')}")
            print(f"   Genre: {', '.join(rec['genre_path'])}")
            print(f"   Mood: {', '.join(rec['mood_tags'])}")
            if 'energy' in rec and 'valence' in rec:
                print(f"   Energy: {rec['energy']:.2f}, Valence: {rec['valence']:.2f}")
            print()

    # Display explanation of the visual charts
    print(f"\n----- Visualization Explanation -----")
    print("Audio Features Bubble Chart:")
    print("  - Shows songs plotted by Valence (positivity) on X-axis and Energy on Y-axis")
    print("  - Each bubble represents a song, with size and color indicating different attributes")
    print("  - Quadrants represent different emotional qualities of music:\n")

    print("    | Calm Positive         | Energetic Positive     |")
    print("    | (High valence,        | (High valence,         |")
    print("    |  Low energy)          |  High energy)          |")
    print("    |------------------------|------------------------|")
    print("    | Calm Negative         | Energetic Negative     |")
    print("    | (Low valence,         | (Low valence,          |")
    print("    |  Low energy)          |  High energy)          |")
    print("\n")

    print("Similarity Network:")
    print("  - Shows connections between similar songs")
    print("  - Songs with similar audio features and mood tags are connected")
    print("  - Larger nodes indicate songs that are similar to many others\n")

    # New added info about clickable links
    print("New Features:")
    print("  - Track names in the web app are now clickable links that open in YouTube Music")
    print("  - All songs in the dataset are available for searching")
    print("  - Default number of search results increased to 50")
    print("  - Recommendation results can be scrolled through\n")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Music Recommender System')

    # Data source arguments
    parser.add_argument('--spotify', type=str, help='Path to Spotify features CSV')
    parser.add_argument('--genre', type=str, help='Path to Jamendo genre TSV')
    parser.add_argument('--mood', type=str, help='Path to Jamendo mood TSV')
    parser.add_argument('--metadata', type=str, help='Path to metadata TSV with track names')
    parser.add_argument('--processed', type=str, help='Path to processed dataset')
    parser.add_argument('--sample', action='store_true', help='Use sample data for testing')

    # Runtime arguments
    parser.add_argument('--demo', action='store_true', help='Run a demo instead of the web app')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--port', type=int, default=8040, help='Port for the web server')
    parser.add_argument('--save', type=str, help='Save processed data to this path')
    parser.add_argument('--limit', type=int, default=10, help='Limit number of recommendations')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Logging level')

    return parser.parse_args()


def main():
    """Main entry point for the music recommender system."""
    # Parse command line arguments
    args = parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level)

    # Set default dataset paths if not provided via command line
    if not args.spotify:
        default_spotify = "spotify_songs.csv"  # Changed from 1200_song_mapped.csv to spotify_songs.csv
        if os.path.exists(default_spotify):
            args.spotify = default_spotify

    if not args.genre:
        default_genre = "autotagging_genre.tsv"
        if os.path.exists(default_genre):
            args.genre = default_genre

    if not args.mood:
        default_mood = "autotagging_moodtheme.tsv"
        if os.path.exists(default_mood):
            args.mood = default_mood

    if not args.metadata and os.path.exists("raw_meta_data.tsv"):
        args.metadata = "raw_meta_data.tsv"

    # Load data
    data = load_data(
        spotify_path=args.spotify,
        genre_path=args.genre,
        mood_path=args.mood,
        metadata_path=args.metadata,
        processed_path=args.processed,
        use_sample=args.sample
    )

    # Save processed data if requested
    if args.save:
        save_processed_data(data, args.save)

    # Run the application
    if args.demo:
        demo_recommendation(data)
    else:
        run_recommender_app(data, debug=args.debug, port=args.port)


if __name__ == '__main__':
    main()
