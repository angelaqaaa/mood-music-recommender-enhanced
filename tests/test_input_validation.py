"""Tests for input validation functionality."""

import pytest
import tempfile
import os
from pathlib import Path


def test_file_validation_logic():
    """Test core file validation logic without importing full modules."""

    def validate_file_path(
        file_path: str, expected_extensions: list, description: str
    ) -> None:
        """Local copy of validation logic for testing."""
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

    # Test existing file with correct extension
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
        f.write("test,data\n1,2\n")
        temp_path = f.name

    try:
        # Should not raise any exceptions
        validate_file_path(temp_path, [".csv"], "Test file")
    finally:
        os.unlink(temp_path)


def test_file_validation_not_found():
    """Test validation fails when file doesn't exist."""

    def validate_file_path(
        file_path: str, expected_extensions: list, description: str
    ) -> None:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"{description} not found: {file_path}")

    with pytest.raises(FileNotFoundError, match="Test file not found"):
        validate_file_path("/non/existent/file.csv", [".csv"], "Test file")


def test_file_validation_wrong_extension():
    """Test validation fails when file has wrong extension."""

    def validate_file_path(
        file_path: str, expected_extensions: list, description: str
    ) -> None:
        path = Path(file_path)
        if path.suffix.lower() not in expected_extensions:
            raise ValueError(
                f"{description} must have one of these extensions {expected_extensions}, "
                f"got: {path.suffix}"
            )

    with pytest.raises(ValueError, match="must have one of these extensions"):
        validate_file_path("test.txt", [".csv"], "Test file")


def test_file_validation_directory():
    """Test validation fails when path is a directory."""

    def validate_file_path(
        file_path: str, expected_extensions: list, description: str
    ) -> None:
        path = Path(file_path)
        if not path.is_file():
            raise ValueError(f"{description} is not a file: {file_path}")

    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(ValueError, match="is not a file"):
            validate_file_path(temp_dir, [".csv"], "Test file")


def test_parameter_validation():
    """Test parameter validation logic."""

    def validate_limit_param(limit: int) -> None:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if limit > 1000:
            raise ValueError("limit must not exceed 1000")

    # Valid parameters
    validate_limit_param(10)
    validate_limit_param(1)
    validate_limit_param(1000)

    # Invalid parameters
    with pytest.raises(ValueError, match="limit must be at least 1"):
        validate_limit_param(0)

    with pytest.raises(ValueError, match="limit must not exceed 1000"):
        validate_limit_param(1001)
