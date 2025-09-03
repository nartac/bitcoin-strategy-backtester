# 📚 Examples & Test Scripts

This directory contains example scripts and comprehensive tests demonstrating the bitcoin-strategy-backtester functionality.

## 🧪 Test Scripts

### **simple_cache_test.py**
Quick test to verify database caching is working correctly.

```bash
python examples/simple_cache_test.py
```

**What it tests:**
- Database initialization
- First fetch (cache miss)
- Second fetch (cache hit) 
- Performance comparison
- Cache statistics

### **test_fetcher.py**
Comprehensive tests for the Yahoo Finance data fetcher.

```bash
python examples/test_fetcher.py
```

**What it tests:**
- Basic data fetching
- Multiple symbols (crypto & stocks)
- Different time periods
- Date range queries
- Bulk operations

### **test_database_features.py**
Full database functionality demonstration and testing.

```bash
python examples/test_database_features.py
```

**What it tests:**
- SQLite database with OHLCV caching
- Multiple symbol management
- Advanced database features
- Cache management operations
- Performance benchmarking

## 🎯 Usage Examples

### Quick Database Test
```bash
# Test if caching is working
python examples/simple_cache_test.py
```

### Test Data Fetching
```bash
# Test Yahoo Finance integration
python examples/test_fetcher.py
```

### Full Database Demo
```bash
# Run comprehensive database tests
python examples/test_database_features.py
```

## 📊 What You'll See

Each test script provides detailed output showing:
- ✅ Successful operations
- ❌ Any failures with details
- ⏱️ Performance timings
- 📊 Data statistics
- 🚀 Speed improvements from caching

## 🔧 Requirements

All example scripts automatically handle Python path resolution and use the same dependencies as the main project.

## 💡 Pro Tips

1. **Run examples in order**: Start with `simple_cache_test.py` to verify basic functionality
2. **Watch the performance**: Notice the dramatic speed improvements from database caching
3. **Explore the output**: Each script provides rich feedback about what's happening
4. **Use for debugging**: These scripts help verify everything is working correctly
