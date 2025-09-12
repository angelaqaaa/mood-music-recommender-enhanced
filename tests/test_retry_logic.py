"""Tests for retry logic and enhanced load_data functionality."""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, call, patch

import pandas as pd
import pytest

from src.musicrec.main import _retry_operation, load_data


class TestRetryOperation:
    """Test the retry operation utility function."""

    def test_retry_success_first_attempt(self):
        """Test successful operation on first attempt."""
        mock_operation = Mock(return_value="success")

        result = _retry_operation(
            mock_operation,
            "arg1",
            "arg2",
            max_attempts=3,
            backoff_seconds=0.1,
            operation_name="test_op",
            kwarg1="value1",
        )

        assert result == "success"
        mock_operation.assert_called_once_with("arg1", "arg2", kwarg1="value1")

    def test_retry_success_second_attempt(self):
        """Test successful operation on second attempt."""
        mock_operation = Mock()
        mock_operation.side_effect = [Exception("First failure"), "success"]

        with patch("time.sleep") as mock_sleep:
            result = _retry_operation(
                mock_operation,
                max_attempts=3,
                backoff_seconds=0.1,
                backoff_multiplier=2.0,
                operation_name="test_op",
            )

        assert result == "success"
        assert mock_operation.call_count == 2
        mock_sleep.assert_called_once_with(0.1)

    def test_retry_all_attempts_fail(self):
        """Test that exception is raised when all attempts fail."""
        mock_operation = Mock()
        mock_operation.side_effect = [
            Exception("Attempt 1"),
            Exception("Attempt 2"),
            Exception("Attempt 3"),
        ]

        with patch("time.sleep") as mock_sleep:
            with pytest.raises(Exception, match="Attempt 3"):
                _retry_operation(
                    mock_operation,
                    max_attempts=3,
                    backoff_seconds=0.1,
                    backoff_multiplier=2.0,
                    operation_name="test_op",
                )

        assert mock_operation.call_count == 3
        # Should have 2 sleeps (after first and second failures)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_has_calls([call(0.1), call(0.2)])

    def test_retry_exponential_backoff(self):
        """Test that exponential backoff works correctly."""
        mock_operation = Mock()
        mock_operation.side_effect = [
            Exception("Fail 1"),
            Exception("Fail 2"),
            Exception("Fail 3"),
            "success",
        ]

        with patch("time.sleep") as mock_sleep:
            result = _retry_operation(
                mock_operation,
                max_attempts=4,
                backoff_seconds=1.0,
                backoff_multiplier=2.0,
                operation_name="test_op",
            )

        assert result == "success"
        assert mock_operation.call_count == 4
        # Backoff: 1.0, 2.0, 4.0
        mock_sleep.assert_has_calls([call(1.0), call(2.0), call(4.0)])

    def test_retry_with_different_exceptions(self):
        """Test retry with different types of exceptions."""
        mock_operation = Mock()
        mock_operation.side_effect = [
            FileNotFoundError("File not found"),
            PermissionError("Permission denied"),
            "success",
        ]

        with patch("time.sleep"):
            result = _retry_operation(
                mock_operation,
                max_attempts=3,
                backoff_seconds=0.1,
                operation_name="test_op",
            )

        assert result == "success"
        assert mock_operation.call_count == 3

    def test_retry_single_attempt(self):
        """Test retry with max_attempts=1."""
        mock_operation = Mock()
        mock_operation.side_effect = Exception("Single failure")

        with pytest.raises(Exception, match="Single failure"):
            _retry_operation(mock_operation, max_attempts=1, operation_name="test_op")

        assert mock_operation.call_count == 1


