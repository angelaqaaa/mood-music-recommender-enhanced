"""CSC111 Winter 2025: A Mood-Driven Music Recommender with Genre Hierarchies

Module for processing music datasets and merging them into a unified representation.
This module handles loading and parsing the Spotify and Jamendo datasets.

Copyright and Usage Information
===============================
This file is Copyright (c) 2025 Qian (Angela) Su & Mengxuan (Connie) Guo.
"""

import pandas as pd
import numpy as np
from typing import List
import python_ta
import html


def load_spotify_data(filepath: str) -> pd.DataFrame:
    """Load the Spotify audio features dataset.

    Args:
        filepath: Path to the Spotify CSV file

    Returns:
        DataFrame containing the Spotify audio features
    """
    try:
        spotify_df = pd.read_csv(filepath)

        # Check if this is the new spotify_songs.csv format or the old 1200_song_mapped.csv
        if 'track_name' in spotify_df.columns and 'danceability' in spotify_df.columns:
            # This is the new spotify_songs.csv format
            print(f"Detected spotify_songs.csv format with {len(spotify_df)} tracks")

            # Rename columns to match what our system expects
            column_mapping = {
                'track_name': 'track',
                'track_artist': 'artist',
                'duration_ms': 'duration (ms)'
            }

            spotify_df.rename(columns=column_mapping, inplace=True)

            # Add the uri column (using track_id as a substitute)
            if 'track_id' in spotify_df.columns and 'uri' not in spotify_df.columns:
                spotify_df['uri'] = spotify_df['track_id'].apply(lambda x: f"spotify:track:{x}")

        # Ensure essential columns exist
        required_columns = {'energy', 'valence', 'tempo'}
        missing_columns = required_columns - set(spotify_df.columns)

        if missing_columns:
            print(f"Warning: Spotify dataset missing columns: {missing_columns}")

        # Decode HTML entities in track and artist names
        if 'track' in spotify_df.columns:
            spotify_df['track'] = spotify_df['track'].apply(lambda x: html.unescape(str(x)) if pd.notna(x) else x)
        if 'artist' in spotify_df.columns:
            spotify_df['artist'] = spotify_df['artist'].apply(lambda x: html.unescape(str(x)) if pd.notna(x) else x)

        return spotify_df
    except Exception as e:
        print(f"Error reading Spotify file: {e}")
        # Create a minimal DataFrame with required columns
        return pd.DataFrame(columns=['track', 'artist', 'energy', 'valence', 'tempo'])


def load_jamendo_genre_data(filepath: str) -> pd.DataFrame:
    """Load the Jamendo genre dataset.

    Args:
        filepath: Path to the Jamendo genre TSV file

    Returns:
        DataFrame containing the Jamendo genre data
    """
    try:
        # Read the file as text first to handle varying number of columns
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Process each line manually
        data = []
        for line in lines:
            # Skip header or empty lines
            if not line.strip() or line.startswith('TRACK_ID'):
                continue

            # Split by tabs
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue

            # Extract track ID and duration from the first few columns
            track_id = parts[0].strip()
            duration = float(parts[4].strip()) if len(parts) > 4 else 0.0

            # Extract all genre tags from remaining columns
            genre_tags = []
            for part in parts[5:]:
                if part.strip().startswith('genre---'):
                    genre_tags.append(part.strip().replace('genre---', ''))

            # Add to data
            data.append({
                'TRACK_ID': track_id,
                'DURATION': duration,
                'genre_tags': genre_tags
            })

        # Create DataFrame
        print(f"Loaded {len(data)} tracks with genre information")
        return pd.DataFrame(data)

    except Exception as e:
        print(f"Error reading genre file: {e}")
        # Create a minimal DataFrame with required columns
        return pd.DataFrame(columns=['TRACK_ID', 'DURATION', 'genre_tags'])


