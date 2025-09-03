"""Tests for configuration management functionality."""

import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from src.musicrec.config.settings import (
    load_config, get_data_paths, get_retry_config, get_app_config,
    resolve_path, DEFAULT_CONFIG, ENV_MAPPINGS
)


class TestDefaultConfig:
    """Test default configuration values."""
    
    def test_default_config_structure(self):
        """Test that default config has expected structure."""
        assert 'data' in DEFAULT_CONFIG
        assert 'retry' in DEFAULT_CONFIG
        assert 'logging' in DEFAULT_CONFIG
        assert 'app' in DEFAULT_CONFIG
        
    def test_data_config_keys(self):
        """Test that data config has all expected keys."""
        data_config = DEFAULT_CONFIG['data']
        expected_keys = [
            'spotify_path', 'genre_path', 'mood_path', 
            'metadata_path', 'processed_data_path'
        ]
        for key in expected_keys:
            assert key in data_config, f"Missing data config key: {key}"
    
    def test_retry_config_values(self):
        """Test that retry config has reasonable defaults."""
        retry_config = DEFAULT_CONFIG['retry']
        assert isinstance(retry_config['max_attempts'], int)
        assert retry_config['max_attempts'] > 0
        assert isinstance(retry_config['backoff_seconds'], (int, float))
        assert retry_config['backoff_seconds'] > 0
        assert isinstance(retry_config['backoff_multiplier'], (int, float))
        assert retry_config['backoff_multiplier'] > 1
    
    def test_app_config_values(self):
        """Test that app config has reasonable defaults."""
        app_config = DEFAULT_CONFIG['app']
        assert isinstance(app_config['default_port'], int)
        assert 1024 <= app_config['default_port'] <= 65535
        assert isinstance(app_config['default_limit'], int)
        assert app_config['default_limit'] > 0


