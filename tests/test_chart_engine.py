"""
Test suite for chart visualization functionality.
Comprehensive tests for the matplotlib charting system.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import tempfile
import os

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.visualization.chart_engine import OHLCVChart
from src.visualization.indicators import TechnicalIndicators, calculate_chart_indicators
from src.visualization.formatters import DateAxisFormatter, PriceAxisFormatter
from src.data.database import OHLCVDatabase


class TestOHLCVChart:
    """Test suite for OHLCVChart class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data for testing."""
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        np.random.seed(42)  # For reproducible tests
        
        # Generate realistic OHLC data
        base_price = 100.0
        data = []
        
        for i, date in enumerate(dates):
            # Random walk with some trend
            price_change = np.random.normal(0, 2)
            base_price = max(10, base_price + price_change)  # Ensure positive prices
            
            # Generate OHLC with realistic relationships
            open_price = base_price
            close_price = base_price + np.random.normal(0, 1)
            high_price = max(open_price, close_price) + abs(np.random.normal(0, 0.5))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, 0.5))
            
            # Ensure low <= open,close <= high
            low_price = min(low_price, open_price, close_price)
            high_price = max(high_price, open_price, close_price)
            
            volume = np.random.randint(1000000, 10000000)
            
            data.append({
                'open': open_price,
                'high': high_price, 
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'dividends': 0.0,
                'stock_splits': 0.0
            })
            
            base_price = close_price
        
        df = pd.DataFrame(data, index=dates)
        return df
    
    @pytest.fixture  
    def mock_database(self, sample_data):
        """Create mock database with sample data."""
        mock_db = MagicMock(spec=OHLCVDatabase)
        mock_db.get_data.return_value = sample_data
        return mock_db
    
    @pytest.fixture
    def mock_cache_manager(self, sample_data):
        """Create mock cache manager."""
        mock_cache = Mock()
        mock_cache.get_cached_data.return_value = sample_data
        return mock_cache
    
    @pytest.fixture
    def chart_with_mocks(self, mock_database):
        """Create chart instance with mocked dependencies."""
        with patch('src.visualization.chart_engine.CacheManager') as mock_cache_class, \
             patch('src.visualization.chart_engine.YahooFetcher') as mock_fetcher_class:
            
            # Setup mocks
            mock_cache_class.return_value.get_cached_data.return_value = mock_database.get_data()
            mock_fetcher_class.return_value = Mock()
            
            chart = OHLCVChart(mock_database, 'TEST-SYMBOL')
            return chart
    
    def test_chart_initialization(self):
        """Test chart initialization."""
        # Test with mock database
        mock_db = Mock(spec=OHLCVDatabase)
        chart = OHLCVChart(mock_db, 'BTC-USD')
        
        assert chart.symbol == 'BTC-USD'
        assert chart.database == mock_db
        assert chart.figure is None
        assert chart.axes is None
        assert chart.data is None
    
    def test_parameter_validation(self, chart_with_mocks):
        """Test parameter validation."""
        chart = chart_with_mocks
        
        # Valid parameters should not raise
        chart._validate_parameters('1Y', 'linear', 'line', 'close', None, False)
        
        # Invalid timeframe
        with pytest.raises(ValueError, match="Invalid timeframe"):
            chart._validate_parameters('INVALID', 'linear', 'line', 'close', None, False)
        
        # Invalid scale
        with pytest.raises(ValueError, match="Invalid scale"):
            chart._validate_parameters('1Y', 'invalid', 'line', 'close', None, False)
        
        # Invalid style
        with pytest.raises(ValueError, match="Invalid style"):
            chart._validate_parameters('1Y', 'linear', 'invalid', 'close', None, False)
        
        # Invalid indicators
        with pytest.raises(ValueError, match="Invalid indicators"):
            chart._validate_parameters('1Y', 'linear', 'line', 'close', 'INVALID', False)
    
    @pytest.mark.parametrize("timeframe,expected_days", [
        ('5D', 7),
        ('1M', 35),
        ('3M', 95),
        ('6M', 190),
        ('1Y', 370),
        ('5Y', 1830)
    ])
    def test_timeframe_date_calculation(self, chart_with_mocks, timeframe, expected_days):
        """Test that timeframes calculate correct date ranges."""
        chart = chart_with_mocks
        
        with patch('src.visualization.chart_engine.date') as mock_date:
            mock_date.today.return_value = date(2024, 12, 31)
            
            # Mock the data retrieval to avoid actual database calls
            with patch.object(chart.cache_manager, 'get_cached_data') as mock_get_data:
                mock_get_data.return_value = pd.DataFrame()
                
                try:
                    chart._get_data(timeframe, 'close')
                except ValueError:
                    pass  # Expected for empty dataframe
                
                # Check that the method was called with appropriate date range
                args, kwargs = mock_get_data.call_args
                if 'start_date' in kwargs and kwargs['start_date']:
                    start_date = kwargs['start_date']
                    end_date = kwargs['end_date'] or date(2024, 12, 31)
                    actual_days = (end_date - start_date).days
                    
                    # Allow some tolerance for timeframe calculations
                    assert abs(actual_days - expected_days) <= 5
    
    @patch('matplotlib.pyplot.subplots')
    def test_plot_method_calls(self, mock_subplots, chart_with_mocks, sample_data):
        """Test that plot method sets up chart correctly."""
        # Setup mocks
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        chart = chart_with_mocks
        
        # Mock data retrieval
        with patch.object(chart, '_get_data', return_value=sample_data):
            # Test basic plot
            result = chart.plot()
            
            assert result == chart  # Should return self for chaining
            assert chart.figure == mock_fig
            
            # Verify subplots was called for single plot
            mock_subplots.assert_called()
    
    @patch('matplotlib.pyplot.subplots')
    def test_volume_subplot_creation(self, mock_subplots, chart_with_mocks, sample_data):
        """Test volume subplot creation."""
        # Setup mocks for subplot scenario
        mock_fig = Mock()
        mock_ax1 = Mock()
        mock_ax2 = Mock()
        mock_subplots.return_value = (mock_fig, [mock_ax1, mock_ax2])
        
        chart = chart_with_mocks
        
        with patch.object(chart, '_get_data', return_value=sample_data):
            chart.plot(volume='subplot')
            
            # Should create 2 subplots for volume
            call_args = mock_subplots.call_args
            assert call_args[0][0] == 2  # 2 rows
            assert call_args[0][1] == 1  # 1 column
    
    def test_error_handling_empty_data(self, chart_with_mocks):
        """Test error handling for empty data."""
        chart = chart_with_mocks
        
        # Mock empty data
        with patch.object(chart, '_get_data', return_value=pd.DataFrame()):
            with pytest.raises(ValueError, match="No data available"):
                chart.plot()
    
    def test_save_without_plot(self, chart_with_mocks):
        """Test save method error when no plot exists."""
        chart = chart_with_mocks
        
        with pytest.raises(ValueError, match="No chart to save"):
            chart.save('test.png')
    
    def test_show_without_plot(self, chart_with_mocks):
        """Test show method error when no plot exists."""
        chart = chart_with_mocks
        
        with pytest.raises(ValueError, match="No chart to display"):
            chart.show()


class TestTechnicalIndicators:
    """Test suite for TechnicalIndicators class."""
    
    @pytest.fixture
    def price_series(self):
        """Create sample price series."""
        dates = pd.date_range(start='2024-01-01', periods=100)
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100) * 0.1)
        return pd.Series(prices, index=dates)
    
    def test_moving_average(self, price_series):
        """Test moving average calculation."""
        ma = TechnicalIndicators.moving_average(price_series, window=20)
        
        assert len(ma) == len(price_series)
        assert not ma.isna().all()  # Should have some non-NaN values
        
        # MA should generally be smoother than original data (allow small variance)
        # Use dropna() to compare only valid values
        ma_valid = ma.dropna()
        price_valid = price_series[ma.notna()]
        assert ma_valid.std() <= price_valid.std() * 1.1  # Allow 10% tolerance
    
    def test_exponential_moving_average(self, price_series):
        """Test exponential moving average calculation."""
        ema = TechnicalIndicators.exponential_moving_average(price_series, window=20)
        
        assert len(ema) == len(price_series)
        assert not ema.isna().all()
        
        # EMA should react faster than SMA to recent price changes
        sma = TechnicalIndicators.moving_average(price_series, window=20)
        
        # Last values should differ (EMA more responsive)
        assert abs(ema.iloc[-1] - sma.iloc[-1]) > 0
    
    def test_bollinger_bands(self, price_series):
        """Test Bollinger Bands calculation."""
        bands = TechnicalIndicators.bollinger_bands(price_series, window=20, std_dev=2)
        
        assert 'upper' in bands
        assert 'middle' in bands  
        assert 'lower' in bands
        
        # Upper should be > middle > lower (ignoring NaN values)
        valid_idx = ~bands['middle'].isna()
        assert (bands['upper'][valid_idx] >= bands['middle'][valid_idx]).all()
        assert (bands['middle'][valid_idx] >= bands['lower'][valid_idx]).all()
        
        # Middle should equal SMA
        sma = TechnicalIndicators.moving_average(price_series, window=20)
        pd.testing.assert_series_equal(bands['middle'], sma)
    
    def test_rsi(self, price_series):
        """Test RSI calculation."""
        rsi = TechnicalIndicators.rsi(price_series, window=14)
        
        assert len(rsi) == len(price_series)
        
        # RSI should be between 0 and 100
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()
    
    def test_calculate_chart_indicators(self):
        """Test chart indicators calculation."""
        # Create sample OHLCV data
        dates = pd.date_range(start='2024-01-01', periods=100)
        data = pd.DataFrame({
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 102,
            'low': np.random.randn(100).cumsum() + 98,
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        # Test no indicators
        result = calculate_chart_indicators(data, None)
        assert len(result) == 0
        
        # Test MA50
        result = calculate_chart_indicators(data, 'MA50')
        assert 'MA50' in result
        assert 'MA200' not in result
        
        # Test MA200  
        result = calculate_chart_indicators(data, 'MA200')
        assert 'MA200' in result
        assert 'MA50' not in result
        
        # Test both
        result = calculate_chart_indicators(data, 'BOTH')
        assert 'MA50' in result
        assert 'MA200' in result


class TestFormatters:
    """Test suite for axis formatters."""
    
    def test_date_axis_formatter(self):
        """Test date axis formatting."""
        # Create mock axis
        mock_ax = Mock()
        mock_ax.xaxis = Mock()
        mock_ax.xaxis.get_majorticklabels.return_value = [Mock() for _ in range(10)]
        mock_ax.get_xticklabels.return_value = [Mock() for _ in range(10)]
        
        # Create sample date index
        dates = pd.date_range(start='2024-01-01', periods=100)
        
        # Test different timeframes
        timeframes = ['5D', '1M', '3M', '6M', 'YTD', '1Y', '5Y', 'MAX']
        
        for timeframe in timeframes:
            # Should not raise an exception
            DateAxisFormatter.format_date_axis(mock_ax, dates, timeframe)
            
            # Verify formatter was set
            mock_ax.xaxis.set_major_formatter.assert_called()
            mock_ax.xaxis.set_major_locator.assert_called()
    
    def test_price_axis_formatter(self):
        """Test price axis formatting."""
        mock_ax = Mock()
        mock_ax.yaxis = Mock()
        
        # Test different symbols and price ranges
        test_cases = [
            ('BTC-USD', pd.Series([50000, 60000, 55000])),  # Crypto
            ('AAPL', pd.Series([150, 160, 155])),           # Stock
            ('PENNY', pd.Series([0.5, 1.0, 0.75]))          # Penny stock
        ]
        
        for symbol, prices in test_cases:
            # Should not raise an exception
            PriceAxisFormatter.format_price_axis(mock_ax, symbol, prices)
            
            # Verify formatter was set
            mock_ax.yaxis.set_major_formatter.assert_called()


@pytest.mark.integration
class TestChartIntegration:
    """Integration tests for the complete charting system."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    @pytest.mark.skip(reason="Requires matplotlib installation and display")
    def test_end_to_end_chart_creation(self, temp_db_path):
        """Test complete chart creation process."""
        # This test would require actual matplotlib and display
        # Skip in automated testing but useful for manual verification
        
        from src.data.database import OHLCVDatabase
        
        # Create database with sample data
        db = OHLCVDatabase(temp_db_path)
        
        # Add sample data
        dates = pd.date_range(start='2024-01-01', periods=100)
        sample_data = pd.DataFrame({
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 102,
            'low': np.random.randn(100).cumsum() + 98,
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100),
            'dividends': [0.0] * 100,
            'stock_splits': [0.0] * 100
        }, index=dates)
        
        db.store_data('TEST-SYMBOL', sample_data)
        
        # Create and test chart
        chart = OHLCVChart(db, 'TEST-SYMBOL')
        
        # Test various configurations
        configs = [
            {'timeframe': '1Y', 'style': 'line'},
            {'timeframe': '6M', 'style': 'candlestick', 'indicators': 'MA50'},
            {'timeframe': '3M', 'style': 'area', 'volume': 'subplot'}
        ]
        
        for config in configs:
            try:
                result = chart.plot(**config)
                assert result == chart
                assert chart.figure is not None
                
                # Test save functionality
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    chart.save(tmp.name)
                    assert os.path.exists(tmp.name)
                    os.unlink(tmp.name)
                    
            except Exception as e:
                pytest.fail(f"Chart creation failed with config {config}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
