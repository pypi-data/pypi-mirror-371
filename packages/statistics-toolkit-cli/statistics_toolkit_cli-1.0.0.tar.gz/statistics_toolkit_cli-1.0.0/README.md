# Statistics Toolkit CLI 📊

> A comprehensive command-line statistics learning and analysis tool with step-by-step explanations

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/connorodea/statistics-toolkit-cli)](https://github.com/connorodea/statistics-toolkit-cli/issues)

## 🎯 Overview

Transform your terminal into a comprehensive statistics education platform! This toolkit provides step-by-step explanations for statistical concepts, making it perfect for students, educators, and anyone who wants to understand the "why" behind statistical calculations.

## ✨ Features

- **📈 Descriptive Statistics**: Mean, median, mode, variance, standard deviation, five-number summary, outlier detection
- **🧪 Hypothesis Testing**: One-sample and two-sample t-tests with complete explanations
- **📊 Data Visualization**: Histograms, box plots, scatter plots with statistical overlays
- **💾 Data Management**: CSV import/export, save/load datasets
- **🎓 Educational Focus**: Every calculation shows mathematical steps and reasoning
- **🖥️ Interactive CLI**: User-friendly menu-driven interface

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/connorodea/statistics-toolkit-cli.git
cd statistics-toolkit-cli

# Install dependencies
pip install -r requirements.txt

# Run the toolkit
python stats_cli.py
```

### One-Line Setup

```bash
curl -sSL https://raw.githubusercontent.com/connorodea/statistics-toolkit-cli/main/setup_stats_toolkit.sh | bash
```

## 📖 Usage Examples

### Interactive Menu
```bash
python stats_cli.py
```

### Sample Data Demo
```bash
python stats_cli.py --demo
```

### Quick Analysis
```
Enter values: 85 92 78 88 95 82 79 91 87 84

=== MEASURES OF CENTER ===
Sample size: n = 10
MEAN CALCULATION:
x̄ = Σx/n = 861/10 = 86.1000

MEDIAN CALCULATION:
Sorted data: [78 79 82 84 85 87 88 91 92 95]
n is even: median = (85 + 87)/2 = 86.0000
```

## 🎓 Educational Philosophy

This toolkit is designed for **learning statistics**, not just computing answers. Every calculation shows:

- 📝 **The formula being used**
- 🔢 **Step-by-step substitution of values**  
- 📊 **Intermediate calculations**
- 💡 **Interpretation of results**
- ✅ **Assumption checking**

## 📁 Project Structure

```
statistics-toolkit-cli/
├── stats_cli.py              # Main application
├── requirements.txt          # Python dependencies
├── setup.py                  # Package installation
├── Makefile                  # Development commands
├── examples/
│   ├── data/                 # Sample CSV datasets
│   └── create_sample_data.py # Generate sample data
├── tests/
│   └── test_basic.py         # Unit tests
└── docs/                     # Documentation
```

## 🛠️ Development

### Setup Development Environment
```bash
# Clone and setup
git clone https://github.com/connorodea/statistics-toolkit-cli.git
cd statistics-toolkit-cli

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install as editable package
pip install -e .
```

### Available Commands
```bash
make run          # Run the CLI tool
make demo         # Run sample data demo
make test         # Run tests
make sample-data  # Generate sample datasets
make clean        # Clean build artifacts
make help         # Show all commands
```

### Running Tests
```bash
python -m pytest tests/ -v
# or
make test
```

## 📊 Sample Datasets

The toolkit includes sample datasets for practice:

- **`test_scores.csv`** - Student academic performance data
- **`sales_data.csv`** - Business sales and advertising data  
- **`study_vs_scores.csv`** - Study time vs exam performance

Generate fresh sample data:
```bash
make sample-data
```

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run tests**: `make test`
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to the branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Include tests for new features
- Update README if adding major features
- Maintain the educational focus of explanations

## 🐛 Issues & Support

- **Bug Reports**: [Create an issue](https://github.com/connorodea/statistics-toolkit-cli/issues/new?template=bug_report.md)
- **Feature Requests**: [Create an issue](https://github.com/connorodea/statistics-toolkit-cli/issues/new?template=feature_request.md)
- **Questions**: [Start a discussion](https://github.com/connorodea/statistics-toolkit-cli/discussions)

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [User Manual](docs/user_manual.md)
- [Developer Guide](docs/developer_guide.md)
- [API Reference](docs/api_reference.md)

## 🏆 Inspiration

Originally inspired by TI-84 calculator programs, this toolkit brings the same step-by-step educational approach to modern Python development, making statistics accessible and understandable for everyone.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for statistics education and learning
- Inspired by the need for transparent statistical calculations
- Designed to complement traditional statistics textbooks and courses

---

**Made with ❤️ for statistics education**

[![GitHub stars](https://img.shields.io/github/stars/connorodea/statistics-toolkit-cli?style=social)](https://github.com/connorodea/statistics-toolkit-cli/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/connorodea/statistics-toolkit-cli?style=social)](https://github.com/connorodea/statistics-toolkit-cli/network/members)

## 📦 PyPI Package Installation

Once published to PyPI, install with:

```bash
pip install statistics-toolkit-cli
```

Then use anywhere:
```bash
statstoolkit
# or  
stats-cli
```

## 🏗️ Building the Package

```bash
# Build for PyPI
make build

# Test locally
python -m statistics_toolkit_cli.cli --demo

# Check package
make package-info
```

## 🚀 Publishing to PyPI

```bash
# Publish to Test PyPI first
bash scripts/publish_to_pypi.sh  # Choose option 1

# Test installation
pip install --index-url https://test.pypi.org/simple/ statistics-toolkit-cli

# Then publish to real PyPI
bash scripts/publish_to_pypi.sh  # Choose option 2
```
