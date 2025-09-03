# 📊 Chart Visualization System

The Bitcoin Strategy Backtester now includes a comprehensive matplotlib-based charting system for professional financial data visualization.

## 🎯 Quick Start

```python
from src.visualization import OHLCVChart

# Basic usage - 1 year Bitcoin line chart
chart = OHLCVChart(symbol='BTC-USD')
chart.plot().save('bitcoin_chart.png')

# Advanced usage - Tesla candlestick with indicators and volume
chart = OHLCVChart(symbol='TSLA')
chart.plot(
    timeframe='6M',
    style='candlestick',
    indicators='BOTH',  # 50-day and 200-day MA
    volume='subplot'
).save('tesla_advanced.png')
```

## 📈 Features

### **Timeframes**
- `'5D'` - 5 days
- `'1M'` - 1 month  
- `'3M'` - 3 months
- `'6M'` - 6 months
- `'YTD'` - Year-to-date
- `'1Y'` - 1 year (default)
- `'5Y'` - 5 years
- `'MAX'` - All available data

### **Chart Styles**
- `'line'` - Line chart (default)
- `'area'` - Filled area chart
- `'candlestick'` - Japanese candlestick
- `'ohlc'` - Traditional OHLC bars

### **Price Scales**
- `'linear'` - Linear scale (default)
- `'log'` - Logarithmic scale

### **Technical Indicators**
- `'MA50'` - 50-day moving average
- `'MA200'` - 200-day moving average
- `'BOTH'` - Both moving averages
- `None` - No indicators (default)

### **Volume Display**
- `False` - No volume (default)
- `'subplot'` - Volume in separate subplot
- `'overlay'` - Semi-transparent volume overlay

## 🎨 Chart Examples

### Line Chart with Moving Averages
```python
chart = OHLCVChart(symbol='AAPL')
chart.plot(
    timeframe='1Y',
    style='line',
    indicators='BOTH'
).save('apple_ma.png')
```

### Candlestick with Volume
```python
chart = OHLCVChart(symbol='BTC-USD')
chart.plot(
    timeframe='3M',
    style='candlestick',
    volume='subplot'
).save('bitcoin_candlestick.png')
```

### Logarithmic Scale for Long-term Analysis
```python
chart = OHLCVChart(symbol='BTC-USD')
chart.plot(
    timeframe='MAX',
    scale='log',
    indicators='MA200'
).save('bitcoin_longterm_log.png')
```

## 🛠️ Advanced Usage

### Custom Database Connection
```python
from src.data.database import OHLCVDatabase

# Use custom database
db = OHLCVDatabase('path/to/custom.db')
chart = OHLCVChart(db, 'SYMBOL')
```

### Method Chaining
```python
# Chain multiple operations
chart = OHLCVChart(symbol='TSLA')
result = (chart
    .plot(timeframe='6M', style='candlestick', indicators='MA50')
    .save('tesla_6m.png'))
```

### Multiple Export Formats
```python
chart = OHLCVChart(symbol='AAPL')
chart.plot(timeframe='1Y', indicators='BOTH')

# Save in different formats
chart.save('apple.png', dpi=300)           # High-res PNG
chart.save('apple.pdf', format='pdf')      # PDF
chart.save('apple.svg', format='svg')      # Scalable SVG
```

## 📊 Supported Symbols

The system works with any symbol available in your database:
- **Cryptocurrencies**: BTC-USD, ETH-USD, DOGE-USD
- **Stocks**: AAPL, TSLA, SPY, MSFT, GOOGL
- **ETFs**: SPY, QQQ, VTI

## 🎯 Professional Features

### **Intelligent Axis Formatting**
- Automatic date formatting based on timeframe
- Smart price formatting (currency vs. regular numbers)
- Volume scaling with K/M/B suffixes

### **Financial Industry Standards**
- Professional color scheme
- Clean grid lines and styling
- Proper candlestick colors (green/red)
- Volume bars with up/down coloring

### **Performance Optimizations**
- Automatic memory management
- Efficient data querying
- Figure cleanup after save/show

## 🧪 Testing

Run the comprehensive chart examples:
```bash
python examples/chart_examples.py
```

Run quick functionality test:
```bash
python examples/quick_chart_test.py
```

## 📁 Output

Charts are saved to `examples/charts/` directory with descriptive filenames:
- `BTC-USD_line_1y.png` - Basic line chart
- `TSLA_candlestick_ma.png` - Candlestick with moving averages
- `AAPL_indicators_BOTH.png` - Chart with technical indicators

## 🔧 Troubleshooting

### Memory Warnings
If you see "More than 20 figures" warning, use:
```python
chart.plot().save('file.png')  # Automatically cleans up
# OR
chart.close()  # Manual cleanup
```

### Missing Data
If no data is available, the system will attempt to fetch it automatically using the integrated `YahooFetcher`.

### Display Issues
For headless environments, always use `save()` instead of `show()`.

## 🎨 Customization

The charting system uses a professional color palette and styling that can be customized through the `ChartStyler` class in `src/visualization/styles.py`.

---

🎉 **The charting system is now fully integrated and ready for professional financial analysis!**
