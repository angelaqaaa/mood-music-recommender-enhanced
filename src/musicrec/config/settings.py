"""Configuration settings for the music recommender system.

This module provides centralized configuration management, including default settings
for data file paths and other application settings.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Default configuration settings
DEFAULT_CONFIG = {
    "data": {
        "base_path": "data",
        "spotify_path": "data/spotify_songs.csv",
        "genre_path": "data/autotagging_genre.tsv",
        "mood_path": "data/autotagging_moodtheme.tsv",
        "metadata_path": "data/raw_meta_data.tsv",
        "processed_data_path": "data/processed_data.pkl",
    },
    "retry": {"max_attempts": 3, "backoff_seconds": 1.0, "backoff_multiplier": 2.0},
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    },
    "app": {"default_port": 8040, "default_limit": 10},
}

# Environment variable mappings
ENV_MAPPINGS = {
    "MUSICREC_DATA_PATH": "data.base_path",
    "MUSICREC_SPOTIFY_PATH": "data.spotify_path",
    "MUSICREC_GENRE_PATH": "data.genre_path",
    "MUSICREC_MOOD_PATH": "data.mood_path",
    "MUSICREC_METADATA_PATH": "data.metadata_path",
    "MUSICREC_PROCESSED_PATH": "data.processed_data_path",
    "MUSICREC_MAX_ATTEMPTS": "retry.max_attempts",
    "MUSICREC_BACKOFF_SECONDS": "retry.backoff_seconds",
    "MUSICREC_LOG_LEVEL": "logging.level",
    "MUSICREC_DEFAULT_PORT": "app.default_port",
    "MUSICREC_DEFAULT_LIMIT": "app.default_limit",
}


def _set_nested_value(config: Dict[str, Any], key_path: str, value: Any) -> None:
    """Set a nested dictionary value using dot notation."""
    keys = key_path.split(".")
    current = config
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    # Convert string values to appropriate types
    if isinstance(value, str):
        if (
            key_path.endswith("_attempts")
            or key_path.endswith("_port")
            or key_path.endswith("_limit")
        ):
            try:
                value = int(value)
            except ValueError:
                logger.warning(f"Could not convert {key_path}={value} to integer")
        elif key_path.endswith("_seconds") or key_path.endswith("_multiplier"):
            try:
                value = float(value)
            except ValueError:
                logger.warning(f"Could not convert {key_path}={value} to float")

    current[keys[-1]] = value


def _get_nested_value(config: Dict[str, Any], key_path: str) -> Any:
    """Get a nested dictionary value using dot notation."""
    keys = key_path.split(".")
    current = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from defaults, config file, and environment variables.

    Args:
        config_path: Optional path to JSON config file

    Returns:
        Dictionary containing merged configuration
    """
    # Start with defaults
    config = DEFAULT_CONFIG.copy()

    # Load from config file if provided
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, "r") as f:
                file_config = json.load(f)

            # Merge file config into defaults
            for section, values in file_config.items():
                if (
                    section in config
                    and isinstance(values, dict)
                    and isinstance(config[section], dict)
                ):
                    config[section].update(values)  # type: ignore
                else:
                    config[section] = values

            logger.info(f"Loaded config from {config_path}")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not load config file {config_path}: {e}")

    # Override with environment variables
    for env_var, config_key in ENV_MAPPINGS.items():
        env_value = os.environ.get(env_var)
        if env_value is not None:
            _set_nested_value(config, config_key, env_value)
            logger.debug(f"Override from {env_var}: {config_key}={env_value}")

    # Handle base path override
    base_path = os.environ.get("MUSICREC_DATA_PATH")
    if base_path:
        base_dir = Path(base_path)
        # Update all data paths to use the new base directory
        for key in [
            "spotify_path",
            "genre_path",
            "mood_path",
            "metadata_path",
            "processed_data_path",
        ]:
            current_path = config["data"][key]  # type: ignore
            if not Path(current_path).is_absolute():
                # Keep the original filename, just change the directory
                filename = Path(current_path).name
                config["data"][key] = str(base_dir / filename)  # type: ignore

    return config


def get_data_paths(config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """Get data file paths from configuration.

    Args:
        config: Optional config dictionary, will load default if not provided

    Returns:
        Dictionary mapping data types to file paths
    """
    if config is None:
        config = load_config()

    return config["data"].copy()


def get_retry_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get retry configuration settings.

    Args:
        config: Optional config dictionary, will load default if not provided

    Returns:
        Dictionary containing retry settings
    """
    if config is None:
        config = load_config()

    return config["retry"].copy()


def get_app_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get application configuration settings.

    Args:
        config: Optional config dictionary, will load default if not provided

    Returns:
        Dictionary containing app settings
    """
    if config is None:
        config = load_config()

    return config["app"].copy()


def resolve_path(path: str, base_dir: Optional[str] = None) -> str:
    """Resolve a file path, making it absolute if needed.

    Args:
        path: The file path to resolve
        base_dir: Optional base directory for relative paths

    Returns:
        Absolute file path
    """
    path_obj = Path(path)

    if path_obj.is_absolute():
        return str(path_obj)

    if base_dir:
        return str(Path(base_dir) / path_obj)

    # Default to current working directory
    return str(Path.cwd() / path_obj)
