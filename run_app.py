#!/usr/bin/env python3
"""Entry point for running the music recommender application."""

import sys
from pathlib import Path

# Add src to Python path so we can import the package
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from musicrec.main import main

if __name__ == "__main__":
    main()