class TestEnhancedLoadData:
    """Test the enhanced load_data function with configuration and retry logic."""

    def test_load_data_sample_mode(self):
        """Test load_data in sample mode."""
        df = load_data(use_sample=True)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) > 0

    def test_load_data_with_config_defaults(self):
        """Test load_data uses config defaults when no paths provided."""
        with patch("src.musicrec.main.build_dataset") as mock_build:
            mock_build.return_value = pd.DataFrame({"test": [1, 2, 3]})

            # Mock the validation to avoid actual file access
            with patch("src.musicrec.main._validate_file_path") as mock_validate:
                mock_validate.side_effect = FileNotFoundError("No files")

                # Should fall back to sample data when no valid files
                df = load_data()
                assert isinstance(df, pd.DataFrame)

    def test_load_data_with_explicit_paths(self):
        """Test load_data with explicitly provided paths."""
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as spotify_file:
            spotify_path = spotify_file.name
            spotify_file.write(b"test,data\n1,2\n")

        try:
            with patch("src.musicrec.main.build_dataset") as mock_build:
                mock_build.return_value = pd.DataFrame({"test": [1, 2, 3]})

                df = load_data(spotify_path=spotify_path)

                assert isinstance(df, pd.DataFrame)
                mock_build.assert_called_once()

                # Check that the spotify path was passed to build_dataset
                call_args = mock_build.call_args[0]
                assert (
                    call_args[0] == spotify_path
                )  # First argument should be spotify path
        finally:
            os.unlink(spotify_path)

    def test_load_data_file_validation_retry(self):
        """Test that file validation is retried on failure."""

        # Create a more controlled test by only providing spotify path
        # and disabling other paths
        custom_config = {
            "data": {
                "spotify_path": None,  # Will use explicit path
                "genre_path": None,
                "mood_path": None,
                "metadata_path": None,
            },
            "retry": {
                "max_attempts": 3,
                "backoff_seconds": 0.1,
                "backoff_multiplier": 2.0,
            },
        }

        with patch("src.musicrec.main.load_config") as mock_load_config:
            mock_load_config.return_value = custom_config

            with patch("src.musicrec.main._validate_file_path") as mock_validate:
                # First two calls fail, third succeeds
                mock_validate.side_effect = [
                    PermissionError("Temp permission error"),
                    PermissionError("Another temp error"),
                    None,  # Success
                ]

                with patch("src.musicrec.main.build_dataset") as mock_build:
                    mock_build.return_value = pd.DataFrame({"test": [1, 2, 3]})

                    with patch("time.sleep"):  # Mock sleep to speed up test
                        df = load_data(spotify_path="test.csv")

                    assert isinstance(df, pd.DataFrame)
                    assert (
                        mock_validate.call_count == 3
                    )  # Should have retried exactly 3 times

    def test_load_data_build_dataset_retry(self):
        """Test that build_dataset operation is retried on failure."""
        # Create a temporary file that passes validation
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as spotify_file:
            spotify_path = spotify_file.name
            spotify_file.write(b"test,data\n1,2\n")

        try:
            with patch("src.musicrec.main.build_dataset") as mock_build:
                # First two calls fail, third succeeds
                mock_build.side_effect = [
                    Exception("Database connection error"),
                    Exception("Another temp error"),
                    pd.DataFrame({"test": [1, 2, 3]}),
                ]

                with patch("time.sleep"):  # Mock sleep to speed up test
                    df = load_data(spotify_path=spotify_path)

                assert isinstance(df, pd.DataFrame)
                assert mock_build.call_count == 3  # Should have retried
        finally:
            os.unlink(spotify_path)

    def test_load_data_retry_exhausted_fallback_to_sample(self):
        """Test fallback to sample data when all retries are exhausted."""
        with patch("src.musicrec.main._validate_file_path") as mock_validate:
            mock_validate.side_effect = FileNotFoundError("File not found")

            with patch("time.sleep"):  # Mock sleep to speed up test
                df = load_data(spotify_path="nonexistent.csv")

            # Should fall back to sample data
            assert isinstance(df, pd.DataFrame)
            assert not df.empty

    def test_load_data_sample_generation_failure(self):
        """Test behavior when both data loading and sample generation fail."""
        with patch("src.musicrec.main._validate_file_path") as mock_validate:
            mock_validate.side_effect = FileNotFoundError("File not found")

            with patch("src.musicrec.main.create_sample_data") as mock_sample:
                mock_sample.side_effect = Exception("Sample generation failed")

                with pytest.raises(
                    RuntimeError, match="Both data loading and sample generation failed"
                ):
                    load_data(spotify_path="nonexistent.csv")

    def test_load_data_custom_retry_config(self):
        """Test that custom retry configuration is respected."""
        # Create custom config with different retry settings
        custom_config = {
            "data": {"spotify_path": "test.csv"},
            "retry": {
                "max_attempts": 2,
                "backoff_seconds": 0.05,
                "backoff_multiplier": 3.0,
            },
        }

        with patch("src.musicrec.main.load_config") as mock_load_config:
            mock_load_config.return_value = custom_config

            with patch("src.musicrec.main._validate_file_path") as mock_validate:
                mock_validate.side_effect = [
                    PermissionError("Error 1"),
                    PermissionError("Error 2"),  # Should fail after 2 attempts
                ]

                with patch("time.sleep") as mock_sleep:
                    df = load_data()  # Should fall back to sample

                # Verify custom retry config was used
                assert mock_validate.call_count == 2  # Only 2 attempts
                mock_sleep.assert_called_once_with(0.05)  # Custom backoff

    def test_load_data_environment_variable_paths(self):
        """Test that environment variables override config paths."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as env_file:
            env_path = env_file.name
            env_file.write(b"env,data\n1,2\n")

        try:
            with patch.dict(os.environ, {"MUSICREC_SPOTIFY_PATH": env_path}):
                with patch("src.musicrec.main.build_dataset") as mock_build:
                    mock_build.return_value = pd.DataFrame({"env_test": [1, 2, 3]})

                    df = load_data()

                    assert isinstance(df, pd.DataFrame)
                    mock_build.assert_called_once()

                    # Verify the environment path was used
                    call_args = mock_build.call_args[0]
                    assert call_args[0] == env_path
        finally:
            os.unlink(env_path)

    def test_load_data_missing_required_files(self):
        """Test behavior when required files are missing."""
        # Only provide non-required files
        with tempfile.NamedTemporaryFile(suffix=".tsv", delete=False) as genre_file:
            genre_path = genre_file.name
            genre_file.write(b"genre\tdata\nrock\ttest\n")

        try:
            # No spotify file (required), only genre file
            df = load_data(genre_path=genre_path)

            # Should fall back to sample data
            assert isinstance(df, pd.DataFrame)
            assert not df.empty
        finally:
            os.unlink(genre_path)

    def test_load_data_partial_file_success(self):
        """Test successful loading with only some files available."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as spotify_file:
            spotify_path = spotify_file.name
            spotify_file.write(b"test,data\n1,2\n")

        try:
            with patch("src.musicrec.main.build_dataset") as mock_build:
                mock_build.return_value = pd.DataFrame({"partial": [1, 2, 3]})

                # Provide spotify (required) but invalid genre path
                df = load_data(
                    spotify_path=spotify_path, genre_path="/nonexistent/genre.tsv"
                )

                assert isinstance(df, pd.DataFrame)
                mock_build.assert_called_once()

                # Should be called with spotify path and None for invalid files
                call_args = mock_build.call_args[0]
                assert call_args[0] == spotify_path  # spotify
                assert call_args[1] is None  # genre (invalid)
        finally:
            os.unlink(spotify_path)