def load_jamendo_mood_data(filepath: str) -> pd.DataFrame:
    """Load the Jamendo mood/theme dataset.

    Args:
        filepath: Path to the Jamendo mood/theme TSV file

    Returns:
        DataFrame containing the Jamendo mood/theme data
    """
    try:
        # Read the file as text first to handle varying number of columns
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Process each line manually
        data = []
        for line in lines:
            # Skip header or empty lines
            if not line.strip() or line.startswith('TRACK_ID'):
                continue

            # Split by tabs
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue

            # Extract track ID and duration from the first few columns
            track_id = parts[0].strip()
            duration = float(parts[4].strip()) if len(parts) > 4 else 0.0

            # Extract all mood tags from remaining columns
            mood_tags = []
            for part in parts[5:]:
                if part.strip().startswith('mood/theme---'):
                    mood_tags.append(part.strip().replace('mood/theme---', ''))

            # Add to data
            data.append({
                'TRACK_ID': track_id,
                'DURATION': duration,
                'mood_tags': mood_tags
            })

        # Create DataFrame
        print(f"Loaded {len(data)} tracks with mood information")
        return pd.DataFrame(data)

    except Exception as e:
        print(f"Error reading mood file: {e}")
        # Create a minimal DataFrame with required columns
        return pd.DataFrame(columns=['TRACK_ID', 'DURATION', 'mood_tags'])


def load_metadata(filepath: str) -> pd.DataFrame:
    """Load the raw metadata file that contains track names.

    Args:
        filepath: Path to the raw metadata TSV file

    Returns:
        DataFrame containing track names and IDs
    """
    try:
        # Try loading with pandas first
        try:
            metadata_df = pd.read_csv(filepath, sep='\t', encoding='utf-8')
            print(f"Loaded metadata with pandas: {len(metadata_df)} tracks")

            # Decode HTML entities in text fields
            text_columns = ['TRACK_NAME', 'ARTIST_NAME', 'ALBUM_NAME']
            for col in text_columns:
                if col in metadata_df.columns:
                    metadata_df[col] = metadata_df[col].apply(
                        lambda x: html.unescape(str(x)) if pd.notna(x) else x
                    )

            return metadata_df
        except Exception as e:
            print(f"Error loading with pandas: {e}")
            # Fall back to manual loading

        # Read the file as text to handle any formatting issues
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Get header
        header = lines[0].strip().split('\t')

        # Process each line manually
        data = []
        for line in lines[1:]:  # Skip header
            if not line.strip():
                continue

            # Split by tabs
            parts = line.strip().split('\t')
            if len(parts) < 4:  # Need at least track_id and track_name
                continue

            # Create a row dict
            row = {}
            for i, part in enumerate(parts):
                if i < len(header):
                    # Decode HTML entities if this is a text field like TRACK_NAME or ARTIST_NAME
                    if header[i] in ['TRACK_NAME', 'ARTIST_NAME', 'ALBUM_NAME']:
                        row[header[i]] = html.unescape(part)
                    else:
                        row[header[i]] = part

            data.append(row)

        # Create DataFrame
        metadata_df = pd.DataFrame(data)
        print(f"Loaded metadata manually: {len(metadata_df)} tracks")
        return metadata_df

    except Exception as e:
        print(f"Error reading metadata file: {e}")
        # Create a minimal DataFrame with required columns
        return pd.DataFrame(columns=['TRACK_ID', 'TRACK_NAME'])


