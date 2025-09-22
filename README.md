# 🎵 Mood Music Recommender - Enhanced Edition

[![CI/CD Pipeline](https://github.com/angelaqaaa/mood-music-recommender-enhanced/workflows/CI/badge.svg)](https://github.com/angelaqaaa/mood-music-recommender-enhanced/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-15_files-brightgreen.svg)](https://github.com/angelaqaaa/mood-music-recommender-enhanced)
[![Features](https://img.shields.io/badge/features-user_interactive-purple.svg)](./FEATURES.md)

> **An enterprise-grade music recommendation system that discovers songs based on mood, genre hierarchies, and audio feature similarity. Built with Python, featuring interactive visualizations, modern web interface, and production-ready deployment.**

## ✨ **Key Features**

### 🎯 **Intelligent Recommendations**
- **Genre hierarchy traversal** using graph algorithms (BFS/DFS/Direct search)
- **Enhanced similarity matching** with audio feature analysis and mood-based filtering
- **Smart fallback system** ensuring comprehensive recommendations
- **Interactive visualizations** with network graphs and bubble charts

### 🔍 **Advanced Search Engine**
- **Fuzzy matching** with trigram indexing for fast performance
- **Real-time search suggestions** with debounced input handling
- **Multi-algorithm support** with configurable thresholds
- **LRU caching** for optimized response times

### 🎨 **Modern Web Interface**
- **Dark/Light mode** with user preference persistence
- **Responsive design** optimized for desktop and mobile
- **Interactive visualizations** with Plotly and NetworkX
- **Professional UI** with gradient styling and animations

### 🏗️ **Enterprise Architecture**
- **Clean modular architecture** with separation of concerns and dependency injection
- **Type-safe Python implementation** with comprehensive type hints and validation
- **Extensive test coverage** spanning unit, integration, performance, and accessibility tests
- **Full CI/CD pipeline** with automated testing, code quality checks, and multi-platform deployment

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
pip install -r requirements-dev.txt  # For development

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
- **Docker**: Universal containerized deployment

## 🎬 **Usage Examples**

### Basic Usage
```bash
# Run with sample data (recommended for first time)
python -m src.musicrec.main --sample

# Run with real data files (if available)
python -m src.musicrec.main

# Run on custom port
python -m src.musicrec.main --port 8050

# Save processed data
python -m src.musicrec.main --save processed_data.pkl
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
│   ├── search/      # Advanced search engine
│   ├── static/js/   # JavaScript assets
│   └── app.py       # Main Dash application
├── utils/           # Utilities and logging
├── metrics/         # Performance monitoring
└── main.py          # Application entry point
```

### Core Components

- **`core/engine.py`**: Main recommendation engine with genre hierarchy and similarity algorithms
- **`core/structures.py`**: Data structures for genre trees and similarity graphs
- **`web/app.py`**: Interactive Dash web application with modern UI
- **`web/search/engine.py`**: Advanced fuzzy search with trigram indexing
- **`config/settings.py`**: Configuration management with environment overrides
- **`data/processor.py`**: Data loading and processing pipeline

## 📈 **Performance & Quality**

### Technical Metrics
- **Dataset Capacity**: 55,446+ tracks with full metadata and audio features
- **Search Performance**: Sub-100ms response times with LRU caching
- **Startup Time**: < 5 seconds (sample), optimized for production deployment
- **Memory Usage**: ~200MB (sample), ~800MB (full dataset)

### Code Quality
- **Testing**: 15 test files covering core functionality, search, and integration
- **Code Formatting**: Black, isort for consistent styling
- **Type Checking**: MyPy for type safety
- **Linting**: Flake8 for code quality
- **CI/CD**: 6 automated workflows for quality gates

## 🧪 **Development & Testing**

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/musicrec --cov-report=html

# Run specific test categories
pytest tests/test_*core*        # Core functionality
pytest tests/performance/       # Performance tests
pytest tests/test_*integration* # Integration tests
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

The application supports various configuration options via environment variables or the `config/settings.json` file:

- **MUSICREC_ENV**: Set to "production" for optimized deployment
- **PORT**: Custom port (default: 8040)
- **LOG_LEVEL**: Logging verbosity (INFO, DEBUG, etc.)

## 🤝 **Contributing**

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Steps
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Run tests** and ensure code quality (`pytest`, `black`, `flake8`, `mypy`)
4. **Commit** with conventional commit format
5. **Push** and create a Pull Request

All contributions are automatically tested via GitHub Actions CI/CD.

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
All features beyond the original course scope are documented in [FEATURES.md](FEATURES.md), including:
- 🎨 Modern web interface with dark/light mode toggle
- 🔍 Enterprise-grade search engine with trigram indexing
- ⚡ Production deployment optimizations
- 🧪 Comprehensive testing infrastructure (15 test files)
- 🔄 CI/CD automation with 6 GitHub Actions workflows
- 📊 Performance monitoring and metrics collection
- 🎯 Enhanced recommendation algorithms with smart fallbacks

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 **Links**

- [**Features Documentation**](./FEATURES.md) - Detailed feature overview
- [**Contributing Guide**](./CONTRIBUTING.md) - Development guidelines
- [**Changelog**](CHANGELOG.md) - Version history and updates
