"""Tests for logging configuration."""

import logging
import tempfile
from pathlib import Path

from src.musicrec.utils.logging import setup_logging


class TestLogging:
    """Test suite for logging setup."""

    def test_setup_logging_console_only(self):
        """Test setting up console logging."""
        setup_logging(level="INFO")

        logger = logging.getLogger("musicrec")
        assert logger.level <= logging.INFO

    def test_setup_logging_with_file(self):
        """Test setting up logging with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_logging(level="DEBUG", log_file=str(log_file))

            logger = logging.getLogger("musicrec")
            logger.info("Test message")

            assert log_file.exists()
            assert log_file.read_text().strip() != ""

    def test_setup_logging_invalid_level(self):
        """Test that invalid log levels default to INFO."""
        setup_logging(level="INVALID")

        logger = logging.getLogger("musicrec")
        # Should default to INFO level
        assert logger.level <= logging.INFO
