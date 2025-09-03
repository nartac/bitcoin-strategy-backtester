"""
Data fetching module for financial market data.
Enhanced Yahoo Finance fetcher with intelligent database caching.
"""

import yfinance as yf
import pandas as pd
import logging
from typing import Dict, Optional, List
from datetime import datetime, date

from ..utils.config import DATABASE_CONFIG, CACHE_WARM_SYMBOLS


class YahooFetcher:
    """
    Enhanced Yahoo Finance data fetcher with intelligent database caching.
    
    Provides unlimited free access to historical stock and cryptocurrency data
    with persistent storage and smart caching capabilities.
    """
    
    def __init__(self, use_cache: bool = True, db_path: str = None):
        """
        Initialize the Yahoo Finance fetcher with optional database caching.
        
        Args:
            use_cache: Whether to use database caching
            db_path: Optional custom database path
        """
        self.use_cache = use_cache
        self.logger = logging.getLogger(__name__)
        
        # Initialize database and cache manager if caching is enabled
        if self.use_cache:
            try:
                from .database import OHLCVDatabase
                from .cache_manager import CacheManager
                
                db_path = db_path or DATABASE_CONFIG['db_path']
                self.database = OHLCVDatabase(db_path)
                self.cache_manager = CacheManager(
                    database=self.database,
                    fetcher=self,  # Pass self for cache manager to use non-cached methods
                    max_age_days=DATABASE_CONFIG['max_cache_age_days']
                )
                
                self.logger.info(f"Database caching enabled: {db_path}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize database caching: {e}")
                self.use_cache = False
                self.database = None
                self.cache_manager = None
        else:
            self.database = None
            self.cache_manager = None
            self.logger.info("Database caching disabled")
        
        # Crypto symbol mapping for Yahoo Finance
        self.crypto_mapping = {
            'BTC': 'BTC-USD',
            'ETH': 'ETH-USD', 
            'LTC': 'LTC-USD',
            'XRP': 'XRP-USD',
            'ADA': 'ADA-USD',
            'DOT': 'DOT-USD',
            'LINK': 'LINK-USD',
            'BCH': 'BCH-USD',
            'XLM': 'XLM-USD',
            'DOGE': 'DOGE-USD',
            'MATIC': 'MATIC-USD',
            'AVAX': 'AVAX-USD',
            'ATOM': 'ATOM-USD'
        }
        
        # Known crypto symbols for auto-detection
        self.crypto_symbols = set(self.crypto_mapping.keys())
        
        self.logger.info(f"YahooFetcher initialized with {len(self.crypto_symbols)} crypto symbols")
    
    def _get_yahoo_symbol(self, symbol: str) -> str:
        """Convert symbol to Yahoo Finance format."""
        symbol = symbol.upper()
        
        # Check if it's a known crypto symbol
        if symbol in self.crypto_mapping:
            return self.crypto_mapping[symbol]
        
        # For stocks, return as-is
        return symbol
    
    def fetch_data(self, symbol: str, period: str = 'max', start_date: str = None, 
                   end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        Fetch data directly from Yahoo Finance (no caching).
        
        Args:
            symbol: Trading symbol (e.g., 'BTC', 'AAPL')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: OHLCV data with date index
        """
        try:
            # Convert symbol to Yahoo format
            yahoo_symbol = self._get_yahoo_symbol(symbol)
            
            # Create ticker object
            ticker = yf.Ticker(yahoo_symbol)
            
            # Fetch data based on parameters
            if start_date and end_date:
                data = ticker.history(start=start_date, end=end_date)
                self.logger.info(f"Fetched {len(data)} records for {symbol} from {start_date} to {end_date}")
            else:
                data = ticker.history(period=period)
                self.logger.info(f"Fetched {len(data)} records for {symbol} (period: {period})")
            
            if data.empty:
                self.logger.warning(f"No data returned for symbol: {symbol}")
                return pd.DataFrame()
            
            # Standardize column names (Yahoo uses Title Case)
            data.columns = data.columns.str.lower()
            
            # Ensure we have the required columns
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in data.columns:
                    self.logger.error(f"Missing required column '{col}' for {symbol}")
                    return pd.DataFrame()
            
            # Fill missing optional columns
            if 'dividends' not in data.columns:
                data['dividends'] = 0.0
            if 'stock splits' in data.columns:
                data['stock_splits'] = data['stock splits']
                data = data.drop('stock splits', axis=1)
            elif 'stock_splits' not in data.columns:
                data['stock_splits'] = 0.0
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to fetch data for {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_data_with_cache(self, symbol: str, period: str = 'max', 
                             force_refresh: bool = False, **kwargs) -> pd.DataFrame:
        """
        Fetch data with intelligent database caching.
        
        Args:
            symbol: Trading symbol
            period: Time period (ignored if using cache with date range)
            force_refresh: Force refresh from source
            
        Returns:
            pd.DataFrame: OHLCV data with date index
        """
        if not self.use_cache or self.cache_manager is None:
            # Fall back to direct fetching
            return self.fetch_data(symbol, period=period, **kwargs)
        
        try:
            if force_refresh:
                # Force refresh by updating cache
                self.cache_manager.update_symbol_cache(symbol, force_refresh=True)
            
            # Use cache manager to get data
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            
            # Convert string dates to date objects if provided
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            return self.cache_manager.get_cached_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )
            
        except Exception as e:
            self.logger.error(f"Cache fetch failed for {symbol}, falling back to direct fetch: {e}")
            return self.fetch_data(symbol, period=period, **kwargs)
    
    def get_full_history(self, symbol: str, use_cache: bool = None) -> pd.DataFrame:
        """Get maximum available historical data."""
        if use_cache is None:
            use_cache = self.use_cache
            
        if use_cache:
            return self.fetch_data_with_cache(symbol, period="max")
        else:
            return self.fetch_data(symbol, period="max")
    
    def get_recent_data(self, symbol: str, days: int = 365, use_cache: bool = None) -> pd.DataFrame:
        """Get recent data for specified number of days."""
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        if use_cache is None:
            use_cache = self.use_cache
            
        if use_cache:
            return self.fetch_data_with_cache(
                symbol,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
        else:
            return self.fetch_data(
                symbol,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
    
    def bulk_fetch(self, symbols: List[str], period: str = 'max', use_cache: bool = None) -> Dict[str, pd.DataFrame]:
        """
        Efficiently fetch multiple symbols.
        
        Args:
            symbols: List of symbols to fetch
            period: Time period for each symbol
            use_cache: Override cache usage for this operation
            
        Returns:
            Dict[str, pd.DataFrame]: Symbol -> DataFrame mapping
        """
        results = {}
        use_cache_for_bulk = use_cache if use_cache is not None else self.use_cache
        
        self.logger.info(f"Bulk fetching {len(symbols)} symbols")
        
        for symbol in symbols:
            try:
                if use_cache_for_bulk:
                    data = self.fetch_data_with_cache(symbol, period=period)
                else:
                    data = self.fetch_data(symbol, period=period)
                
                results[symbol] = data
                
                if not data.empty:
                    self.logger.info(f"✅ {symbol}: {len(data)} records")
                else:
                    self.logger.warning(f"❌ {symbol}: No data returned")
                    
            except Exception as e:
                self.logger.error(f"❌ {symbol}: {e}")
                results[symbol] = pd.DataFrame()
        
        return results
    
    def bulk_cache_symbols(self, symbols: List[str], period: str = 'max'):
        """
        Efficiently cache multiple symbols (pre-populate cache).
        
        Args:
            symbols: List of symbols to cache
            period: Time period to cache
        """
        if not self.use_cache or self.cache_manager is None:
            self.logger.warning("Caching not enabled, skipping bulk cache operation")
            return
        
        self.cache_manager.warm_cache(symbols, period=period)
    
    def get_cache_stats(self) -> Optional[Dict]:
        """
        Get cache performance statistics.
        
        Returns:
            Dict: Cache statistics or None if caching disabled
        """
        if not self.use_cache or self.cache_manager is None:
            return None
        
        return self.cache_manager.get_cache_stats()
    
    def warm_default_cache(self):
        """Pre-populate cache with default symbols."""
        if self.use_cache and self.cache_manager:
            self.cache_manager.warm_cache(CACHE_WARM_SYMBOLS)
    
    def clear_cache(self, symbol: str = None):
        """
        Clear cached data.
        
        Args:
            symbol: Specific symbol to clear (all if None)
        """
        if not self.use_cache or self.database is None:
            return
        
        if symbol:
            self.database.delete_symbol_data(symbol)
            self.logger.info(f"Cleared cache for {symbol}")
        else:
            # Clear all data (would need to implement full database reset)
            self.logger.warning("Full cache clear not implemented - clear specific symbols instead")
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols."""
        if self.use_cache and self.database:
            symbols_info = self.database.get_symbols_info()
            return [info.symbol for info in symbols_info]
        else:
            return list(self.crypto_mapping.values()) + ['AAPL', 'TSLA', 'SPY', 'MSFT', 'GOOGL']


# For backward compatibility
UniversalFetcher = YahooFetcher