# 📈 Bitcoin Strategy Backtester

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)](https://docs.pytest.org/)

> A comprehensive Python-based tool for backtesting Bitcoin trading strategies using historical data with interactive visualization and performance analytics.

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [Development](#-development)
- [Performance & Limitations](#-performance--limitations)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

## 🚀 Overview

The Bitcoin Strategy Backtester is a powerful, extensible framework designed for quantitative analysis of cryptocurrency trading strategies. Built with Python and modern data science tools, it enables traders, researchers, and developers to rigorously test their trading hypotheses against historical Bitcoin price data.

This tool bridges the gap between theoretical trading strategies and practical implementation by providing a comprehensive backtesting environment. Whether you're a seasoned quantitative analyst developing sophisticated algorithms or a cryptocurrency enthusiast exploring basic trading strategies, this backtester offers the flexibility and precision needed for reliable strategy evaluation.

Key use cases include portfolio optimization, risk assessment, strategy comparison, and educational exploration of cryptocurrency markets. The interactive dashboard makes complex backtesting results accessible through intuitive visualizations, while the extensible architecture allows for custom strategy development and integration with external data sources.

## ✨ Features

- **🎯 Strategy Backtesting**
  - Support for multiple trading strategies (Buy & Hold, Moving Average Crossover, RSI, Bollinger Bands)
  - Customizable parameters and optimization
  - Portfolio rebalancing and position sizing
  - Transaction cost modeling

- **📊 Historical Data Analysis**
  - Real-time data fetching from multiple exchanges
  - OHLCV data processing and validation
  - Multiple timeframe support (1m, 5m, 1h, 1d)
  - Data quality checks and gap filling

- **🎨 Interactive Visualization Dashboard**
  - Real-time strategy performance charts
  - Portfolio value evolution
  - Drawdown analysis and risk metrics
  - Comparative strategy analysis
  - Export capabilities for reports

- **📈 Performance Metrics & Reporting**
  - Comprehensive performance statistics
  - Risk-adjusted returns (Sharpe ratio, Sortino ratio)
  - Maximum drawdown and volatility analysis
  - Trade-by-trade analysis
  - Automated report generation

- **🔧 Extensible Strategy Framework**
  - Plugin architecture for custom strategies
  - Event-driven backtesting engine
  - Signal generation and filtering
  - Risk management integration

## 🛠 Installation

### Prerequisites

- **Python 3.11.9** or higher
- **pip** package manager
- **Git** for version control

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/XaJason/bitcoin-strategy-backtester.git
   cd bitcoin-strategy-backtester
   ```

2. **Create and activate virtual environment**
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
   python -c "import pandas, numpy, streamlit; print('Installation successful!')"
   ```

### Environment Configuration

Create a `.env` file in the project root (optional):
```env
# API Configuration
COINBASE_API_KEY=your_api_key_here
BINANCE_API_KEY=your_api_key_here

# Data Configuration
DEFAULT_TIMEFRAME=1d
DEFAULT_LOOKBACK_DAYS=365

# Backtesting Configuration
DEFAULT_INITIAL_CAPITAL=10000
DEFAULT_COMMISSION=0.001
```

## ⚡ Quick Start

### 1. Basic Strategy Backtesting

```python
from backtester import StrategyBacktester
from strategies import BuyAndHoldStrategy, MovingAverageCrossover

# Initialize backtester
backtester = StrategyBacktester(
    initial_capital=10000,
    start_date='2023-01-01',
    end_date='2024-01-01'
)

# Create and run a simple Buy & Hold strategy
buy_hold = BuyAndHoldStrategy()
results = backtester.run_strategy(buy_hold)

# Print basic results
print(f"Total Return: {results.total_return:.2%}")
print(f"Sharpe Ratio: {results.sharpe_ratio:.3f}")
print(f"Max Drawdown: {results.max_drawdown:.2%}")
```

### 2. Running the Interactive Dashboard

```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` to access the interactive dashboard.

### 3. Custom Strategy Development

```python
from strategies.base import BaseStrategy

class CustomRSIStrategy(BaseStrategy):
    def __init__(self, rsi_period=14, overbought=70, oversold=30):
        super().__init__()
        self.rsi_period = rsi_period
        self.overbought = overbought
        self.oversold = oversold
    
    def generate_signals(self, data):
        rsi = self.calculate_rsi(data['close'], self.rsi_period)
        
        signals = []
        for i in range(len(data)):
            if rsi[i] < self.oversold:
                signals.append('BUY')
            elif rsi[i] > self.overbought:
                signals.append('SELL')
            else:
                signals.append('HOLD')
        
        return signals
```

### 4. Example Output

*[Placeholder for strategy performance chart showing portfolio value over time, drawdown periods, and key metrics]*

*[Placeholder for comparison chart showing multiple strategies performance side-by-side]*

## 📚 Usage

### Data Sources

The backtester supports multiple data sources:

- **Coinbase Pro API** - Real-time and historical OHLCV data
- **Binance API** - Comprehensive cryptocurrency data
- **CSV Import** - Custom data file support
- **Yahoo Finance** - Bitcoin price data (BTC-USD)

```python
from data_sources import CoinbaseDataSource, CSVDataSource

# Using Coinbase data source
coinbase = CoinbaseDataSource()
data = coinbase.get_historical_data('BTC-USD', '2023-01-01', '2024-01-01')

# Using custom CSV data
csv_source = CSVDataSource('path/to/btc_data.csv')
data = csv_source.load_data()
```

### Strategy Configuration

Configure strategies through YAML files or programmatically:

```yaml
# strategies.yaml
moving_average_crossover:
  short_window: 20
  long_window: 50
  
rsi_strategy:
  period: 14
  overbought: 70
  oversold: 30
  
bollinger_bands:
  period: 20
  std_dev: 2
```

### Risk Management

Implement position sizing and risk controls:

```python
from risk_management import PositionSizer, RiskManager

# Position sizing based on volatility
sizer = PositionSizer(method='volatility_target', target_vol=0.15)

# Risk management with stop-loss and take-profit
risk_mgr = RiskManager(
    max_position_size=0.1,  # 10% of portfolio
    stop_loss=0.05,         # 5% stop loss
    take_profit=0.15        # 15% take profit
)
```

### Performance Analysis

Access comprehensive performance metrics:

```python
# Get detailed performance report
report = backtester.get_performance_report()

print(f"Annual Return: {report.annual_return:.2%}")
print(f"Volatility: {report.volatility:.2%}")
print(f"Sharpe Ratio: {report.sharpe_ratio:.3f}")
print(f"Sortino Ratio: {report.sortino_ratio:.3f}")
print(f"Maximum Drawdown: {report.max_drawdown:.2%}")
print(f"Win Rate: {report.win_rate:.2%}")
print(f"Profit Factor: {report.profit_factor:.2f}")
```

## 🏗 Architecture

### System Design

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Strategies    │    │  Risk Manager   │
│                 │    │                 │    │                 │
│ • Coinbase API  │    │ • Buy & Hold    │    │ • Position Size │
│ • Binance API   │────│ • MA Crossover  │────│ • Stop Loss     │
│ • CSV Files     │    │ • RSI Strategy  │    │ • Take Profit   │
│ • Yahoo Finance │    │ • Custom Logic  │    │ • Drawdown Ctrl │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Backtester     │
                    │  Engine         │
                    │                 │
                    │ • Event Loop    │
                    │ • Portfolio Mgmt│
                    │ • Trade Exec    │
                    │ • Metric Calc   │
                    └─────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   Visualization │ │   Performance   │ │    Reporting    │
    │                 │ │    Analytics    │ │                 │
    │ • Streamlit UI  │ │ • Risk Metrics  │ │ • PDF Reports   │
    │ • Plotly Charts │ │ • Drawdown Calc │ │ • CSV Export    │
    │ • Real-time     │ │ • Statistics    │ │ • JSON Results  │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Core Components

- **Data Pipeline**: Handles data ingestion, cleaning, and validation
- **Strategy Engine**: Executes trading logic and signal generation
- **Portfolio Manager**: Manages positions, cash, and rebalancing
- **Risk Manager**: Implements position sizing and risk controls
- **Performance Analyzer**: Calculates metrics and generates reports
- **Visualization Layer**: Creates interactive charts and dashboards

### Data Flow

1. **Data Ingestion**: Historical price data is fetched from configured sources
2. **Data Processing**: OHLCV data is cleaned, validated, and prepared
3. **Strategy Execution**: Trading signals are generated based on strategy logic
4. **Portfolio Updates**: Positions are updated based on signals and risk rules
5. **Performance Calculation**: Metrics are computed in real-time
6. **Visualization**: Results are rendered in interactive dashboard

## 🔧 Development

### Setting Up Development Environment

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

3. **Run code formatting**
   ```bash
   black src/ tests/
   isort src/ tests/
   flake8 src/ tests/
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_strategies.py

# Run tests in parallel
pytest -n auto
```

### Code Style and Standards

- **Code Formatting**: Black with 88-character line length
- **Import Sorting**: isort with Black-compatible settings
- **Linting**: flake8 with custom configuration
- **Type Hints**: Mandatory for all public functions
- **Docstrings**: Google-style docstrings for all classes and functions

### Contributing Guidelines

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality
3. **Ensure code quality** passes all checks
4. **Update documentation** as needed
5. **Submit a pull request** with clear description

```bash
# Example workflow
git checkout -b feature/new-strategy
# Make your changes
pytest
black src/ tests/
git commit -m "Add new momentum strategy"
git push origin feature/new-strategy
```

## ⚡ Performance & Limitations

### System Requirements

- **Minimum**: 4GB RAM, Python 3.11+
- **Recommended**: 8GB+ RAM, SSD storage
- **For large datasets**: 16GB+ RAM, multi-core CPU

### Performance Benchmarks

- **Small dataset** (1 year daily): ~0.1 seconds
- **Medium dataset** (5 years hourly): ~2 seconds  
- **Large dataset** (10 years minute-level): ~30 seconds
- **Concurrent strategies** (10 strategies): ~5 seconds

### Known Limitations

- **Look-ahead bias**: Ensure strategies don't use future data
- **Survivorship bias**: Historical data may not include delisted assets
- **Transaction costs**: Real-world costs may vary from estimates
- **Market impact**: Large orders may have slippage not modeled
- **Data quality**: Gaps or errors in historical data affect results

### Future Improvements

- [ ] Multi-asset portfolio backtesting
- [ ] Options and derivatives support
- [ ] Machine learning strategy framework
- [ ] Real-time paper trading
- [ ] Advanced risk modeling
- [ ] Cloud-based backtesting
- [ ] API for external integrations

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute

- **Report bugs** and request features via GitHub Issues
- **Submit pull requests** for bug fixes and enhancements
- **Improve documentation** and add examples
- **Share trading strategies** and best practices
- **Help with testing** across different environments

### Development Process

1. Check existing issues and discussions
2. Create an issue for major changes
3. Fork the repository
4. Create a feature branch
5. Make changes with tests
6. Submit a pull request

### Issue Reporting

When reporting bugs, please include:
- Python version and operating system
- Complete error traceback
- Minimal reproducible example
- Expected vs actual behavior

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Commercial Use

This software is free for commercial use. If you use this project in your business or research, we'd appreciate attribution but it's not required.

## 🙏 Acknowledgments

### Data Sources
- [Coinbase Pro API](https://docs.pro.coinbase.com/) - Professional cryptocurrency data
- [Binance API](https://binance-docs.github.io/apidocs/) - Comprehensive crypto market data
- [Yahoo Finance](https://finance.yahoo.com/) - Historical price data

### Inspiration and References
- [Zipline](https://github.com/quantopian/zipline) - Algorithmic trading library
- [Backtrader](https://github.com/mementum/backtrader) - Python backtesting library
- [QuantLib](https://www.quantlib.org/) - Quantitative finance framework

### Contributors
Special thanks to all contributors who help improve this project. See [CONTRIBUTORS.md](CONTRIBUTORS.md) for the full list.

---

**Disclaimer**: This software is for educational and research purposes. Cryptocurrency trading involves substantial risk of loss. Past performance does not guarantee future results. Always do your own research and consider your financial situation before trading.

---

⭐ **Star this repository** if you find it useful and follow [@XaJason](https://github.com/XaJason) for updates!