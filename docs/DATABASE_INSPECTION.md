# 🔍 Database Inspection Tools

This project includes powerful tools to visually inspect and explore the SQLite database containing OHLCV (Open, High, Low, Close, Volume) data.

## 🛠️ Available Tools

### 1. **Database Inspector** (`inspect_database.py`)
Comprehensive tool for detailed database exploration.

### 2. **Quick Database Checker** (`quick_db_check.py`)  
Simple, fast interface for common queries.

## 📊 Usage Examples

### **List All Symbols**
```bash
python inspect_database.py --symbols
```
Shows all symbols in the database with record counts and date ranges.

### **Check Specific Symbol and Date**
```bash
# Check TSLA data for a specific date
python inspect_database.py --symbol TSLA --date 2025-09-02

# Using quick checker
python quick_db_check.py TSLA 2025-09-02
```

### **Show Recent Data**
```bash
# Show last 10 records for TSLA
python inspect_database.py --symbol TSLA --tail --limit 10

# Quick way
python quick_db_check.py TSLA recent
```

### **Date Range Queries**
```bash
# Show data for a date range
python inspect_database.py --symbol BTC-USD --start 2025-08-01 --end 2025-09-01

# Show data around a specific date (±3 days)
python inspect_database.py --symbol TSLA --date 2025-09-02 --around 3
```

### **Quick Date Shortcuts**
```bash
python quick_db_check.py BTC-USD today
python quick_db_check.py AAPL yesterday  
python quick_db_check.py SPY recent
```

## 📈 Sample Output

### **Symbol List**
```
📊 SYMBOLS IN DATABASE
==================================================
| Symbol   | Type   | Records | Date Range               |
+==========+========+=========+==========================+
| AAPL     | stock  |     251 | 2024-09-03 to 2025-09-03|
| BTC-USD  | crypto |   4,005 | 2014-09-17 to 2025-09-03|
| TSLA     | stock  |     251 | 2024-09-03 to 2025-09-03|
+----------+--------+---------+--------------------------+
```

### **Specific Date Data**
```
📅 DATA FOR TSLA ON 2025-09-02
==================================================
✅ Data found for 2025-09-02:
   💰 Open:      $  328.23
   📈 High:      $  333.33  
   📉 Low:       $  325.60
   💼 Close:     $  329.36
   📊 Volume:    58,225,400
   
📊 DAILY STATISTICS:
   📈 Daily Change: $  1.13 ( +0.34%)
   📏 Daily Range:  $  7.73 (  2.36%)
```

### **Data Table View**
```
🔍 LAST 5 RECORDS:
+------------+-----------+-----------+-----------+-----------+
| Date       | Open      | High      | Low       | Close     |
+============+===========+===========+===========+===========+
| 2025-08-29 | $  347.23 | $  348.75 | $  331.70 | $  333.87 |
| 2025-09-02 | $  328.23 | $  333.33 | $  325.60 | $  329.36 |
| 2025-09-03 | $  335.10 | $  342.53 | $  328.51 | $  341.13 |
+------------+-----------+-----------+-----------+-----------+
```

## 🔧 Command Line Options

### **inspect_database.py Options**
- `--symbols`: List all symbols
- `--symbol SYMBOL`: Specify symbol to inspect
- `--date YYYY-MM-DD`: Show data for specific date
- `--start YYYY-MM-DD`: Start date for range
- `--end YYYY-MM-DD`: End date for range  
- `--limit N`: Number of records to show (default: 10)
- `--tail`: Show last N records instead of first N
- `--around N`: Show N days around specified date

### **quick_db_check.py Usage**
```bash
python quick_db_check.py                    # Show available symbols
python quick_db_check.py SYMBOL             # Recent data for symbol
python quick_db_check.py SYMBOL DATE        # Specific date/shortcut
```

**Date shortcuts:**
- `today` - Current date
- `yesterday` - Previous day  
- `recent` - Last 10 records
- `YYYY-MM-DD` - Specific date

## 🎯 Smart Features

### **Missing Date Handling**
When querying a date with no data (e.g., weekends), the tool shows:
- Available date range for the symbol
- Closest earlier and later dates with data

### **Interactive Mode**
Run without arguments for interactive exploration:
```bash
python inspect_database.py
```

### **Performance Stats**
Each query shows:
- Total records available
- Date range coverage
- Price range (min/max)
- Latest closing price

## 💡 Pro Tips

1. **Weekend Dates**: Markets are closed on weekends, so use `yesterday` or check Friday's data
2. **Crypto vs Stocks**: Crypto trades 24/7, stocks only on weekdays
3. **Data Freshness**: The database auto-updates when data is older than 1 day
4. **Large Ranges**: Use `--limit` to avoid overwhelming output for large date ranges

## 🔍 Troubleshooting

**No data found?**
- Check if symbol exists: `python inspect_database.py --symbols`
- Verify date format: `YYYY-MM-DD`
- Try nearby dates if markets were closed

**Symbol not in database?**
```python
# Add data for new symbol
from src.data.fetcher import YahooFetcher
fetcher = YahooFetcher(use_cache=True)
fetcher.fetch_data_with_cache('NEW-SYMBOL', period='1mo')
```

These tools make it easy to explore your cached financial data and verify the database is working correctly! 🚀
