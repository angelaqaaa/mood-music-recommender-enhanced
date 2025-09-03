# 🎵 Mood Music Recommender — Enhanced Edition

<div align="center">

[![CI](https://github.com/angelaqaaa/mood-music-recommender-enhanced/actions/workflows/ci.yml/badge.svg)](https://github.com/angelaqaaa/mood-music-recommender-enhanced/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*An intelligent music recommendation system that understands your mood and discovers music through advanced graph algorithms and machine learning.*

[🚀 Quick Start](#quick-start) • [📊 Features](#features) • [🏗️ Architecture](#architecture) • [📖 Documentation](#documentation)

</div>

---

## 🎯 Overview

The **Mood Music Recommender** is a sophisticated recommendation engine that combines genre hierarchies, similarity graphs, and mood-based filtering to deliver personalized music discoveries. Built with modern software engineering practices, this system demonstrates advanced data structures, machine learning integration, and production-ready architecture.

### 🌟 Key Highlights

- **🧠 Intelligent Recommendations**: Genre-based, mood-driven, and similarity-based algorithms
- **📊 Interactive Visualizations**: Real-time network graphs and audio feature analysis
- **🏗️ Production Architecture**: Clean separation of concerns, dependency injection, comprehensive testing
- **⚡ High Performance**: Optimized graph algorithms with caching and retry logic
- **🔧 Developer Experience**: Type hints, structured logging, CI/CD pipeline

---

## 📊 Features

### Core Recommendation Algorithms
- **Genre Hierarchy Navigation**: Tree-based exploration with BFS/DFS search strategies
- **Similarity Matching**: Cosine similarity on audio features (energy, valence, tempo)
- **Mood-Based Filtering**: Multi-tag mood classification with weighted recommendations
- **Hybrid Approach**: Combines multiple algorithms for diverse, accurate results

### Interactive Web Interface
- **Real-time Recommendations**: Live updates based on user preferences
- **Visualization Dashboard**: Network graphs showing track relationships
- **Audio Feature Analysis**: Bubble charts mapping valence vs energy
- **Search & Discovery**: Full-text search across tracks, artists, and genres

### Production-Ready Features
- **Configuration Management**: JSON config files with environment variable overrides
- **Structured Logging**: Configurable levels with file and console output
- **Error Handling**: Comprehensive input validation and graceful failure recovery
- **Testing**: 147+ test cases with integration, unit, and performance tests
- **CI/CD Pipeline**: Automated testing across Python 3.10-3.12 with security scanning

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/angelaqaaa/mood-music-recommender-enhanced.git
cd mood-music-recommender-enhanced

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### Running the Application

```bash
# Launch web interface with sample data
python run_app.py --sample

# Launch on custom port
python run_app.py --sample --port 8050

# CLI mode for batch processing
python run_app.py --demo --sample

# Process and save data for later use
python run_app.py --save processed_data.pkl
```

The web interface will be available at `http://localhost:8040` (or your specified port).

### Sample Usage

```python
from src.musicrec.main import create_sample_data, MusicRecommender

# Generate sample dataset
data = create_sample_data(num_genres=5, tracks_per_genre=20)

# Initialize recommender
recommender = MusicRecommender(data)

# Get genre-based recommendations
rock_tracks = recommender.recommend_by_genre("rock", limit=5)

# Get mood-based recommendations
happy_tracks = recommender.recommend_by_mood("happy", limit=5)

# Find similar tracks
similar = recommender.recommend_similar_to_track("track_1", limit=3)
```

---

## 🏗️ Architecture

### Project Structure
```
src/musicrec/
├── __init__.py
├── main.py                 # Application entry point
├── recommendation_engine.py # Core recommendation logic
├── music_structures.py     # Data structures (GenreTree, SimilarityGraph)
├── data_processor.py       # Data loading and processing
├── visualization.py        # Dash web application
├── log_setup.py           # Structured logging configuration
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration management
├── ui/
│   └── __init__.py         # Web interface components
└── data/
    └── __init__.py         # Data loading utilities

tests/                      # Comprehensive test suite (147+ tests)
├── test_*.py              # Unit tests for all modules
├── test_integration_*.py  # End-to-end integration tests
└── conftest.py            # Pytest fixtures and configuration

.github/workflows/          # CI/CD pipeline
└── ci.yml                 # Multi-Python testing with security scanning
```

### Core Components

#### 🌲 GenreTree
Hierarchical organization of music genres with parent-child relationships, enabling:
- Efficient genre-based search and filtering
- Breadth-first and depth-first traversal algorithms
- Mood tag indexing and retrieval

#### 🕸️ SimilaritySongGraph
Graph-based representation of track relationships using:
- Cosine similarity on audio features
- Mood-based similarity weighting
- Configurable similarity thresholds
- Optimized neighbor search

#### 🎯 MusicRecommender
Central recommendation engine providing:
- Multiple recommendation strategies
- Configurable audio features
- Performance monitoring and metrics
- Scalable architecture for large datasets

---

## 📖 Documentation

### API Reference

#### MusicRecommender Class

```python
class MusicRecommender:
    """Core recommendation engine for mood-driven music discovery."""
    
    def recommend_by_genre(self, genre: str, limit: int = 10) -> List[Dict]:
        """Get tracks by genre with optional mood filtering."""
    
    def recommend_by_mood(self, mood: str, limit: int = 10) -> List[Dict]:
        """Find tracks matching specific mood tags."""
    
    def recommend_similar_to_track(self, track_id: str, limit: int = 5) -> List[Dict]:
        """Discover tracks similar to a given track."""
    
    def bfs_recommend(self, genre: str, mood: str = None, max_depth: int = 2) -> List[Dict]:
        """Breadth-first search through genre hierarchy."""
    
    def dfs_recommend(self, genre: str, mood: str = None, max_breadth: int = 5) -> List[Dict]:
        """Depth-first exploration of genre relationships."""
```

### Configuration

The system supports flexible configuration through JSON files and environment variables:

```json
{
  "data": {
    "spotify_path": "data/spotify_songs.csv",
    "genre_path": "data/autotagging_genre.tsv"
  },
  "retry": {
    "max_attempts": 3,
    "backoff_seconds": 1.0
  },
  "app": {
    "default_port": 8040,
    "default_limit": 10
  }
}
```

Environment variables (prefix `MUSICREC_`):
- `MUSICREC_DATA_PATH`: Override data directory
- `MUSICREC_MAX_RETRIES`: Set retry attempts for I/O operations
- `MUSICREC_LOG_LEVEL`: Configure logging verbosity

---

## 🧪 Development

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test categories
pytest tests/test_recommendation_engine.py  # Unit tests
pytest tests/test_integration_cli.py        # Integration tests

# Generate coverage report
pytest --cov=src/musicrec --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Type checking
mypy src/musicrec/

# Linting
flake8 src/ tests/

# Run all quality checks (as in CI)
black --check src/ tests/ && flake8 src/ tests/ && mypy src/musicrec/
```

### Performance Benchmarks

The system includes performance tests for key operations:
- Recommendation generation: <2 seconds for 200 tracks
- Similarity graph construction: <10 seconds for 200 tracks
- Memory usage: Optimized for datasets up to 10,000 tracks

---

## 🤝 Attribution & Development History

### Original Course Project (v1.0)
**CSC111 Winter 2025** at the University of Toronto  
Developed collaboratively with **Mengxuan (Connie) Guo**

**Original Features:**
- Basic genre hierarchy tree structure
- Similarity-based recommendations using audio features
- Simple Dash web interface for recommendations
- Core data structures and algorithms

### Post-Course Enhancements (v1.1+)
**Enhanced by Qian "Angela" Su** after course completion

**Key Improvements:**
- ✅ **Professional package structure** with proper separation of concerns
- ✅ **Comprehensive testing suite** with 147+ tests and CI/CD pipeline
- ✅ **Configuration management** with JSON config and environment variables
- ✅ **Structured logging** with configurable levels and multiple outputs
- ✅ **Input validation & error handling** with retry logic and graceful failures
- ✅ **Type hints throughout** codebase for better maintainability
- ✅ **Performance optimizations** with caching and algorithm improvements
- ✅ **Security scanning** with bandit and dependency vulnerability checks

See [`ENHANCEMENTS.md`](ENHANCEMENTS.md) for detailed enhancement roadmap and [`CHANGELOG.md`](CHANGELOG.md) for version history.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Repository**: [GitHub](https://github.com/angelaqaaa/mood-music-recommender-enhanced)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/angelaqaaa/mood-music-recommender-enhanced/issues)
- **CI/CD**: [GitHub Actions](https://github.com/angelaqaaa/mood-music-recommender-enhanced/actions)

---

<div align="center">

**Built with ❤️ using Python, NetworkX, scikit-learn, and Plotly Dash**

*Transforming music discovery through intelligent algorithms and beautiful visualizations*

</div>