# 🤝 Contributing to Mood Music Recommender Enhanced

Thank you for your interest in contributing to the Mood Music Recommender Enhanced project! This guide will help you get started with development and ensure your contributions align with our project standards.

## 📋 **Table of Contents**

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Community Guidelines](#community-guidelines)

---

## 🚀 **Getting Started**

### Prerequisites

Before contributing, ensure you have:

- **Python 3.11+** installed
- **Git** for version control
- **Basic understanding** of Python, web development, and music recommendation systems
- **Familiarity** with testing frameworks (pytest) and code quality tools

### First-Time Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/mood-music-recommender-enhanced.git
   cd mood-music-recommender-enhanced
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/angelaqaaa/mood-music-recommender-enhanced.git
   ```

---

## 🛠️ **Development Setup**

### 1. Environment Configuration

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify installation
python -m src.musicrec.main --sample
```

### 2. Pre-commit Setup (Recommended)

```bash
# Install pre-commit hooks
pre-commit install

# Test pre-commit setup
pre-commit run --all-files
```

### 3. IDE Configuration

#### **VS Code Setup** (Recommended)
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.provider": "isort"
}
```

#### **PyCharm Setup**
- Set Python interpreter to `./venv/bin/python`
- Enable Black as code formatter
- Configure pytest as test runner
- Enable type checking with mypy

---

## 📁 **Project Structure**

Understanding the codebase structure will help you navigate and contribute effectively:

```
mood-music-recommender-enhanced/
├── src/musicrec/                 # Main application package
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py           # Settings and environment handling
│   ├── core/                     # Core recommendation algorithms
│   │   ├── __init__.py
│   │   ├── engine.py             # Main recommendation engine
│   │   └── structures.py         # Data structures (GenreTree, SimilarityGraph)
│   ├── data/                     # Data processing utilities
│   │   ├── __init__.py
│   │   └── processor.py          # Data loading and preprocessing
│   ├── web/                      # Web interface components
│   │   ├── components/           # UI components and styling
│   │   ├── search/               # Search engine implementation
│   │   ├── __init__.py
│   │   └── app.py                # Main Dash web application
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   └── logging.py            # Logging configuration
│   ├── metrics/                  # Performance monitoring
│   │   ├── __init__.py
│   │   └── collector.py          # Metrics collection
│   ├── __init__.py
│   └── main.py                   # Application entry point
├── tests/                        # Test suite (22+ files)
│   ├── test_*.py                 # Unit tests
│   ├── performance/              # Performance benchmarks
│   └── integration/              # Integration tests
├── data/                         # Data files (sample and real)
├── .github/workflows/            # CI/CD automation (6 workflows)
├── requirements*.txt             # Dependency specifications
├── Dockerfile                    # Container configuration
├── pyproject.toml               # Project metadata
└── docs/                        # Documentation files
```

### Key Components to Understand

#### **Core Engine (`src/musicrec/core/engine.py`)**
- Main recommendation logic
- Genre hierarchy traversal
- Similarity calculations

#### **Web Application (`src/musicrec/web/app.py`)**
- Dash-based user interface
- Interactive visualizations
- User interaction handling

#### **Search Engine (`src/musicrec/web/search/engine.py`)**
- Fuzzy string matching
- Trigram indexing
- Performance optimization

---

## 🔄 **Development Workflow**

### 1. Before Starting Work

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Development Process

1. **Write failing tests first** (Test-Driven Development)
2. **Implement the feature** to make tests pass
3. **Run the full test suite** to ensure no regressions
4. **Update documentation** if necessary
5. **Run code quality checks** before committing

### 3. Testing Your Changes

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/musicrec --cov-report=html

# Run specific test categories
pytest tests/test_core_*        # Core functionality
pytest tests/test_web_*         # Web interface
pytest tests/performance/       # Performance tests

# Test the application manually
python -m src.musicrec.main --sample
```

### 4. Code Quality Checks