def extract_genre_hierarchy(genre_tags: List[str]) -> List[str]:
    """Extract a genre hierarchy from a list of genre tags.

    Args:
        genre_tags: A list of genre strings (e.g., ['metal', 'rock', 'punkrock'])

    Returns:
        A list representing the genre hierarchy path

    >>> extract_genre_hierarchy(['metal'])
    ['metal']
    >>> extract_genre_hierarchy(['rock', 'punkrock'])
    ['rock', 'punkrock']
    >>> extract_genre_hierarchy(['metal', 'deathmetal'])
    ['metal', 'deathmetal']
    """
    # Define genre parent relationships
    # This is a simplified mapping; in a real project you might want more sophisticated rules
    genre_parents = {
        'punkrock': 'rock',
        'hardrock': 'rock',
        'poprock': 'rock',
        'indierock': 'rock',
        'progressiverock': 'rock',
        'alternativerock': 'rock',
        'folkrock': 'rock',

        'deathmetal': 'metal',
        'blackmetal': 'metal',
        'heavymetal': 'metal',
        'thrashmetal': 'metal',
        'powermetal': 'metal',

        'house': 'electronic',
        'techno': 'electronic',
        'trance': 'electronic',
        'ambient': 'electronic',
        'idm': 'electronic',
        'dnb': 'electronic',
        'dubstep': 'electronic',

        'hiphop': 'hip-hop',
        'rap': 'hip-hop',

        'folk': 'acoustic',
        'country': 'acoustic',
        'acoustic': 'acoustic',

        'funk': 'rnb',
        'disco': 'dance',
        'pop': 'popular',

        # Adding more mappings for the Spotify playlist genres
        'dance pop': 'pop',
        'post-teen pop': 'pop',
        'electropop': 'pop',
        'indie pop': 'pop',

        'modern rock': 'rock',
        'permanent wave': 'rock',
        'alternative metal': 'metal',

        'hip hop': 'hip-hop',
        'southern hip hop': 'hip-hop',
        'gangster rap': 'hip-hop',

        'edm': 'electronic',
        'electro house': 'electronic',
        'big room': 'electronic',

        'contemporary country': 'country',
        'country road': 'country'
    }

    if not genre_tags or len(genre_tags) == 0:
        return ['unknown']

    # Start with a set to avoid duplicates
    hierarchy_set = set()

    # Process each genre tag
    for genre in genre_tags:
        genre_lower = genre.lower()
        # Check if this genre has a parent
        if genre_lower in genre_parents:
            parent = genre_parents[genre_lower]
            hierarchy_set.add(parent)
        # Add the original genre
        hierarchy_set.add(genre_lower)

    # Convert to list and sort by parent-child relationships
    hierarchy = list(hierarchy_set)

    # Sort hierarchy to ensure parent genres come before child genres
    # This is a simplified sort; in a real project you might need a more complex algorithm
    sorted_hierarchy = []

    # First add high-level genres (those that are parents but not children)
    parent_genres = set(genre_parents.values())
    child_genres = set(genre_parents.keys())
    high_level_genres = parent_genres - child_genres

    for genre in hierarchy:
        if genre in high_level_genres:
            sorted_hierarchy.append(genre)

    # Then add mid-level genres (those that are both parents and children)
    mid_level_genres = parent_genres.intersection(child_genres)
    for genre in hierarchy:
        if genre in mid_level_genres:
            sorted_hierarchy.append(genre)

    # Finally add leaf genres (those that are children but not parents)
    leaf_genres = child_genres - parent_genres
    for genre in hierarchy:
        if genre in leaf_genres or (genre not in high_level_genres and genre not in mid_level_genres):
            sorted_hierarchy.append(genre)

    # If the hierarchy is empty (no matches found), use the first genre tag
    if not sorted_hierarchy and genre_tags:
        sorted_hierarchy = [genre_tags[0].lower()]

    return sorted_hierarchy


