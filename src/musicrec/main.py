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
import logging
from pathlib import Path

from .data.processor import build_dataset, save_processed_data
from .models.engine import MusicRecommender
from .ui.dash_app import MusicRecommenderDashApp
from .utils.logging import setup_logging

logger = logging.getLogger(__name__)


def create_sample_data(num_genres: int = 4, tracks_per_genre: int = 10) -> pd.DataFrame:
    """Create a sample dataset for testing when real data files are not available.

    Args:
        num_genres: Number of genre categories to generate (default: 4)
        tracks_per_genre: Number of tracks per genre (default: 10)

    Returns:
        Sample DataFrame for testing

    Raises:
        ValueError: If parameters are invalid or data generation fails
        RuntimeError: If sample data generation produces invalid results
    """
    logger.info(
        f"Creating sample dataset with {num_genres} genres, {tracks_per_genre} tracks per genre"
    )

    # Enhanced parameter validation
    if not isinstance(num_genres, int):
        raise ValueError(
            f"num_genres must be an integer, got {type(num_genres).__name__}"
        )
    if not isinstance(tracks_per_genre, int):
        raise ValueError(
            f"tracks_per_genre must be an integer, got {type(tracks_per_genre).__name__}"
        )
    if num_genres < 1:
        raise ValueError(f"num_genres must be at least 1, got {num_genres}")
    if num_genres > 100:
        raise ValueError(f"num_genres cannot exceed 100, got {num_genres}")
    if tracks_per_genre < 1:
        raise ValueError(f"tracks_per_genre must be at least 1, got {tracks_per_genre}")
    if tracks_per_genre > 1000:
        raise ValueError(f"tracks_per_genre cannot exceed 1000, got {tracks_per_genre}")

    # Calculate total expected tracks
    expected_total = num_genres * tracks_per_genre + 10  # +10 for subgenre tracks
    logger.info(f"Expected to generate approximately {expected_total} total tracks")

    try:
        # Create sample tracks
        sample_data = []

        # Rock genre tracks (only if we're generating at least 1 genre)
        if num_genres >= 1:
            for i in range(1, min(tracks_per_genre + 1, 11)):
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

                sample_data.append(
                    {
                        "track_id": track_id,
                        "track_name": track_name,
                        "artist_name": artist_name,
                        "genre_tags": [genre],
                        "mood_tags": mood_tags,
                        "duration": 180 + i * 10,
                        "energy": energy,
                        "valence": valence,
                        "tempo": tempo,
                        "genre_hierarchy": ["rock"],
                    }
                )

        # Metal genre tracks
        if num_genres >= 2:
            for i in range(1, min(tracks_per_genre + 1, 11)):
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

                sample_data.append(
                    {
                        "track_id": track_id,
                        "track_name": track_name,
                        "artist_name": artist_name,
                        "genre_tags": [genre],
                        "mood_tags": mood_tags,
                        "duration": 210 + i * 10,
                        "energy": energy,
                        "valence": valence,
                        "tempo": tempo,
                        "genre_hierarchy": ["metal"],
                    }
                )

        # Electronic genre tracks
        if num_genres >= 3:
            for i in range(1, min(tracks_per_genre + 1, 11)):
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

                sample_data.append(
                    {
                        "track_id": track_id,
                        "track_name": track_name,
                        "artist_name": artist_name,
                        "genre_tags": [genre],
                        "mood_tags": mood_tags,
                        "duration": 200 + i * 10,
                        "energy": energy,
                        "valence": valence,
                        "tempo": tempo,
                        "genre_hierarchy": ["electronic"],
                    }
                )

        # Acoustic genre tracks
        if num_genres >= 4:
            for i in range(1, min(tracks_per_genre + 1, 11)):
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

                sample_data.append(
                    {
                        "track_id": track_id,
                        "track_name": track_name,
                        "artist_name": artist_name,
                        "genre_tags": [genre],
                        "mood_tags": mood_tags,
                        "duration": 190 + i * 10,
                        "energy": energy,
                        "valence": valence,
                        "tempo": tempo,
                        "genre_hierarchy": ["acoustic"],
                    }
                )

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

            sample_data.append(
                {
                    "track_id": track_id,
                    "track_name": track_name,
                    "artist_name": artist_name,
                    "genre_tags": [genre],
                    "mood_tags": mood_tags,
                    "duration": 150 + i * 10,
                    "energy": energy,
                    "valence": valence,
                    "tempo": tempo,
                    "genre_hierarchy": ["rock", "punkrock"],
                }
            )

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

            sample_data.append(
                {
                    "track_id": track_id,
                    "track_name": track_name,
                    "artist_name": artist_name,
                    "genre_tags": [genre],
                    "mood_tags": mood_tags,
                    "duration": 170 + i * 10,
                    "energy": energy,
                    "valence": valence,
                    "tempo": tempo,
                    "genre_hierarchy": ["metal", "deathmetal"],
                }
            )

        # Create a DataFrame
        df = pd.DataFrame(sample_data)

        # Validate the generated data
        if df.empty:
            raise RuntimeError("Sample data generation resulted in empty DataFrame")

        required_columns = [
            "track_id",
            "track_name",
            "artist_name",
            "genre_tags",
            "mood_tags",
            "duration",
            "energy",
            "valence",
            "tempo",
            "genre_hierarchy",
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise RuntimeError(
                f"Generated data missing required columns: {missing_columns}"
            )

        # Validate data ranges
        if df["energy"].min() < 0 or df["energy"].max() > 1:
            raise RuntimeError("Energy values must be between 0 and 1")
        if df["valence"].min() < 0 or df["valence"].max() > 1:
            raise RuntimeError("Valence values must be between 0 and 1")
        if df["tempo"].min() <= 0:
            raise RuntimeError("Tempo values must be positive")
        if df["duration"].min() <= 0:
            raise RuntimeError("Duration values must be positive")

        # Check for duplicate track IDs
        if df["track_id"].duplicated().any():
            raise RuntimeError("Generated data contains duplicate track IDs")

        logger.info(
            f"Successfully generated {len(df)} sample tracks with {df['genre_hierarchy'].apply(lambda x: x[0]).nunique()} unique genres"
        )
        return df

    except Exception as e:
        logger.error(f"Failed to generate sample data: {e}")
        raise


def _validate_file_path(
    file_path: str, expected_extensions: list, description: str
) -> None:
    """Validate that a file path exists, is readable, and has the correct extension.

    Args:
        file_path: Path to the file to validate
        expected_extensions: List of allowed file extensions (e.g., ['.csv', '.tsv'])
        description: Human-readable description of the file for error messages

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the path is not a file or has wrong extension
        PermissionError: If the file is not readable
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"{description} not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"{description} is not a file: {file_path}")

    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"{description} is not readable: {file_path}")

    if expected_extensions and path.suffix.lower() not in expected_extensions:
        raise ValueError(
            f"{description} must have one of these extensions {expected_extensions}, "
            f"got: {path.suffix}"
        )


def load_data(
    spotify_path: Optional[str] = None,
    genre_path: Optional[str] = None,
    mood_path: Optional[str] = None,
    metadata_path: Optional[str] = None,
    use_sample: bool = False,
) -> pd.DataFrame:
    """Load and process music data from various sources.

    Args:
        spotify_path: Path to Spotify audio features CSV file
        genre_path: Path to Jamendo genre annotations TSV file
        mood_path: Path to Jamendo mood annotations TSV file
        metadata_path: Path to track metadata TSV file
        use_sample: If True, generate sample data instead of loading files

    Returns:
        Processed DataFrame ready for recommendation engine

    Raises:
        FileNotFoundError: If required files don't exist
        ValueError: If file paths are invalid
        PermissionError: If files are not readable
    """
    logger.info("Starting data loading process")

    try:
        # Check if we should use sample data
        if use_sample:
            logger.info("Using sample dataset for testing")
            return create_sample_data()

        # Validate file paths if provided
        validated_paths = {}
        try:
            if spotify_path:
                _validate_file_path(spotify_path, [".csv"], "Spotify file")
                validated_paths["spotify"] = spotify_path
            if genre_path:
                _validate_file_path(genre_path, [".tsv"], "Genre file")
                validated_paths["genre"] = genre_path
            if mood_path:
                _validate_file_path(mood_path, [".tsv"], "Mood file")
                validated_paths["mood"] = mood_path
            if metadata_path:
                _validate_file_path(metadata_path, [".tsv"], "Metadata file")
                validated_paths["metadata"] = metadata_path
        except (FileNotFoundError, ValueError, PermissionError) as e:
            logger.error(f"File validation failed: {e}")
            raise

        # Check if we have enough valid files
        required_files = ["spotify"]  # Minimum requirement
        missing = [key for key in required_files if key not in validated_paths]
        if missing:
            logger.warning(f"Missing required files: {missing}")

        # If no valid data sources, fall back to sample data
        if not validated_paths:
            logger.info("No valid data sources available, using sample dataset")
            return create_sample_data()

        # Build dataset from validated files
        logger.info(f"Building dataset from {len(validated_paths)} data sources")
        return build_dataset(
            validated_paths.get("spotify"),
            validated_paths.get("genre"),
            validated_paths.get("mood"),
            validated_paths.get("metadata"),
        )

    except Exception as e:
        logger.error(f"Data loading failed: {e}")
        raise

    # If no valid data sources, fall back to sample data
    logger.info("No valid data sources available, using sample dataset")
    return create_sample_data()


def run_recommender_app(
    data: pd.DataFrame, debug: bool = False, port: int = 8040
) -> None:
    """Run the music recommender Dash application.

    Args:
        data: The processed music dataset
        debug: Whether to run in debug mode (enables auto-reload)
        port: Port number for the web application (default: 8040)
    """
    try:
        print("\nBuilding recommendation engine...")
        recommender = MusicRecommender(data)

        print("Starting web application...")
        app = MusicRecommenderDashApp(recommender)
        app.run_server(debug=debug, port=port, host="0.0.0.0")

    except Exception as e:
        print(f"Error running application: {e}")
        raise


def run_demo_cli(data: pd.DataFrame, limit: int = 5) -> None:
    """Run a simple command-line demo of the recommendation system.

    Args:
        data: The processed music dataset
        limit: Number of recommendations to show (default: 5)
    """
    try:
        print("\nBuilding recommendation engine...")
        recommender = MusicRecommender(data)

        print("\n" + "=" * 50)
        print("🎵 MUSIC RECOMMENDER DEMO")
        print("=" * 50)

        # Show available genres and moods
        genres = recommender.get_available_genres()
        moods = recommender.get_available_moods()

        print(f"\nAvailable Genres ({len(genres)}): {', '.join(genres[:10])}")
        if len(genres) > 10:
            print(f"... and {len(genres) - 10} more")

        print(f"\nAvailable Moods ({len(moods)}): {', '.join(moods[:10])}")
        if len(moods) > 10:
            print(f"... and {len(moods) - 10} more")

        # Demo recommendations by genre
        if genres:
            sample_genre = genres[0]
            print(f"\n--- Recommendations for '{sample_genre}' genre ---")
            genre_recs = recommender.recommend_by_genre(sample_genre, limit)

            for i, track in enumerate(genre_recs, 1):
                track_name = track.get("track_name", "Unknown")
                artist_name = track.get("artist_name", "Unknown")
                moods = ", ".join(track.get("mood_tags", []))
                print(f"{i}. {track_name} by {artist_name}")
                print(f"   Moods: {moods}")

        # Demo recommendations by mood
        if moods:
            sample_mood = moods[0]
            print(f"\n--- Recommendations for '{sample_mood}' mood ---")
            mood_recs = recommender.recommend_by_mood(sample_mood, limit)

            for i, track in enumerate(mood_recs, 1):
                track_name = track.get("track_name", "Unknown")
                artist_name = track.get("artist_name", "Unknown")
                genre_path = " > ".join(track.get("genre_path", []))
                print(f"{i}. {track_name} by {artist_name}")
                print(f"   Genre: {genre_path}")

        print("\n" + "=" * 50)
        print("Demo completed! Use --no-demo to start the web interface.")
        print("=" * 50)

    except Exception as e:
        print(f"Error running demo: {e}")
        raise


def main() -> None:
    """Main function to run the music recommender system."""
    parser = argparse.ArgumentParser(description="CSC111 Music Recommender System")
    parser.add_argument("--spotify", type=str, help="Path to Spotify songs CSV file")
    parser.add_argument("--genre", type=str, help="Path to genre annotations TSV file")
    parser.add_argument("--mood", type=str, help="Path to mood annotations TSV file")
    parser.add_argument("--metadata", type=str, help="Path to metadata TSV file")
    parser.add_argument(
        "--sample", action="store_true", help="Use sample data for testing"
    )
    parser.add_argument(
        "--save", type=str, help="Save processed data to file (CSV or pickle)"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Run CLI demo instead of web app"
    )
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument(
        "--port",
        type=int,
        default=8040,
        help="Port for web application (default: 8040)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of recommendations to show in demo (1-1000)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument("--log-file", type=str, help="Path to log file (optional)")

    args = parser.parse_args()

    # Set up logging
    setup_logging(level=args.log_level, log_file=args.log_file)
    logger.info("Starting Music Recommender System")

    # Validate CLI parameters
    if args.limit < 1 or args.limit > 1000:
        raise ValueError(f"--limit must be between 1 and 1000, got: {args.limit}")
    if args.port < 1024 or args.port > 65535:
        raise ValueError(f"--port must be between 1024 and 65535, got: {args.port}")

    try:
        # Load the data
        data = load_data(
            spotify_path=args.spotify,
            genre_path=args.genre,
            mood_path=args.mood,
            metadata_path=args.metadata,
            use_sample=args.sample,
        )

        logger.info(f"Loaded dataset with {len(data)} tracks")

        # Save processed data if requested
        if args.save:
            print(f"Saving processed data to {args.save}...")
            save_processed_data(data, args.save)
            print("Data saved successfully!")

        # Run demo or web app
        if args.demo:
            run_demo_cli(data, limit=args.limit)
        else:
            run_recommender_app(data, debug=args.debug, port=args.port)

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        logger.info("Application interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    main()
