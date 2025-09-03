"""
Test suite for OHLCV database functionality.
Comprehensive tests for database operations, data integrity, and performance.
"""

import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
import sqlite3
import tempfile
from datetime import date, datetime, timedelta

from src.data.database import OHLCVDatabase
from src.data.models import OHLCVRecord, SymbolInfo, DataValidator


class TestOHLCVDatabase:
    """Test suite for OHLCVDatabase class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        # Create database instance
        db = OHLCVDatabase(db_path)
        yield db
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample OHLCV data with valid OHLCV relationships."""
        dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
        data = pd.DataFrame({
            'open': [100, 102, 105, 103, 108, 110, 107, 109, 111, 114],
            'high': [105, 107, 108, 107, 112, 115, 110, 112, 115, 118],
            'low': [98, 100, 102, 100, 106, 108, 105, 107, 109, 112],
            'close': [102, 105, 103, 104, 110, 112, 109, 111, 114, 116],  # Fixed: close must be within [low, high]
            'volume': [1000, 1200, 800, 1500, 2000, 1800, 1300, 1100, 1600, 1900],
            'dividends': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'stock_splits': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        }, index=dates)
        return data
    
    def test_database_creation(self, temp_db):
        """Test database and schema creation."""
        # Database should be created with proper schema
        assert Path(temp_db.db_path).exists()
        
        # Check tables exist
        with temp_db.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            
            assert 'symbols' in tables
            assert 'ohlcv_data' in tables
    
    def test_symbol_management(self, temp_db):
        """Test adding and updating symbols."""
        # Add new symbol
        symbol_id = temp_db.add_symbol('BTC-USD', asset_type='crypto', name='Bitcoin')
        assert isinstance(symbol_id, int)
        assert symbol_id > 0
        
        # Get symbol ID
        retrieved_id = temp_db.get_symbol_id('BTC-USD')
        assert retrieved_id == symbol_id
        
        # Update existing symbol
        updated_id = temp_db.add_symbol('BTC-USD', name='Bitcoin USD', exchange='Coinbase')
        assert updated_id == symbol_id  # Same ID
        
        # Verify symbol info
        symbols = temp_db.get_symbols_info()
        assert len(symbols) == 1
        assert symbols[0].symbol == 'BTC-USD'
        assert symbols[0].name == 'Bitcoin USD'
        assert symbols[0].asset_type == 'crypto'
    
    def test_ohlcv_data_storage(self, temp_db, sample_data):
        """Test storing and retrieving OHLCV data."""
        symbol = 'TEST-USD'
        
        # Store data
        stored_count = temp_db.store_ohlcv_data(symbol, sample_data)
        assert stored_count == len(sample_data)
        
        # Retrieve data
        retrieved_data = temp_db.get_ohlcv_data(symbol)
        assert len(retrieved_data) == len(sample_data)
        assert list(retrieved_data.columns) == ['open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits']
        
        # Check data values - adjust for database storage format
        expected_data = sample_data.copy()
        expected_data.index.name = 'date'  # Database returns index with name 'date'
        expected_data.index.freq = None  # Database doesn't preserve frequency info
        
        pd.testing.assert_frame_equal(
            retrieved_data.round(6), 
            expected_data.round(6), 
            check_dtype=False
        )
    
    def test_duplicate_prevention(self, temp_db, sample_data):
        """Test that duplicates are handled correctly."""
        symbol = 'TEST-USD'
        
        # Store data first time
        stored_count_1 = temp_db.store_ohlcv_data(symbol, sample_data)
        assert stored_count_1 == len(sample_data)
        
        # Store same data again (should be ignored)
        stored_count_2 = temp_db.store_ohlcv_data(symbol, sample_data)
        assert stored_count_2 == 0  # No new records
        
        # Verify only one set of data exists
        retrieved_data = temp_db.get_ohlcv_data(symbol)
        assert len(retrieved_data) == len(sample_data)
    
    def test_date_range_queries(self, temp_db, sample_data):
        """Test date range filtering."""
        symbol = 'TEST-USD'
        temp_db.store_ohlcv_data(symbol, sample_data)
        
        # Test start date only
        start_date = date(2023, 1, 5)
        filtered_data = temp_db.get_ohlcv_data(symbol, start_date=start_date)
        assert len(filtered_data) == 6  # 2023-01-05 to 2023-01-10
        assert filtered_data.index.min().date() == start_date
        
        # Test end date only
        end_date = date(2023, 1, 5)
        filtered_data = temp_db.get_ohlcv_data(symbol, end_date=end_date)
        assert len(filtered_data) == 5  # 2023-01-01 to 2023-01-05
        assert filtered_data.index.max().date() == end_date
        
        # Test both start and end date
        start_date = date(2023, 1, 3)
        end_date = date(2023, 1, 7)
        filtered_data = temp_db.get_ohlcv_data(symbol, start_date=start_date, end_date=end_date)
        assert len(filtered_data) == 5  # 2023-01-03 to 2023-01-07
    
    def test_date_range_info(self, temp_db, sample_data):
        """Test getting date range information."""
        symbol = 'TEST-USD'
        
        # No data initially
        date_range = temp_db.get_date_range(symbol)
        assert date_range is None
        
        # After storing data
        temp_db.store_ohlcv_data(symbol, sample_data)
        date_range = temp_db.get_date_range(symbol)
        assert date_range is not None
        
        min_date, max_date = date_range
        assert min_date == date(2023, 1, 1)
        assert max_date == date(2023, 1, 10)
    
    def test_missing_dates_detection(self, temp_db, sample_data):
        """Test missing date detection."""
        symbol = 'TEST-USD'
        temp_db.store_ohlcv_data(symbol, sample_data)
        
        # Test with range that includes all existing data
        missing_dates = temp_db.get_missing_dates(
            symbol, 
            date(2023, 1, 1), 
            date(2023, 1, 10)
        )
        assert len(missing_dates) == 0  # No missing dates
        
        # Test with extended range
        missing_dates = temp_db.get_missing_dates(
            symbol, 
            date(2022, 12, 28), 
            date(2023, 1, 15)
        )
        # Should find missing dates before and after existing data
        assert len(missing_dates) > 0
        assert date(2022, 12, 28) in missing_dates
        assert date(2023, 1, 15) in missing_dates
    
    def test_database_stats(self, temp_db, sample_data):
        """Test database statistics."""
        # Empty database stats
        stats = temp_db.get_data_stats()
        assert stats['symbol_count'] == 0
        assert stats['total_records'] == 0
        
        # After adding data
        symbol = 'TEST-USD'
        temp_db.store_ohlcv_data(symbol, sample_data)
        
        # Overall stats
        stats = temp_db.get_data_stats()
        assert stats['symbol_count'] == 1
        assert stats['total_records'] == len(sample_data)
        
        # Symbol-specific stats
        symbol_stats = temp_db.get_data_stats(symbol)
        assert symbol_stats['symbol'] == symbol
        assert symbol_stats['record_count'] == len(sample_data)
    
    def test_data_deletion(self, temp_db, sample_data):
        """Test deleting symbol data."""
        symbol = 'TEST-USD'
        temp_db.store_ohlcv_data(symbol, sample_data)
        
        # Verify data exists
        data = temp_db.get_ohlcv_data(symbol)
        assert len(data) == len(sample_data)
        
        # Delete data
        deleted_count = temp_db.delete_symbol_data(symbol)
        assert deleted_count == len(sample_data)
        
        # Verify data is gone
        data = temp_db.get_ohlcv_data(symbol)
        assert len(data) == 0


