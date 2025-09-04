# 📈 Bitcoin Strategy Backtester

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](https://docs.pytest.org/)

> A professional Python-based financial chart generator and data analysis tool for cryptocurrency and stock market visualization. Generate publication-ready charts with technical indicators, volume analysis, and intelligent data caching.

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Chart Types & Indicators](#-chart-types--indicators)
- [Technical Architecture](#-technical-architecture)
- [Examples](#-examples)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Overview

The Bitcoin Strategy Backtester is a powerful financial chart generation and data analysis tool built for traders, analysts, and developers. It provides professional-grade charting capabilities with real-time data fetching, intelligent caching, and comprehensive technical analysis features.

**What it does:**
- Generates professional financial charts for any Yahoo Finance symbol (BTC-USD, AAPL, TSLA, etc.)
- Provides multiple chart styles: candlestick, OHLC, line, and area charts
- Calculates and displays technical indicators with proper statistical validity
- Offers interactive CLI interface for rapid chart generation
- Manages data efficiently with SQLite caching and automatic expiry

**Target Users:**
- Financial analysts creating presentations and reports
- Cryptocurrency traders analyzing market trends  
- Python developers building financial applications
- Researchers studying market behavior and technical analysis

## ✨ Features

### 📊 Professional Chart Generation
- **Multiple Chart Styles**: Candlestick, OHLC bars, line charts, and area charts
- **Comprehensive Timeframes**: 5D, 1M, 3M, 6M, YTD, 1Y, 5Y, and MAX (all available data)
- **Technical Indicators**: Moving averages (MA50, MA200) with proper lookback calculations
- **Volume Analysis**: Subplot and overlay volume visualization with up/down coloring
- **Scaling Options**: Linear and logarithmic price scales

### 🔄 Intelligent Data Management
- **Real-time Data**: Fetches live market data from Yahoo Finance
- **SQLite Caching**: Local database storage for improved performance
- **Cache Expiry System**: Automatic data refresh with configurable expiry (1-24 hours)
- **Gap Filling**: Smart handling of weekend and holiday data gaps
- **Data Validation**: Comprehensive OHLCV data quality checks

### 🖥️ Interactive CLI Interface
- **Command-line Interface**: Simple, powerful chart generation commands
- **Interactive Mode**: Step-by-step chart creation with guided prompts
- **Cache Management**: Built-in commands for cache status, refresh, and cleanup
- **Chart History**: Automatic saving and organization of generated charts
- **Export Options**: High-resolution PNG output for presentations

### 🏗️ Professional Architecture
- **Modular Design**: Clean separation of data, visualization, and interface layers
- **Extensible Framework**: Easy integration of new indicators and chart types
- **Memory Efficient**: Optimized data handling for large datasets
- **Error Handling**: Robust error recovery and user feedback
- **Test Coverage**: Comprehensive test suite with pytest

## 🛠 Installation

### Prerequisites
- **Python 3.11** or higher
- **pip** package manager
- **Git** for cloning the repository

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/XaJason/bitcoin-strategy-backtester.git
   cd bitcoin-strategy-backtester
   ```

2. **Create virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python chart_explorer.py --help
   ```

## 🚀 Quick Start

### Generate Your First Chart
```bash
# Bitcoin 1-year candlestick chart with moving averages
python chart_explorer.py BTC-USD --timeframe 1Y --style candlestick --indicators BOTH --volume subplot

# Apple stock 6-month chart with MA50
python chart_explorer.py AAPL --timeframe 6M --style candlestick --indicators MA50

# Tesla 5-year line chart with logarithmic scale  
python chart_explorer.py TSLA --timeframe 5Y --style line --scale log
```

### Interactive Mode
```bash
python chart_explorer.py
# Follow the prompts to create custom charts
```

### Cache Management
```bash
# Check cache status
python chart_explorer.py --cache-status

# Refresh all cached data
python chart_explorer.py --cache-refresh

# View cache statistics
python chart_explorer.py --cache-info
```

## 📈 Chart Types & Indicators

### Supported Chart Styles
- **Candlestick**: Professional OHLC candlestick charts with customizable colors
- **OHLC**: Traditional open-high-low-close bar charts
- **Line**: Clean line charts using closing prices
- **Area**: Filled area charts for trend visualization

### Technical Indicators (Currently Implemented)
- **MA50**: 50-period Simple Moving Average
- **MA200**: 200-period Simple Moving Average  
- **BOTH**: Display both MA50 and MA200 simultaneously
- **Proper Lookback**: Indicators calculated with sufficient historical data for statistical validity

### Volume Analysis
- **Subplot**: Volume displayed in separate chart below price data
- **Overlay**: Volume overlaid on price chart with transparency
- **Up/Down Coloring**: Green for up days, red for down days

### Supported Symbols
Any Yahoo Finance symbol including:
- **Cryptocurrencies**: BTC-USD, ETH-USD, ADA-USD, DOT-USD
- **US Stocks**: AAPL, TSLA, GOOGL, MSFT, AMZN
- **Indices**: ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ)
- **Forex**: EURUSD=X, GBPUSD=X, USDJPY=X

## 🏗️ Technical Architecture

### Core Components
```
bitcoin-strategy-backtester/
├── chart_explorer.py          # Main CLI interface
├── src/
│   ├── data/
│   │   ├── database.py        # SQLite OHLCV database
│   │   ├── cache_manager.py   # Intelligent caching system
│   │   └── fetcher.py         # Yahoo Finance data fetcher
│   ├── visualization/
│   │   ├── chart_engine.py    # Core plotting engine
│   │   ├── indicators.py      # Technical indicator calculations
│   │   ├── styles.py          # Chart styling and themes
│   │   └── formatters.py      # Axis formatting and labels
│   └── utils/
│       └── config.py          # Configuration management
├── examples/                  # Sample charts and demos
├── tests/                     # Comprehensive test suite
└── tools/                     # Database utilities
```

### Technology Stack
- **Data Processing**: pandas, numpy for efficient data manipulation
- **Visualization**: matplotlib, mplfinance for professional chart rendering
- **Data Source**: yfinance for real-time market data
- **Database**: SQLite for local data caching
- **Testing**: pytest for comprehensive test coverage
- **CLI**: argparse for command-line interface

### Performance Characteristics
- **Data Fetching**: ~1-2 seconds for real-time data
- **Chart Generation**: ~2-3 seconds for complex charts with indicators
- **Cache Hit**: <0.5 seconds for cached data retrieval  
- **Memory Usage**: ~50-200MB depending on data timeframe
- **Storage**: ~1-5MB per cached symbol dataset

## 📸 Examples

### Command Examples with Outputs

```bash
# Professional Bitcoin analysis chart
python chart_explorer.py BTC-USD --timeframe 1Y --style candlestick --indicators BOTH --volume subplot
# Output: chart_BTC-USD_1Y_candlestick_[timestamp].png

# Apple stock quarterly analysis
python chart_explorer.py AAPL --timeframe 3M --style candlestick --indicators MA50 --volume overlay
# Output: chart_AAPL_3M_candlestick_[timestamp].png

# Tesla long-term trend analysis
python chart_explorer.py TSLA --timeframe 5Y --style line --scale log --indicators MA200
# Output: chart_TSLA_5Y_line_[timestamp].png
```

### Available Chart Examples
The `examples/charts/` directory contains sample outputs including:
- Multi-timeframe analysis (5D to MAX)
- Various chart styles (candlestick, line, area, OHLC)
- Technical indicator combinations
- Volume visualization options
- Linear vs logarithmic scaling examples

### Use Cases
- **Portfolio Presentations**: Generate professional charts for client meetings
- **Technical Analysis**: Analyze trends with proper moving average calculations
- **Market Research**: Compare multiple symbols across different timeframes
- **Educational Content**: Create charts for trading education and tutorials

## 🔧 Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test modules
pytest tests/test_chart_engine.py -v
```

### Code Quality
```bash
# Format code
black src/ tests/

# Check code style
flake8 src/ tests/
```

### Adding New Features
1. **New Indicators**: Add methods to `TechnicalIndicators` class in `indicators.py`
2. **Chart Styles**: Extend chart plotting methods in `chart_engine.py`  
3. **Data Sources**: Implement new fetcher classes following the `YahooFetcher` pattern

## 🤝 Contributing

This project welcomes contributions! Current areas for enhancement:

### Contribution Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-indicator`)
3. Add tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install black flake8 pytest-cov

# Run pre-commit checks
python -m pytest
python -m black --check src/ tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the financial analysis community**

*Generate professional charts • Analyze market trends • Make data-driven decisions*
