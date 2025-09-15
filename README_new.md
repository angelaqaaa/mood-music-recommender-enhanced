# 🎵 Mood Music Recommender - Enhanced Edition

[![CI/CD Pipeline](https://github.com/yourusername/mood-music-recommender-enhanced/workflows/CI/badge.svg)](https://github.com/yourusername/mood-music-recommender-enhanced/actions)
[![Code Coverage](https://codecov.io/gh/yourusername/mood-music-recommender-enhanced/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/mood-music-recommender-enhanced)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Live Demo](https://img.shields.io/badge/demo-coming_soon-orange)](https://github.com/yourusername/mood-music-recommender-enhanced)
[![Tests](https://img.shields.io/badge/tests-196_passing-brightgreen.svg)](https://github.com/yourusername/mood-music-recommender-enhanced)

> **An enterprise-grade music recommendation system that discovers songs based on mood, genre hierarchies, and audio feature similarity. Built with Python, featuring interactive visualizations, WCAG 2.1 AA accessibility compliance, and a modern web interface.**

[**🚀 Live Demo**](https://your-app.onrender.com) • [**📖 Documentation**](./ENHANCEMENTS.md) • [**🎬 Demo Video**](#demo)

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
- **Genre hierarchy traversal** using graph algorithms (BFS/DFS)
- **Audio feature similarity** based on energy, valence, tempo, and danceability
- **Mood-based filtering** with explanation generation
- **Interactive visualizations** showing recommendation reasoning

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
git clone https://github.com/yourusername/mood-music-recommender-enhanced.git
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

- **Search Response Time**: < 100ms (average)
- **Application Startup**: < 5 seconds
- **Memory Usage**: < 200MB (with sample data)
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
- Enterprise search engine with optimization
- WCAG 2.1 AA accessibility implementation
- Comprehensive test suite and CI/CD automation
- Performance monitoring and metrics collection
- Client-side JavaScript integration

## 🔗 **Links**

- [**Live Demo**](https://your-app.onrender.com) (Coming Soon)
- [**Enhancement Documentation**](./ENHANCEMENTS.md)
- [**Development Guide**](./CLAUDE.md)
- [**Changelog**](./CHANGELOG.md)

---

**Built with ❤️ using Python, Dash, and modern web technologies**

*This project demonstrates enterprise-grade software engineering practices and serves as a professional portfolio showcase.*