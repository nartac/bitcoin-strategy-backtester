"""
Test suite for cache manager functionality.
Tests intelligent caching logic, cache hits/misses, and performance.
"""

import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
import tempfile
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch

from src.data.cache_manager import CacheManager
from src.data.database import OHLCVDatabase
from src.data.fetcher import YahooFetcher


class TestCacheManager:
    """Test suite for CacheManager class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = OHLCVDatabase(db_path)
        yield db
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def mock_fetcher(self):
        """Create mock fetcher for testing."""
        fetcher = Mock(spec=YahooFetcher)
        
        # Sample data that mock fetcher returns - use recent dates to avoid cache age issues
        from datetime import date, timedelta
        today = date.today()
        dates = pd.date_range(start=today - timedelta(days=9), end=today, freq='D')
        sample_data = pd.DataFrame({
            'open': [100, 102, 105, 103, 108, 110, 107, 109, 111, 114],
            'high': [105, 107, 108, 107, 112, 115, 110, 112, 115, 118],
            'low': [98, 100, 102, 100, 106, 108, 105, 107, 109, 112],
            'close': [102, 105, 103, 104, 110, 112, 109, 111, 114, 116],  # Fixed: close within [low, high]
            'volume': [1000, 1200, 800, 1500, 2000, 1800, 1300, 1100, 1600, 1900],
            'dividends': [0.0] * 10,
            'stock_splits': [0.0] * 10
        }, index=dates)
        
        fetcher.fetch_data.return_value = sample_data
        return fetcher
    
    @pytest.fixture
    def cache_manager(self, temp_db, mock_fetcher):
        """Create cache manager with temp database and mock fetcher."""
        return CacheManager(database=temp_db, fetcher=mock_fetcher, max_age_days=1)
    
    def test_cache_miss_empty_database(self, cache_manager, mock_fetcher):
        """Test cache miss when database is empty."""
        symbol = 'BTC-USD'
        
        # Should be cache miss and fetch from source
        data = cache_manager.get_cached_data(symbol)
        
        assert not data.empty
        assert cache_manager.cache_misses == 1
        assert cache_manager.cache_hits == 0
        assert cache_manager.fetch_count == 1
        
        # Mock fetcher should have been called
        mock_fetcher.fetch_data.assert_called_once()
    
    def test_cache_hit_fresh_data(self, cache_manager, temp_db, mock_fetcher):
        """Test cache hit when data is fresh."""
        symbol = 'BTC-USD'
        
        # Pre-populate database with recent data
        dates = pd.date_range(start=datetime.now().date() - timedelta(days=5), 
                             end=datetime.now().date(), freq='D')
        fresh_data = pd.DataFrame({
            'open': [100] * len(dates),
            'high': [105] * len(dates),
            'low': [95] * len(dates),
            'close': [102] * len(dates),
            'volume': [1000] * len(dates),
            'dividends': [0.0] * len(dates),
            'stock_splits': [0.0] * len(dates)
        }, index=dates)
        
        temp_db.store_ohlcv_data(symbol, fresh_data)
        
        # Should be cache hit
        data = cache_manager.get_cached_data(symbol)
        
        assert not data.empty
        assert cache_manager.cache_hits == 1
        assert cache_manager.cache_misses == 0
        assert cache_manager.fetch_count == 0
        
        # Mock fetcher should NOT have been called
        mock_fetcher.fetch_data.assert_not_called()
    
    def test_cache_miss_stale_data(self, cache_manager, temp_db, mock_fetcher):
        """Test cache miss when data is stale."""
        symbol = 'BTC-USD'
        
        # Pre-populate database with old data
        old_end_date = datetime.now().date() - timedelta(days=10)
        dates = pd.date_range(start=old_end_date - timedelta(days=5), 
                             end=old_end_date, freq='D')
        old_data = pd.DataFrame({
            'open': [100] * len(dates),
            'high': [105] * len(dates),
            'low': [95] * len(dates),
            'close': [102] * len(dates),
            'volume': [1000] * len(dates),
            'dividends': [0.0] * len(dates),
            'stock_splits': [0.0] * len(dates)
        }, index=dates)
        
        temp_db.store_ohlcv_data(symbol, old_data)
        
        # Should be cache miss due to stale data
        data = cache_manager.get_cached_data(symbol, max_age_days=1)
        
        assert not data.empty
        assert cache_manager.cache_misses == 1
        assert cache_manager.cache_hits == 0
        assert cache_manager.fetch_count == 1
        
        # Mock fetcher should have been called to get fresh data
        mock_fetcher.fetch_data.assert_called_once()
    
    def test_partial_cache_miss_missing_dates(self, cache_manager, temp_db, mock_fetcher):
        """Test partial cache miss when some dates are missing."""
        symbol = 'BTC-USD'
        
        # Pre-populate database with partial data
        recent_dates = pd.date_range(start=datetime.now().date() - timedelta(days=3), 
                                   end=datetime.now().date(), freq='D')
        partial_data = pd.DataFrame({
            'open': [100] * len(recent_dates),
            'high': [105] * len(recent_dates),
            'low': [95] * len(recent_dates),
            'close': [102] * len(recent_dates),
            'volume': [1000] * len(recent_dates),
            'dividends': [0.0] * len(recent_dates),
            'stock_splits': [0.0] * len(recent_dates)
        }, index=recent_dates)
        
        temp_db.store_ohlcv_data(symbol, partial_data)
        
        # Request data for wider range (should trigger fetch for missing dates)
        request_start = datetime.now().date() - timedelta(days=10)
        request_end = datetime.now().date()
        
        data = cache_manager.get_cached_data(symbol, start_date=request_start, end_date=request_end)
        
        assert not data.empty
        assert cache_manager.cache_misses == 1
        assert cache_manager.fetch_count == 1
        
        # Mock fetcher should have been called for missing date range
        mock_fetcher.fetch_data.assert_called_once()
    
    def test_cache_warm_operation(self, cache_manager, mock_fetcher):
        """Test cache warming functionality."""
        symbols = ['BTC-USD', 'ETH-USD', 'AAPL']
        
        # Warm cache
        cache_manager.warm_cache(symbols, period='1y')
        
        # Should have called fetcher for each symbol
        assert mock_fetcher.fetch_data.call_count == len(symbols)
        
        # Verify calls were made with correct symbols
        call_args_list = mock_fetcher.fetch_data.call_args_list
        called_symbols = [call[0][0] for call in call_args_list]  # First positional arg
        assert set(called_symbols) == set(symbols)
    
    def test_cache_stats(self, cache_manager, mock_fetcher):
        """Test cache statistics tracking."""
        symbol = 'BTC-USD'
        
        # Initial stats
        stats = cache_manager.get_cache_stats()
        assert stats['cache_hits'] == 0
        assert stats['cache_misses'] == 0
        assert stats['total_requests'] == 0
        assert stats['hit_rate_percent'] == 0
        
        # Trigger cache miss
        cache_manager.get_cached_data(symbol)
        
        # Updated stats
        stats = cache_manager.get_cache_stats()
        assert stats['cache_misses'] == 1
        assert stats['total_requests'] == 1
        assert stats['hit_rate_percent'] == 0.0
        
        # Trigger cache hit
        cache_manager.get_cached_data(symbol)
        
        # Updated stats
        stats = cache_manager.get_cache_stats()
        assert stats['cache_hits'] == 1
        assert stats['cache_misses'] == 1
        assert stats['total_requests'] == 2
        assert stats['hit_rate_percent'] == 50.0
    
    def test_symbol_cache_update(self, cache_manager, temp_db, mock_fetcher):
        """Test updating cache for specific symbol."""
        symbol = 'BTC-USD'
        
        # Pre-populate with old data
        old_dates = pd.date_range(start='2023-01-01', end='2023-01-05', freq='D')
        old_data = pd.DataFrame({
            'open': [100] * len(old_dates),
            'high': [105] * len(old_dates),
            'low': [95] * len(old_dates),
            'close': [102] * len(old_dates),
            'volume': [1000] * len(old_dates),
            'dividends': [0.0] * len(old_dates),
            'stock_splits': [0.0] * len(old_dates)
        }, index=old_dates)
        
        temp_db.store_ohlcv_data(symbol, old_data)
        
        # Update cache
        result = cache_manager.update_symbol_cache(symbol)
        assert result is True
        
        # Should have fetched new data
        assert mock_fetcher.fetch_data.called
    
    def test_symbol_cache_info(self, cache_manager, temp_db):
        """Test getting cache information for specific symbol."""
        symbol = 'BTC-USD'
        
        # No data initially
        info = cache_manager.get_symbol_cache_info(symbol)
        assert info['symbol'] == symbol
        assert info['record_count'] == 0
        assert info['date_range'] is None
        assert info['cache_age_days'] is None
        
        # Add some data
        dates = pd.date_range(start=datetime.now().date() - timedelta(days=2), 
                             end=datetime.now().date(), freq='D')
        data = pd.DataFrame({
            'open': [100] * len(dates),
            'high': [105] * len(dates),
            'low': [95] * len(dates),
            'close': [102] * len(dates),
            'volume': [1000] * len(dates),
            'dividends': [0.0] * len(dates),
            'stock_splits': [0.0] * len(dates)
        }, index=dates)
        
        temp_db.store_ohlcv_data(symbol, data)
        
        # Check updated info
        info = cache_manager.get_symbol_cache_info(symbol)
        assert info['record_count'] == len(dates)
        assert info['date_range'] is not None
        assert info['cache_age_days'] is not None
        assert info['cache_age_days'] <= 1  # Should be fresh
        assert info['is_fresh'] is True
    
    def test_clear_old_data(self, cache_manager, temp_db):
        """Test clearing old data functionality."""
        from datetime import date, timedelta
        
        symbol = 'BTC-USD'
        
        # Add old and recent data using relative dates
        today = date.today()
        old_dates = pd.date_range(start=today - timedelta(days=500), end=today - timedelta(days=490), freq='D')
        recent_dates = pd.date_range(start=today - timedelta(days=9), end=today, freq='D')
        
        old_data = pd.DataFrame({
            'open': [100] * len(old_dates),
            'high': [105] * len(old_dates),
            'low': [95] * len(old_dates),
            'close': [102] * len(old_dates),
            'volume': [1000] * len(old_dates),
            'dividends': [0.0] * len(old_dates),
            'stock_splits': [0.0] * len(old_dates)
        }, index=old_dates)
        
        recent_data = pd.DataFrame({
            'open': [110] * len(recent_dates),
            'high': [115] * len(recent_dates),
            'low': [105] * len(recent_dates),
            'close': [112] * len(recent_dates),
            'volume': [2000] * len(recent_dates),
            'dividends': [0.0] * len(recent_dates),
            'stock_splits': [0.0] * len(recent_dates)
        }, index=recent_dates)
        
        temp_db.store_ohlcv_data(symbol, old_data)
        temp_db.store_ohlcv_data(symbol, recent_data)
        
        # Verify both datasets are stored
        all_data = temp_db.get_ohlcv_data(symbol)
        assert len(all_data) == len(old_dates) + len(recent_dates)
        
        # Clear old data (keep last 365 days)
        cache_manager.clear_old_data(days_to_keep=365)
        
        # Verify old data is gone, recent data remains
        remaining_data = temp_db.get_ohlcv_data(symbol)
        assert len(remaining_data) == len(recent_dates)
        
        # Verify it's the recent data that remains
        assert remaining_data['close'].iloc[0] == 112  # Recent data value


@pytest.mark.integration
class TestCacheManagerIntegration:
    """Integration tests for cache manager with real fetcher."""
    
    def test_integration_with_yahoo_fetcher(self):
        """Test cache manager integration with real Yahoo Finance fetcher."""
        # Skip if no internet connection available
        pytest.importorskip("yfinance")
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Create real fetcher (but disable caching to avoid circular dependency)
            fetcher = YahooFetcher(use_cache=False)
            database = OHLCVDatabase(db_path)
            cache_manager = CacheManager(database=database, fetcher=fetcher, max_age_days=30)
            
            # Test with a known stable symbol and specific recent date range
            symbol = 'AAPL'
            from datetime import date, timedelta
            end_date = date.today() - timedelta(days=7)   # A week ago (data should definitely exist)
            start_date = end_date - timedelta(days=10)    # 10-day range
            
            # First call - should fetch and cache data
            data1 = cache_manager.get_cached_data(symbol, start_date=start_date, end_date=end_date)
            assert not data1.empty
            initial_misses = cache_manager.cache_misses
            initial_fetch_count = cache_manager.fetch_count
            
            # Verify data was stored in database
            stored_data = database.get_ohlcv_data(symbol, start_date=start_date, end_date=end_date)
            assert not stored_data.empty
            assert len(stored_data) > 0
            
            # Verify cache statistics were updated
            stats = cache_manager.get_cache_stats()
            assert stats['total_requests'] > 0
            assert stats['symbols_cached'] == 1
            assert stats['total_records'] > 0
            
            print(f"Successfully cached {len(data1)} records for {symbol}")
            print(f"Cache stats: {stats}")
            
        finally:
            Path(db_path).unlink(missing_ok=True)
    
    def test_cache_performance_benchmark(self):
        """Benchmark cache performance vs direct fetching."""
        import time
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Create fetcher with caching
            fetcher_with_cache = YahooFetcher(use_cache=True, db_path=db_path)
            
            # Create fetcher without caching
            fetcher_no_cache = YahooFetcher(use_cache=False)
            
            symbol = 'BTC-USD'
            
            # First call with caching (will be slow due to initial fetch)
            start_time = time.time()
            data1 = fetcher_with_cache.fetch_data_with_cache(symbol, period='1y')
            first_call_time = time.time() - start_time
            
            # Second call with caching (should be fast due to cache hit)
            start_time = time.time()
            data2 = fetcher_with_cache.fetch_data_with_cache(symbol, period='1y')
            second_call_time = time.time() - start_time
            
            # Direct fetch for comparison
            start_time = time.time()
            data3 = fetcher_no_cache.fetch_data(symbol, period='1y')
            direct_fetch_time = time.time() - start_time
            
            # Verify data consistency
            assert len(data1) > 0
            assert len(data2) > 0
            assert len(data3) > 0
            
            # Cache hit should be significantly faster than direct fetch
            assert second_call_time < direct_fetch_time * 0.5  # At least 2x faster
            
            print(f"First call (cache miss): {first_call_time:.3f}s")
            print(f"Second call (cache hit): {second_call_time:.3f}s")
            print(f"Direct fetch: {direct_fetch_time:.3f}s")
            print(f"Cache speedup: {direct_fetch_time / second_call_time:.1f}x")
            print(f"Cache speedup: {direct_fetch_time/second_call_time:.1f}x")
            
        finally:
            Path(db_path).unlink(missing_ok=True)