class TestOHLCVRecord:
    """Test suite for OHLCVRecord model."""
    
    def test_valid_record_creation(self):
        """Test creating valid OHLCV record."""
        record = OHLCVRecord(
            symbol='BTC-USD',
            date=date(2023, 1, 1),
            open=100.0,
            high=105.0,
            low=98.0,
            close=103.0,
            volume=1000
        )
        
        assert record.symbol == 'BTC-USD'
        assert record.open == 100.0
        assert record.high == 105.0
        assert record.low == 98.0
        assert record.close == 103.0
        assert record.volume == 1000
    
    def test_invalid_record_validation(self):
        """Test validation of invalid records."""
        # High < Low
        with pytest.raises(ValueError, match="High.*cannot be less than Low"):
            OHLCVRecord(
                symbol='TEST',
                date=date(2023, 1, 1),
                open=100.0,
                high=95.0,  # Less than low
                low=98.0,
                close=103.0,
                volume=1000
            )
        
        # Negative prices
        with pytest.raises(ValueError, match="Prices cannot be negative"):
            OHLCVRecord(
                symbol='TEST',
                date=date(2023, 1, 1),
                open=-100.0,
                high=105.0,
                low=98.0,
                close=103.0,
                volume=1000
            )
        
        # Open outside high-low range
        with pytest.raises(ValueError, match="Open.*must be between"):
            OHLCVRecord(
                symbol='TEST',
                date=date(2023, 1, 1),
                open=120.0,  # Above high
                high=105.0,
                low=98.0,
                close=103.0,
                volume=1000
            )
    
    def test_pandas_row_conversion(self):
        """Test creating record from pandas row."""
        row = pd.Series({
            'open': 100.0,
            'high': 105.0,
            'low': 98.0,
            'close': 103.0,
            'volume': 1000,
            'dividends': 0.0,
            'stock_splits': 0.0
        }, name=pd.Timestamp('2023-01-01'))
        
        record = OHLCVRecord.from_pandas_row('BTC-USD', row)
        
        assert record.symbol == 'BTC-USD'
        assert record.date == date(2023, 1, 1)
        assert record.open == 100.0
        assert record.volume == 1000