def merge_datasets(spotify_df: pd.DataFrame, genre_df: pd.DataFrame,
                   mood_df: pd.DataFrame, metadata_df: pd.DataFrame = None) -> pd.DataFrame:
    """Merge the Spotify and Jamendo datasets into a unified representation.

    Args:
        spotify_df: Spotify audio features DataFrame
        genre_df: Jamendo genre DataFrame
        mood_df: Jamendo mood/theme DataFrame
        metadata_df: Optional metadata DataFrame with track names

    Returns:
        Merged DataFrame containing all features
    """
    print("Merging datasets...")

    # First, merge genre and mood data (same source, so we can join on TRACK_ID)
    # We'll do an outer join to keep all tracks
    jamendo_merged = pd.merge(
        genre_df[['TRACK_ID', 'DURATION', 'genre_tags']],
        mood_df[['TRACK_ID', 'mood_tags']],
        on='TRACK_ID',
        how='outer'
    )

    # Create a unified DataFrame
    # This is a placeholder for real matching between Spotify and Jamendo data
    # In a real project, you might need more sophisticated matching based on track names, etc.

    # Create a unified ID field (we'll use TRACK_ID from Jamendo)
    merged_df = jamendo_merged.copy()
    merged_df.rename(columns={'TRACK_ID': 'track_id'}, inplace=True)

    # Add track names if metadata is available
    if metadata_df is not None:
        print("Adding track names from metadata...")
        # Rename columns to match our schema
        metadata_df_renamed = metadata_df.rename(columns={
            'TRACK_ID': 'track_id',
            'TRACK_NAME': 'track_name',
            'ARTIST_NAME': 'artist_name',
            'ALBUM_NAME': 'album_name'
        })

        # Merge with metadata to get track names
        track_columns = ['track_id', 'track_name', 'artist_name', 'album_name']
        avail_columns = [col for col in track_columns if col in metadata_df_renamed.columns]

        if avail_columns:
            print(f"Merging on metadata columns: {avail_columns}")
            merged_df = pd.merge(
                merged_df,
                metadata_df_renamed[avail_columns],
                on='track_id',
                how='left'
            )

    # For the new spotify_songs.csv format, we need to handle it differently
    if 'track_id' in spotify_df.columns:
        print("Using track_id from the Spotify dataset for matching")
        # Use direct track_id matching if possible
        spotify_tracks = {track_id: idx for idx, track_id in enumerate(spotify_df['track_id'])}

    # Create dummy mappings for audio features
    # In a real project, you'd actually match Spotify and Jamendo tracks
    # But here we'll just assign random values for demonstration

    # For tracks that have Jamendo IDs but no Spotify features
    if len(merged_df) > len(spotify_df):
        # Take Spotify features and repeat them to match Jamendo's length
        sample_indices = np.random.choice(len(spotify_df), size=len(merged_df), replace=True)

        # Add audio features from Spotify
        merged_df['energy'] = spotify_df.iloc[sample_indices]['energy'].values
        merged_df['valence'] = spotify_df.iloc[sample_indices]['valence'].values
        merged_df['tempo'] = spotify_df.iloc[sample_indices]['tempo'].values

        # Add additional columns that might be useful
        if 'danceability' in spotify_df.columns:
            merged_df['danceability'] = spotify_df.iloc[sample_indices]['danceability'].values
        if 'acousticness' in spotify_df.columns:
            merged_df['acousticness'] = spotify_df.iloc[sample_indices]['acousticness'].values

        # If spotify_songs.csv format, add track_name and artist_name from Spotify if missing
        if 'track' in spotify_df.columns and 'artist' in spotify_df.columns:
            for i, row in merged_df.iterrows():
                if pd.isna(row.get('track_name')):
                    merged_df.at[i, 'track_name'] = spotify_df.iloc[sample_indices[i]]['track']
                if pd.isna(row.get('artist_name')):
                    merged_df.at[i, 'artist_name'] = spotify_df.iloc[sample_indices[i]]['artist']

    # Fill missing values
    # For tracks that have genre but no mood
    merged_df['mood_tags'] = merged_df['mood_tags'].apply(
        lambda x: [] if isinstance(x, float) and pd.isna(x) else x
    )

    # For tracks that have mood but no genre
    merged_df['genre_tags'] = merged_df['genre_tags'].apply(
        lambda x: ['unknown'] if isinstance(x, float) and pd.isna(x) else x
    )

    # Make sure track_name is available
    if 'track_name' not in merged_df.columns:
        merged_df['track_name'] = merged_df['track_id']
    else:
        # Fill missing track names with track_id
        merged_df['track_name'] = merged_df['track_name'].fillna(merged_df['track_id'])

    # Convert duration to seconds if it's in milliseconds in Spotify
    # Jamendo data typically has duration in seconds
    if 'DURATION' in merged_df.columns and merged_df['DURATION'].mean() > 1000:
        merged_df['duration'] = merged_df['DURATION'] / 1000
    elif 'DURATION' in merged_df.columns:
        merged_df['duration'] = merged_df['DURATION']

    # If we have Spotify song data with playlist_genre, use it to supplement genre_tags
    if 'playlist_genre' in spotify_df.columns and 'playlist_subgenre' in spotify_df.columns:
        print("Adding playlist genre and subgenre information from Spotify data")

        # Create a mapping to add Spotify genres to genre_tags
        sample_indices = np.random.choice(len(spotify_df), size=len(merged_df), replace=True)

        for i, row in merged_df.iterrows():
            if not row['genre_tags'] or row['genre_tags'] == ['unknown']:
                # Get genre and subgenre from Spotify data
                playlist_genre = spotify_df.iloc[sample_indices[i]]['playlist_genre']
                playlist_subgenre = spotify_df.iloc[sample_indices[i]]['playlist_subgenre']

                # Add both to genre_tags if they're not already there
                genre_tags = []
                if pd.notna(playlist_genre) and playlist_genre not in genre_tags:
                    genre_tags.append(playlist_genre)
                if pd.notna(playlist_subgenre) and playlist_subgenre not in genre_tags:
                    genre_tags.append(playlist_subgenre)

                if genre_tags:
                    merged_df.at[i, 'genre_tags'] = genre_tags

    print(f"Final merged dataset contains {len(merged_df)} tracks")
    return merged_df