class TestConfigLoading:
    """Test configuration loading functionality."""
    
    def test_load_config_defaults_only(self):
        """Test loading config with defaults only."""
        config = load_config()
        
        # Should have all default sections
        assert 'data' in config
        assert 'retry' in config
        assert 'logging' in config
        assert 'app' in config
        
        # Should match default values
        assert config['retry']['max_attempts'] == DEFAULT_CONFIG['retry']['max_attempts']
    
    def test_load_config_with_file(self):
        """Test loading config from JSON file."""
        test_config = {
            "data": {
                "spotify_path": "custom/spotify.csv"
            },
            "retry": {
                "max_attempts": 5,
                "backoff_seconds": 2.0
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            config_path = f.name
        
        try:
            config = load_config(config_path)
            
            # Should merge with defaults
            assert config['data']['spotify_path'] == "custom/spotify.csv"
            assert config['retry']['max_attempts'] == 5
            assert config['retry']['backoff_seconds'] == 2.0
            
            # Should preserve other defaults
            assert config['data']['genre_path'] == DEFAULT_CONFIG['data']['genre_path']
            assert config['retry']['backoff_multiplier'] == DEFAULT_CONFIG['retry']['backoff_multiplier']
        finally:
            os.unlink(config_path)
    
    def test_load_config_nonexistent_file(self):
        """Test loading config with non-existent file path."""
        config = load_config("/nonexistent/path/config.json")
        
        # Should fall back to defaults
        assert config == DEFAULT_CONFIG
    
    def test_load_config_invalid_json(self):
        """Test loading config with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {")
            config_path = f.name
        
        try:
            config = load_config(config_path)
            
            # Should fall back to defaults
            assert config == DEFAULT_CONFIG
        finally:
            os.unlink(config_path)


class TestEnvironmentOverrides:
    """Test environment variable override functionality."""
    
    def test_env_override_data_paths(self):
        """Test that environment variables override data paths."""
        with patch.dict(os.environ, {
            'MUSICREC_SPOTIFY_PATH': 'env/spotify.csv',
            'MUSICREC_GENRE_PATH': 'env/genre.tsv'
        }):
            config = load_config()
            
            assert config['data']['spotify_path'] == 'env/spotify.csv'
            assert config['data']['genre_path'] == 'env/genre.tsv'
            # Other paths should remain default
            assert config['data']['mood_path'] == DEFAULT_CONFIG['data']['mood_path']
    
    def test_env_override_retry_config(self):
        """Test that environment variables override retry config."""
        with patch.dict(os.environ, {
            'MUSICREC_MAX_RETRIES': '5',
            'MUSICREC_BACKOFF_SECONDS': '2.5'
        }):
            config = load_config()
            
            assert config['retry']['max_attempts'] == 5
            assert config['retry']['backoff_seconds'] == 2.5
    
    def test_env_override_app_config(self):
        """Test that environment variables override app config."""
        with patch.dict(os.environ, {
            'MUSICREC_DEFAULT_PORT': '9000',
            'MUSICREC_DEFAULT_LIMIT': '25'
        }):
            config = load_config()
            
            assert config['app']['default_port'] == 9000
            assert config['app']['default_limit'] == 25
    
    def test_env_override_base_path(self):
        """Test that MUSICREC_DATA_PATH updates all data file paths."""
        with patch.dict(os.environ, {'MUSICREC_DATA_PATH': '/custom/data'}):
            config = load_config()
            
            # All data paths should use the new base directory
            assert config['data']['spotify_path'] == '/custom/data/spotify_songs.csv'
            assert config['data']['genre_path'] == '/custom/data/autotagging_genre.tsv'
            assert config['data']['mood_path'] == '/custom/data/autotagging_moodtheme.tsv'
    
    def test_env_override_invalid_values(self):
        """Test handling of invalid environment variable values."""
        with patch.dict(os.environ, {
            'MUSICREC_MAX_RETRIES': 'not_a_number',
            'MUSICREC_BACKOFF_SECONDS': 'invalid_float'
        }):
            config = load_config()
            
            # Should preserve string values when conversion fails
            assert config['retry']['max_attempts'] == 'not_a_number'
            assert config['retry']['backoff_seconds'] == 'invalid_float'


class TestConfigHelperFunctions:
    """Test configuration helper functions."""
    
    def test_get_data_paths(self):
        """Test get_data_paths function."""
        paths = get_data_paths()
        
        assert isinstance(paths, dict)
        expected_keys = ['spotify_path', 'genre_path', 'mood_path', 'metadata_path', 'processed_data_path']
        for key in expected_keys:
            assert key in paths
    
    def test_get_retry_config(self):
        """Test get_retry_config function."""
        retry_config = get_retry_config()
        
        assert isinstance(retry_config, dict)
        expected_keys = ['max_attempts', 'backoff_seconds', 'backoff_multiplier']
        for key in expected_keys:
            assert key in retry_config
    
    def test_get_app_config(self):
        """Test get_app_config function."""
        app_config = get_app_config()
        
        assert isinstance(app_config, dict)
        expected_keys = ['default_port', 'default_limit']
        for key in expected_keys:
            assert key in app_config
    
    def test_config_functions_with_custom_config(self):
        """Test helper functions with custom config."""
        custom_config = {
            'data': {'spotify_path': 'custom.csv'},
            'retry': {'max_attempts': 10},
            'app': {'default_port': 9000}
        }
        
        data_paths = get_data_paths(custom_config)
        retry_config = get_retry_config(custom_config)
        app_config = get_app_config(custom_config)
        
        assert data_paths['spotify_path'] == 'custom.csv'
        assert retry_config['max_attempts'] == 10
        assert app_config['default_port'] == 9000


class TestPathResolution:
    """Test path resolution functionality."""
    
    def test_resolve_absolute_path(self):
        """Test resolving absolute paths."""
        abs_path = "/absolute/path/to/file.csv"
        resolved = resolve_path(abs_path)
        
        assert resolved == abs_path
    
    def test_resolve_relative_path_no_base(self):
        """Test resolving relative paths without base directory."""
        rel_path = "relative/path/file.csv"
        resolved = resolve_path(rel_path)
        
        expected = str(Path.cwd() / rel_path)
        assert resolved == expected
    
    def test_resolve_relative_path_with_base(self):
        """Test resolving relative paths with base directory."""
        rel_path = "relative/file.csv"
        base_dir = "/custom/base"
        resolved = resolve_path(rel_path, base_dir)
        
        expected = "/custom/base/relative/file.csv"
        assert resolved == expected
    
    def test_resolve_current_directory_path(self):
        """Test resolving current directory references."""
        resolved = resolve_path("./file.csv")
        
        expected = str(Path.cwd() / "file.csv")
        assert resolved == expected


class TestEnvironmentMappings:
    """Test environment variable mappings."""
    
    def test_all_env_mappings_exist(self):
        """Test that all environment mappings are valid."""
        for env_var, config_path in ENV_MAPPINGS.items():
            assert isinstance(env_var, str)
            assert env_var.startswith('MUSICREC_')
            assert isinstance(config_path, str)
            assert '.' in config_path  # Should be nested config path
    
    def test_env_mapping_coverage(self):
        """Test that important config values have environment mappings."""
        important_configs = [
            'data.spotify_path',
            'data.genre_path',
            'retry.max_attempts',
            'app.default_port'
        ]
        
        mapped_configs = set(ENV_MAPPINGS.values())
        for config_path in important_configs:
            assert config_path in mapped_configs, f"Missing environment mapping for {config_path}"