# 🎵 Mood Music Recommender - Enhanced Edition

[![CI/CD Pipeline](https://github.com/angelaqaaa/mood-music-recommender-enhanced/workflows/CI/badge.svg)](https://github.com/angelaqaaa/mood-music-recommender-enhanced/actions)
[![Code Coverage](https://codecov.io/gh/angelaqaaa/mood-music-recommender-enhanced/branch/main/graph/badge.svg)](https://codecov.io/gh/angelaqaaa/mood-music-recommender-enhanced)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Live Demo](https://img.shields.io/badge/demo-coming_soon-orange)](https://github.com/angelaqaaa/mood-music-recommender-enhanced)
[![Tests](https://img.shields.io/badge/tests-196_passing-brightgreen.svg)](https://github.com/angelaqaaa/mood-music-recommender-enhanced)

> **An enterprise-grade music recommendation system that discovers songs based on mood, genre hierarchies, and audio feature similarity. Built with Python, featuring interactive visualizations, WCAG 2.1 AA accessibility compliance, and a modern web interface.**

[**🚀 Live Demo**](https://mood-music-recommender-enhanced.onrender.com)) 

![Main Interface](assets/screenshots/main_interface.png)

## ✨ **Key Features**

### 🔍 **Enterprise Search Engine**
- **Advanced fuzzy matching** with trigram indexing for O(k*m) performance
- **Real-time search suggestions** with debounced input handling
- **Multi-algorithm support** (trigram + difflib) with configurable thresholds
- **LRU caching** for sub-100ms response times

### ♿ **Accessibility Excellence**
- **WCAG 2.1 AA compliant** with full keyboard navigation
- **Screen reader support** with proper ARIA attributes and announcements
- **Reduced motion** and **high contrast** mode support
- **Responsive design** optimized for mobile and desktop

### 🎯 **Intelligent Recommendations**
- **Genre hierarchy traversal** using graph algorithms (BFS/DFS) with user-friendly explanations
- **Enhanced similarity matching** with lowered thresholds and improved audio feature weighting
- **Smart fallback system** ensuring every track gets recommendations via genre/mood matching
- **Mood-based filtering** with explanation generation and neutral similarity handling
- **Interactive visualizations** with helpful tooltips and guidance

### 🏗️ **Professional Architecture**
- **Modular design** with clean separation of concerns
- **Type-safe implementation** with comprehensive type hints
- **196 comprehensive tests** (100% passing) across 18 test files
- **5 CI/CD workflows** with automated quality gates

## 🚀 **Quick Start**

### Prerequisites
- Python 3.9+
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

# Run the application
python src/musicrec/main.py --sample
```

Visit `http://localhost:8040` to explore the application!

## 🆕 **Recent Improvements (v2.1)**

### **Enhanced User Experience**
- **Intuitive explanations** for BFS, DFS, and Direct search methods
- **Helpful tooltips** for visualization features (bubble chart, similarity network)
- **Clear guidance** for search by track functionality
- **Professional styling** with consistent visual hierarchy

### **Improved Recommendation Algorithm**
- **Lowered similarity threshold** from 0.15 to 0.1 for more inclusive matching
- **Optimized feature weighting** (60% audio features, 40% mood) for better similarity
- **Enhanced mood handling** with neutral similarity for tracks without mood tags
- **Increased processing capacity** from 500 to 1000 tracks for better coverage
- **Smart fallback system** ensuring zero "No recommendations found" cases

### Docker Deployment

```bash
# Build the container
docker build -t musicrec-enhanced .

# Run the container
docker run -p 8040:8040 musicrec-enhanced
```

## 📊 **Technical Highlights**

| Feature | Implementation | Status |
|---------|---------------|---------|
| **Search Engine** | Trigram indexing + LRU caching | ✅ Enterprise-grade |
| **Test Coverage** | 196 tests across 18 files | ✅ 100% passing |
| **Code Quality** | Black, isort, flake8, mypy | ✅ All passing |
| **Accessibility** | WCAG 2.1 AA compliance | ✅ Certified |
| **CI/CD** | 5 comprehensive workflows | ✅ Automated |
| **Performance** | Sub-100ms search responses | ✅ Optimized |

## 🎨 **Screenshots**

### Main Interface
![Main Interface](assets/screenshots/main_interface.png)

### Search & Recommendations
![Search Results](assets/screenshots/search_results.png)

### Mobile View
![Mobile Interface](assets/screenshots/mobile_view.png)

## 🎬 **Demo**

![Demo GIF](assets/demo/demo_interaction.gif)

## 🧪 **Development & Testing**

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/musicrec --cov-report=html

# Run specific test categories
pytest tests/test_search_*  # Search functionality
pytest tests/test_accessibility_*  # Accessibility tests
```

### Code Quality
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

### Development Server
```bash
# Run with hot reload (development mode)
python src/musicrec/main.py --sample --debug

# Run with real data files
python src/musicrec/main.py
```

## 🏗️ **Architecture**

```
src/musicrec/
├── config/           # Configuration management
├── data/            # Data processing and loading
├── models/          # Core recommendation algorithms
├── ui/              # Web interface and interactions
│   ├── dash_app.py  # Main Dash application
│   ├── search.py    # Advanced search engine
│   └── styles.py    # Responsive CSS styles
├── utils/           # Utilities and logging
└── metrics/         # Performance monitoring
```

## 📈 **Performance Benchmarks**

- **Dataset Size**: 55,446 tracks with full metadata and audio features
- **Search Response Time**: < 100ms (average)
- **Similarity Connections**: Up to 1000 tracks processed for comprehensive matching
- **Application Startup**: < 5 seconds (sample), ~60 seconds (full dataset)
- **Memory Usage**: < 200MB (sample), ~800MB (full dataset)
- **Test Execution**: 196 tests in ~6 seconds

## 🤝 **Contributing**

This project follows enterprise development practices:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Run tests** (`pytest`) and ensure they pass
4. **Check code quality** (`black`, `isort`, `flake8`, `mypy`)
5. **Commit** with conventional commit format
6. **Push** and create a Pull Request

All contributions are automatically tested via GitHub Actions CI/CD.

## 📜 **Attribution & License**

### **Development History**
- **Original Course Project (v1.0)**: CSC111 Winter 2025 at University of Toronto, developed collaboratively with Mengxuan (Connie) Guo
- **Enhanced Edition (v2.0+)**: All enhancements designed and implemented solely by Qian "Angela" Su after course completion

### **License**
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### **Enhancements Added**
All features beyond the original course project scope are documented in [ENHANCEMENTS.md](ENHANCEMENTS.md), including:
- Enterprise search engine with trigram indexing and optimization
- WCAG 2.1 AA accessibility implementation with keyboard navigation
- Comprehensive test suite (196 tests) and CI/CD automation (5 workflows)
- Enhanced similarity algorithm with smart fallback systems
- Performance monitoring and metrics collection
- Interactive UI explanations and user guidance
- Client-side JavaScript integration and responsive design

## 🔗 **Links**

- [**Live Demo**](https://mood-music-recommender-enhanced.onrender.com)
- [**Changelog**](./CHANGELOG.md)