```bash
# Format code
black src/ tests/

# Organize imports
isort src/ tests/

# Check code style
flake8 src/ tests/

# Type checking
mypy src/

# Run all quality checks
pre-commit run --all-files
```

---

## 📝 **Code Standards**

### Python Code Style

We follow **PEP 8** with additional standards enforced by our tools:

#### **Formatting (Black)**
```python
# Good: Black-compliant formatting
def recommend_tracks(
    self, genre: str, mood: Optional[str] = None, limit: int = 10
) -> List[Track]:
    """Return track recommendations based on genre and mood."""
    pass
```

#### **Import Organization (isort)**
```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import pandas as pd
from dash import html

# Local imports
from musicrec.core.structures import GenreTree
from musicrec.utils.logging import get_logger
```

#### **Type Hints (mypy)**
```python
# Good: Comprehensive type hints
from typing import Dict, List, Optional, Union

class RecommendationEngine:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.tracks: List[MusicNode] = []

    def recommend(self, query: str, limit: int = 10) -> List[MusicNode]:
        """Return recommendations with proper type annotations."""
        return self.search_engine.search(query, limit)
```

### Documentation Standards

#### **Docstring Format**
```python
def calculate_similarity(self, track1: MusicNode, track2: MusicNode) -> float:
    """
    Calculate similarity between two music tracks.

    Args:
        track1: First track for comparison
        track2: Second track for comparison

    Returns:
        Similarity score between 0.0 and 1.0

    Raises:
        ValueError: If tracks have incompatible feature sets

    Example:
        >>> engine = RecommendationEngine()
        >>> similarity = engine.calculate_similarity(track_a, track_b)
        >>> print(f"Similarity: {similarity:.2f}")
    """
    pass
```

#### **Code Comments**
```python
# Good: Explain why, not what
def optimize_similarity_calculation(self, tracks: List[MusicNode]) -> None:
    # Skip expensive calculations in production to ensure fast startup
    if self._is_production_environment() and len(tracks) > 100:
        return self._use_fallback_algorithm(tracks)
```

---

## 🧪 **Testing Guidelines**

### Test Structure

Our testing philosophy emphasizes:
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **Performance Tests**: Benchmark critical operations

#### **Unit Test Example**
```python
# tests/test_core_engine.py
import pytest
from musicrec.core.engine import RecommendationEngine
from musicrec.core.structures import MusicNode

class TestRecommendationEngine:
    def test_bfs_recommendation_returns_diverse_results(self):
        """Test that BFS provides diverse genre exploration."""
        engine = RecommendationEngine()
        results = engine.recommend_by_genre_bfs("rock", limit=10)

        # Assert diverse subgenres are represented
        genres = {track.primary_genre for track in results}
        assert len(genres) > 1, "BFS should return diverse genres"

    def test_similarity_calculation_symmetry(self):
        """Test that similarity calculation is symmetric."""
        engine = RecommendationEngine()
        track1 = MusicNode("track1", "Test Track 1")
        track2 = MusicNode("track2", "Test Track 2")

        sim1 = engine.calculate_similarity(track1, track2)
        sim2 = engine.calculate_similarity(track2, track1)

        assert abs(sim1 - sim2) < 0.001, "Similarity should be symmetric"
```

#### **Integration Test Example**
```python
# tests/test_integration_web_search.py
def test_end_to_end_search_recommendation_flow(self):
    """Test complete user workflow from search to recommendations."""
    app = MusicRecommenderDashApp()

    # Simulate user search
    search_results = app.handle_search_input("jazz")
    assert len(search_results) > 0

    # Simulate recommendation request
    recommendations = app.get_recommendations("jazz", "relaxed")
    assert len(recommendations) > 0
    assert all(track.mood_tags for track in recommendations)
```

### Test Data Management

