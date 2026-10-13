# 🎵 Mood Music Recommender - Enhanced Edition

[![CI/CD Pipeline](https://github.com/angelaqaaa/mood-music-recommender-enhanced/workflows/CI/badge.svg)](https://github.com/angelaqaaa/mood-music-recommender-enhanced/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-231_passing-brightgreen.svg)](https://github.com/angelaqaaa/mood-music-recommender-enhanced)
[![Features](https://img.shields.io/badge/features-user_interactive-purple.svg)](./docs/FEATURES.md)

> **A music recommendation system that discovers songs based on mood and genre hierarchies. Built with Python and Dash, with interactive visualizations and a Docker deployment on Render.**
> 
<img width="1470" height="956" alt="Screenshot 2025-09-22 at 8 15 55 AM" src="https://github.com/user-attachments/assets/c42c3fe9-694f-4a8a-8715-485f7913b1b2" />

<img width="1470" height="473" alt="image" src="https://github.com/user-attachments/assets/24da46fe-70eb-42c5-adf0-039c698e6fd2" />


## ✨ **Key Features**

### 🎯 **Recommendations**
- **Genre hierarchy traversal** using graph algorithms (BFS/DFS/Direct search)
- **Similarity graph** that scores track pairs by mood-tag overlap and audio-feature cosine similarity; it covers at most 1,000 tracks, production mode skips it for catalogs over 100 tracks, and the audio features, with the mood tags inferred from them, are placeholders (see Catalog below)
- **Fallback recommendations**: when a track has no similarity edges, Find Similar recommends tracks from its genre, then from its mood
- **Interactive visualizations** with network graphs and bubble charts

### 🔍 **Search Engine**
- **Fuzzy matching** in the search engine, over a trigram index
- **Search-as-you-type** in the track dropdown; from three characters on, the options come from the search engine
- **Multi-algorithm support** with configurable thresholds
- **LRU cache** (128 entries) on the fuzzy phase's similarity scores

### 🎨 **Web Interface**
- **Dark/Light mode** toggle
- **Responsive design** for desktop and mobile
- **Interactive visualizations** with Plotly and NetworkX
- **Styling** with gradients and animations

### 🏗️ **Architecture**
- **Modular architecture** with separation of concerns and dependency injection
- **Python implementation** with type hints and input validation
- **Test suite** spanning unit, integration, feature, performance, and accessibility tests
- **CI on GitHub Actions** for tests and code quality checks, plus deployment configuration for Docker, Render, and Railway

## 🚀 **Quick Start**

### Prerequisites
- Python 3.10+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/angelaqaaa/mood-music-recommender-enhanced.git
cd mood-music-recommender-enhanced

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development (optional)
pip install -r requirements-dev.txt

# Run the application with sample data
python -m src.musicrec.main --sample
```

Visit `http://localhost:8040` to explore the application!

### Docker Deployment

```bash
# Build the container
docker build -t musicrec-enhanced .

# Run the container
docker run -p 8040:8040 musicrec-enhanced
```

### Cloud Deployment

The project includes configuration for multiple cloud platforms:

- **Railway**: Deploy using `railway.json` configuration
- **Render**: Deploy using `render.yaml` configuration
- **Docker**: Containerized deployment from the `Dockerfile`

The app is live on Render at <https://mood-music-recommender-enhanced.onrender.com/>. The Render configuration (`render.yaml`, free plan) runs the full 55,446-track catalog: the `Dockerfile` copies `data/` and starts without `--sample`, and `MUSICREC_ENV=production` skips the similarity graph at startup, so Find Similar uses the genre and mood fallbacks.

## 🎬 **Usage Examples**

### Basic Usage
```bash
# Run with sample data (recommended for first time)
python -m src.musicrec.main --sample

# Run with real data files (if available)
python -m src.musicrec.main

# Run on custom port
python -m src.musicrec.main --port 8050

# Save the processed catalog as CSV
python -m src.musicrec.main --save processed_data.csv
```

### Development Mode
```bash
# Run in demo mode (command line interface)
python -m src.musicrec.main --demo --sample
```

## 📊 **Technical Architecture**

```
src/musicrec/
├── config/           # Configuration management
├── core/            # Recommendation algorithms and data structures
├── data/            # Data processing and loading utilities
├── web/             # Web interface and components
│   ├── components/  # UI components and styles
│   ├── search/      # Search engine
│   ├── static/js/   # search.js (not loaded by the app)
│   └── app.py       # Main Dash application
├── utils/           # Utilities and logging
├── metrics/         # Performance monitoring
├── benchmark.py     # Full-catalog search benchmark
└── main.py          # Application entry point
```

### Core Components

- **`core/engine.py`**: Main recommendation engine with genre hierarchy and similarity algorithms
- **`core/structures.py`**: Data structures for genre trees and similarity graphs
- **`web/app.py`**: Interactive Dash web application
- **`web/search/engine.py`**: Two-phase search: an exact index, then trigram fuzzy matching
- **`config/settings.py`**: Configuration management with environment overrides
- **`data/processor.py`**: Data loading and processing pipeline

## 📈 **Performance & Quality**

### Technical Metrics
- **Catalog**: 55,446 Jamendo tracks in the search index, the union of `autotagging_genre.tsv` and `autotagging_moodtheme.tsv`, with track and artist names from `raw_meta_data.tsv`. The audio-feature columns, and the playlist-genre fallback for tracks without a genre tag, come from `spotify_songs.csv` (32,833 rows) but are not matched by track: `merge_datasets` (`src/musicrec/data/processor.py`) assigns Spotify rows to Jamendo tracks by unseeded random draws with replacement, so these values are not the tracks' own. `preprocess_merged_data` then infers mood tags (happy, sad, chill and the like) from the drawn valence and energy and adds them to each track's Jamendo mood tags, so the inferred tags are not the tracks' own either, and a track with no Jamendo mood tag has only inferred ones, if any
- **Search Performance**: 200 ms budget asserted in the performance tests, with an LRU cache on the fuzzy path
- **Measured Search Time**: on the full catalog on 2026-10-13 (8-core Apple M2, Python 3.13.1), first run of each query: exact-name queries p50 7.3 ms and p95 16.7 ms, misspelled queries p50 10.8 ms and p95 16.2 ms, from `benchmarks/results/2026-10-13-search-full-catalog.json` produced by `python -m src.musicrec.benchmark`; method and full table in [docs/demo/performance_benchmarks.md](docs/demo/performance_benchmarks.md)

### Code Quality
- **Testing**: 231 tests across 17 test files with 58% line coverage of `src/musicrec` (88% on `core/engine.py`, 89% on `core/structures.py`)
- **Test Success Rate**: 100% (231/231 passing)
- **Code Formatting**: Black, isort for consistent styling
- **Type Checking**: mypy runs in CI on `src/`, but the `pyproject.toml` override sets `ignore_errors` for those modules, so it does not fail a push
- **Linting**: Flake8 for code quality
- **CI/CD**: Every push to main runs lint and format checks (black, isort, flake8), the full test suite on four Python versions with a 200 ms search-performance budget, an app-boot smoke test, and branch coverage reported to Codecov

## 🧪 **Development & Testing**

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/musicrec --cov-report=html

# Run specific test categories
pytest tests/unit/              # Core functionality
pytest tests/performance/       # Performance tests
pytest tests/integration/       # Integration tests
pytest tests/accessibility/     # Accessibility tests
```

### Code Quality Tools
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## 🔧 **Configuration**

Settings come from environment variables, read in `config/settings.py` and `core/structures.py`, and from command-line flags:

- **MUSICREC_ENV**: `production`, or a non-empty `RENDER` variable, skips the similarity graph for catalogs over 100 tracks
- **MUSICREC_DATA_PATH** (a directory for the default file names), **MUSICREC_SPOTIFY_PATH**, **MUSICREC_GENRE_PATH**, **MUSICREC_MOOD_PATH**, **MUSICREC_METADATA_PATH**: data file locations; the `--spotify`, `--genre`, `--mood` and `--metadata` flags take precedence
- **MUSICREC_MAX_ATTEMPTS**, **MUSICREC_BACKOFF_SECONDS**: attempts and first backoff for the startup check that each data file exists and is readable
- **--port**: port for the web app (default: 8040)
- **--log-level**: logging verbosity, one of DEBUG, INFO, WARNING, ERROR (default: INFO)

## 💼 **About This Project**

This is a personal portfolio project showcasing full-stack development, testing, and DevOps skills. The codebase is available under the MIT License - feel free to explore, learn from it, or fork it for your own use!

### Questions or Feedback?
If you have questions about the implementation or find any issues, please feel free to open an issue on GitHub. While this is a personal project, constructive feedback is always appreciated.

## 📜 **Project History & Attribution**

### Development History
- **Original Course Project (v1.0)**: CSC111 Winter 2025 at University of Toronto
  - Collaborative development with Mengxuan (Connie) Guo
  - Basic recommendation algorithms and data structures

- **Enhanced Edition (v2.0+)**: Post-course enhancements by Qian "Angela" Su
  - Modern web interface with dark mode and responsive design
  - Advanced search engine with fuzzy matching and caching
  - Production deployment optimizations and CI/CD automation
  - Comprehensive testing suite and code quality tools

### Key Enhancements Added
Features beyond the original course scope are described in [FEATURES.md](docs/FEATURES.md), including:
- 🎨 Web interface with a dark/light mode toggle
- 🔍 Search engine with trigram indexing
- ⚡ Production mode that skips the similarity graph at startup
- 🧪 Testing infrastructure (231 tests across 17 files)
- 🔄 CI/CD automation on every push to main: lint and format checks (black, isort, flake8), the full test suite on four Python versions with a 200 ms search-performance budget, an app-boot smoke test, and branch coverage reported to Codecov
- 📊 Performance monitoring and metrics collection
- 🎯 Find Similar falls back to the track's genre, then its mood, when the track has no similarity edges

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 **Links**

- [**Features Documentation**](./docs/FEATURES.md) - Detailed feature overview
- [**Changelog**](CHANGELOG.md) - Version history and updates