def preprocess_merged_data(merged_df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the merged dataset for use in the music recommender.

    Args:
        merged_df: The merged DataFrame from merge_datasets

    Returns:
        Processed DataFrame ready for the recommender system
    """
    print("Preprocessing merged data...")

    # Create a copy to avoid modifying the original
    processed_df = merged_df.copy()

    # Extract genre hierarchies
    processed_df['genre_hierarchy'] = processed_df['genre_tags'].apply(extract_genre_hierarchy)

    # Define mood categories based on valence and energy
    # These are simplified rules - in a real application, you might want more sophisticated categorization
    def categorize_mood(row):
        """Categorize a track's mood based on valence and energy values."""
        # Add inferred moods based on audio features
        inferred_moods = []

        if 'valence' in row and 'energy' in row:
            valence = row['valence'] if not pd.isna(row['valence']) else 0.5
            energy = row['energy'] if not pd.isna(row['energy']) else 0.5

            # High valence + high energy = happy/energetic
            if valence > 0.7 and energy > 0.7:
                inferred_moods.append('happy')
                inferred_moods.append('energetic')

            # High valence + low energy = peaceful/relaxed
            elif valence > 0.7 and energy < 0.4:
                inferred_moods.append('peaceful')
                inferred_moods.append('relaxed')

            # Low valence + high energy = angry/intense
            elif valence < 0.3 and energy > 0.7:
                inferred_moods.append('angry')
                inferred_moods.append('intense')

            # Low valence + low energy = sad/melancholic
            elif valence < 0.3 and energy < 0.4:
                inferred_moods.append('sad')
                inferred_moods.append('melancholic')

            # Medium valence + high energy = upbeat
            elif 0.4 <= valence <= 0.6 and energy > 0.7:
                inferred_moods.append('upbeat')

            # Medium valence + low energy = chill
            elif 0.4 <= valence <= 0.6 and energy < 0.4:
                inferred_moods.append('chill')

        # Combine explicitly tagged moods with inferred moods
        existing_moods = row['mood_tags'] if isinstance(row['mood_tags'], list) else []
        combined_moods = list(set(existing_moods + inferred_moods))

        return combined_moods

    # Apply the mood categorization
    processed_df['mood_tags'] = processed_df.apply(categorize_mood, axis=1)

    # Fill any remaining NaN values with appropriate defaults
    for col in processed_df.columns:
        if col in ['energy', 'valence', 'tempo', 'danceability', 'acousticness']:
            processed_df[col] = processed_df[col].fillna(processed_df[col].mean())

    print("Data preprocessing complete")
    return processed_df


def build_dataset(spotify_path: str, genre_path: str, mood_path: str,
                  metadata_path: str = None) -> pd.DataFrame:
    """Build the complete dataset by loading and merging all data sources.

    Args:
        spotify_path: Path to the Spotify features CSV
        genre_path: Path to the Jamendo genre TSV
        mood_path: Path to the Jamendo mood TSV
        metadata_path: Optional path to the metadata TSV with track names

    Returns:
        Processed DataFrame ready for the recommender system
    """
    # Load the datasets
    try:
        print("Loading Spotify data...")
        spotify_df = load_spotify_data(spotify_path)
        print(f"✓ Loaded {len(spotify_df)} tracks from Spotify dataset")

        print("Loading genre data...")
        genre_df = load_jamendo_genre_data(genre_path)
        print(f"✓ Loaded {len(genre_df)} tracks with genre info")

        print("Loading mood data...")
        mood_df = load_jamendo_mood_data(mood_path)
        print(f"✓ Loaded {len(mood_df)} tracks with mood info")

        # Load metadata if provided
        metadata_df = None
        if metadata_path:
            print("Loading metadata with track names...")
            metadata_df = load_metadata(metadata_path)
            print(f"✓ Loaded metadata for {len(metadata_df)} tracks")

        # Merge the datasets
        print("Merging datasets...")
        merged_df = merge_datasets(spotify_df, genre_df, mood_df, metadata_df)
        print(f"✓ Created merged dataset with {len(merged_df)} tracks")

        # Preprocess the merged dataset
        print("Preprocessing data (extracting hierarchies, categorizing moods)...")
        processed_df = preprocess_merged_data(merged_df)
        print(f"✓ Finished preprocessing")

        # Limit the size for faster processing if it's too large
        if len(processed_df) > 500:
            print(f"Dataset is large with {len(processed_df)} tracks. Using full dataset, "
                  f"but similarity calculations will be limited.")

        return processed_df

    except Exception as e:
        print(f"Error building dataset: {e}")
        # Return an empty DataFrame with the expected columns if loading fails
        return pd.DataFrame(columns=['track_id', 'track_name', 'genre_tags', 'mood_tags',
                                     'duration', 'energy', 'valence', 'tempo', 'genre_hierarchy'])


def save_processed_data(df: pd.DataFrame, output_path: str) -> None:
    """Save the processed dataset to a CSV file.

    Args:
        df: The processed DataFrame
        output_path: Path to save the CSV file
    """
    try:
        # Convert list columns to string format for saving
        df_to_save = df.copy()

        # Convert list columns to strings
        for col in ['mood_tags', 'genre_tags', 'genre_hierarchy']:
            if col in df_to_save.columns:
                df_to_save[col] = df_to_save[col].apply(lambda x: ';'.join(x) if isinstance(x, list) else x)

        # Save to CSV
        df_to_save.to_csv(output_path, index=False)
        print(f"Dataset saved to {output_path}")

    except Exception as e:
        print(f"Error saving dataset: {e}")


def load_processed_data(input_path: str) -> pd.DataFrame:
    """Load a preprocessed dataset from a CSV file.

    Args:
        input_path: Path to the CSV file

    Returns:
        The loaded DataFrame
    """
    try:
        # Load the CSV file
        df = pd.read_csv(input_path)

        # Decode HTML entities in text columns
        text_columns = ['track_name', 'artist_name', 'album_name']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: html.unescape(str(x)) if pd.notna(x) else x
                )

        # Convert string columns back to lists
        for col in ['mood_tags', 'genre_tags', 'genre_hierarchy']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x.split(';') if isinstance(x, str) else [])

        return df

    except Exception as e:
        print(f"Error loading dataset: {e}")
        return pd.DataFrame()


if __name__ == '__main__':
    import doctest

    doctest.testmod()

    python_ta.check_all(config={
        'extra-imports': ['pandas', 'numpy', 'typing', 'html'],
        'allowed-io': ['save_processed_data', 'build_dataset', 'load_processed_data',
                       'load_jamendo_genre_data', 'load_jamendo_mood_data', 'load_metadata',
                       'merge_datasets', 'preprocess_merged_data', 'load_spotify_data'],
        'max-line-length': 100,
        'disable': ['E1136']
    })