```python
# Use fixtures for consistent test data
@pytest.fixture
def sample_tracks():
    """Provide sample tracks for testing."""
    return [
        MusicNode("1", "Test Jazz Track", primary_genre="jazz"),
        MusicNode("2", "Test Rock Track", primary_genre="rock"),
    ]

def test_genre_filtering(sample_tracks):
    """Test genre-based filtering functionality."""
    engine = RecommendationEngine(sample_tracks)
    jazz_tracks = engine.filter_by_genre("jazz")
    assert len(jazz_tracks) == 1
    assert jazz_tracks[0].primary_genre == "jazz"
```

### Performance Testing

```python
# tests/performance/test_search_performance.py
import time
import pytest

def test_search_response_time():
    """Ensure search responses are under 100ms."""
    engine = AdvancedFuzzySearchEngine()

    start_time = time.time()
    results = engine.search("test query", limit=10)
    end_time = time.time()

    response_time = (end_time - start_time) * 1000  # Convert to ms
    assert response_time < 100, f"Search took {response_time:.2f}ms (should be < 100ms)"
```

---

## 📤 **Submitting Changes**

### 1. Commit Message Format

Use **Conventional Commits** format:

```bash
# Format: <type>[optional scope]: <description>
# Examples:
feat(search): add fuzzy matching with trigram indexing
fix(ui): resolve dark mode toggle persistence issue
docs(readme): update installation instructions
test(core): add similarity calculation edge cases
perf(engine): optimize recommendation algorithm for large datasets
```

**Commit Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `ci`: CI/CD changes

### 2. Pull Request Process

#### **Before Submitting**
```bash
# Ensure all checks pass
pytest                          # All tests pass
black --check src/ tests/       # Code formatting
isort --check src/ tests/       # Import organization
flake8 src/ tests/              # Linting
mypy src/                       # Type checking

# Update documentation if needed
# Ensure commit messages follow conventions
```

#### **PR Description Template**
```markdown
## 🎯 **Change Description**

Brief summary of what this PR accomplishes.

## 🔧 **Technical Details**

- Specific technical changes made
- Algorithms or approaches used
- Performance considerations

## 🧪 **Testing**

- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed
- [ ] Performance impact assessed

## 📚 **Documentation**

- [ ] Code comments added/updated
- [ ] README updated if needed
- [ ] CHANGELOG entry added

## ✅ **Checklist**

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] No debugging code left behind
- [ ] Breaking changes documented

## 📸 **Screenshots** (if applicable)

Include before/after screenshots for UI changes.
```

### 3. Review Process

- **Automated Checks**: All CI/CD workflows must pass
- **Code Review**: At least one maintainer review required
- **Testing**: Comprehensive test coverage for new features
- **Documentation**: Updates to relevant documentation

---

## 👥 **Community Guidelines**

### Code of Conduct

We are committed to providing a welcoming and inclusive experience for everyone. Please:

- **Be respectful** in all interactions
- **Provide constructive feedback** during code reviews
- **Ask questions** if anything is unclear
- **Help others** learn and grow

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Comments**: For specific implementation questions

### Recognition

Contributors are recognized through:
- **Contributor acknowledgments** in release notes
- **GitHub contributor graphs** and statistics
- **Meaningful commit history** that showcases contributions

---

## 🎯 **Contribution Ideas**

### Good First Issues

- Add new music genre support
- Improve error messages and user feedback
- Add new visualization types
- Enhance accessibility features
- Write additional tests

### Advanced Contributions

- Performance optimizations
- New recommendation algorithms
- Advanced search features
- Deployment improvements
- Security enhancements

### Documentation Contributions

- Tutorial creation
- API documentation
- Code examples
- Translation support

---

## 📞 **Contact**

For questions about contributing:

- **GitHub Issues**: Technical questions and bug reports
- **Email**: For private inquiries
- **GitHub Discussions**: Community discussions and ideas

Thank you for contributing to making music discovery better for everyone! 🎵

---

*This contributing guide ensures high-quality contributions while maintaining a welcoming environment for developers of all skill levels.*