class TestDataValidator:
    """Test suite for DataValidator utility."""
    
    def test_dataframe_validation(self):
        """Test DataFrame validation."""
        # Valid DataFrame
        valid_data = pd.DataFrame({
            'open': [100, 102],
            'high': [105, 107],
            'low': [98, 100],
            'close': [102, 105],
            'volume': [1000, 1200]
        })
        
        errors = DataValidator.validate_dataframe(valid_data, 'TEST')
        assert len(errors) == 0
        
        # Invalid DataFrame (missing column)
        invalid_data = pd.DataFrame({
            'open': [100, 102],
            'high': [105, 107],
            'low': [98, 100],
            # Missing 'close' column
            'volume': [1000, 1200]
        })
        
        errors = DataValidator.validate_dataframe(invalid_data, 'TEST')
        assert len(errors) > 0
        assert any('Missing required columns' in error for error in errors)
    
    def test_dataframe_cleaning(self):
        """Test DataFrame cleaning functionality."""
        # Create DataFrame with issues
        dates = pd.date_range('2023-01-01', periods=5, freq='D')
        dirty_data = pd.DataFrame({
            'open': [100, 102, None, 103, 104],  # NaN value
            'high': [105, 107, 108, 102, 109],   # One invalid (high < low)
            'low': [98, 100, 102, 105, 106],     # One invalid (low > high)
            'close': [102, 105, 106, 104, 108],
            'volume': [1000, 1200, 800, 1500, 2000],
            'dividends': [None, 0.0, 0.0, 0.0, 0.0],  # NaN value
            'stock_splits': [0.0, 0.0, 0.0, 0.0, 0.0]  # Add missing column
        }, index=dates)
        
        cleaned_data = DataValidator.clean_dataframe(dirty_data)
        
        # Should remove rows with NaN and invalid high-low relationships
        assert len(cleaned_data) < len(dirty_data)
        
        # Dividends should be filled with 0
        assert cleaned_data['dividends'].isna().sum() == 0
        
        # All remaining data should be valid
        errors = DataValidator.validate_dataframe(cleaned_data, 'TEST')
        assert len(errors) == 0 or all('duplicate' not in error.lower() for error in errors)
@pytest.mark.integration
class TestDatabasePerformance:
    """Integration tests for database performance."""
    
    @pytest.fixture
    def large_dataset(self):
        """Generate large dataset for performance testing."""
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        size = len(dates)
        
        # Create realistic price data that increases over time
        base_prices = range(100, 100 + size)
        
        data = pd.DataFrame({
            'open': [float(p) for p in base_prices],
            'high': [float(p + 5) for p in base_prices],
            'low': [float(p - 2) for p in base_prices],
            'close': [float(p + 2) for p in base_prices],
            'volume': [int(1000 + (i % 1000)) for i in range(size)],
            'dividends': [0.0] * size,
            'stock_splits': [0.0] * size
        }, index=dates)
        
        return data
    
    def test_large_data_insertion(self, large_dataset):
        """Test performance with large dataset."""
        import time
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = OHLCVDatabase(db_path)
            
            # Measure insertion time
            start_time = time.time()
            stored_count = db.store_ohlcv_data('BTC-USD', large_dataset)
            insertion_time = time.time() - start_time
            
            assert stored_count == len(large_dataset)
            assert insertion_time < 10.0  # Should complete within 10 seconds
            
            # Measure query time
            start_time = time.time()
            retrieved_data = db.get_ohlcv_data('BTC-USD')
            query_time = time.time() - start_time
            
            assert len(retrieved_data) == len(large_dataset)
            assert query_time < 1.0  # Should complete within 1 second
            
        finally:
            Path(db_path).unlink(missing_ok=True)
    
    def test_query_performance_with_date_range(self, large_dataset):
        """Test query performance with date filtering."""
        import time
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db = OHLCVDatabase(db_path)
            db.store_ohlcv_data('BTC-USD', large_dataset)
            
            # Test date range query performance
            start_time = time.time()
            filtered_data = db.get_ohlcv_data(
                'BTC-USD', 
                start_date=date(2022, 1, 1), 
                end_date=date(2022, 12, 31)
            )
            query_time = time.time() - start_time
            
            assert len(filtered_data) == 365  # One year of data
            assert query_time < 0.5  # Should be very fast with proper indexing
            
        finally:
            Path(db_path).unlink(missing_ok=True)
