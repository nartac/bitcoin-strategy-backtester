# 🛠️ Database Tools

This directory contains utility tools for inspecting and managing the OHLCV database.

## 📋 Available Tools

### 🔍 **inspect_database.py**
Comprehensive database exploration tool with advanced features.

**Usage:**
```bash
# List all symbols
python tools/inspect_database.py --symbols

# Show data for specific symbol and date
python tools/inspect_database.py --symbol TSLA --date 2025-09-02

# Show data around a date (±3 days)
python tools/inspect_database.py --symbol BTC-USD --date 2025-09-02 --around 3

# Show date range
python tools/inspect_database.py --symbol AAPL --start 2025-08-01 --end 2025-09-01

# Show recent data
python tools/inspect_database.py --symbol ETH-USD --tail --limit 10
```

### ⚡ **quick_db_check.py**
Simple, fast interface for common database queries.

**Usage:**
```bash
# Show available symbols
python tools/quick_db_check.py

# Check specific date
python tools/quick_db_check.py TSLA 2025-09-02

# Quick date shortcuts
python tools/quick_db_check.py BTC-USD today
python tools/quick_db_check.py AAPL yesterday
python tools/quick_db_check.py SPY recent
```

## 🎯 Quick Examples

```bash
# Check what symbols are cached
python tools/quick_db_check.py

# Look at Tesla's data for yesterday
python tools/quick_db_check.py TSLA yesterday

# Explore Bitcoin data around a specific date
python tools/inspect_database.py --symbol BTC-USD --date 2025-09-01 --around 5

# Interactive mode
python tools/inspect_database.py
```

## 📊 Features

- **Smart Date Handling**: Automatically suggests closest dates for weekends/holidays
- **Beautiful Output**: Formatted tables with proper price display
- **Performance Stats**: Shows total records, date ranges, and cache statistics
- **Interactive Mode**: Explore data interactively without command-line arguments
- **Error Handling**: Graceful handling of missing data or invalid symbols

## 🔧 Requirements

All tools automatically handle Python path resolution and require no additional setup beyond the main project dependencies.
