"""
Intelligent caching system for OHLCV data.
Manages data freshness, updates, and optimization for bitcoin-strategy-backtester.
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
import pandas as pd

from .database import OHLCVDatabase
from .fetcher import YahooFetcher


class CacheManager:
    """
    Intelligent caching system for OHLCV data.
    
    Features:
    - Smart cache hit/miss logic
    - Incremental data updates
    - Configurable data freshness
    - Bulk warming operations
    - Performance monitoring
    """
    
    def __init__(self, database: OHLCVDatabase = None, fetcher: YahooFetcher = None, 
                 max_age_days: int = 1):
        """
        Initialize cache manager with database and fetcher.
        
        Args:
            database: Database instance (creates new if None)
            fetcher: Data fetcher instance (creates new if None)
            max_age_days: Maximum age of cached data before refresh
        """
        self.database = database or OHLCVDatabase()
        self.fetcher = fetcher or YahooFetcher()
        self.max_age_days = max_age_days
        
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.cache_hits = 0
        self.cache_misses = 0
        self.fetch_count = 0
    
    def get_cached_data(self, symbol: str, start_date: date = None, end_date: date = None, 
                       max_age_days: int = None) -> pd.DataFrame:
        """
        Get data with intelligent caching logic.
        
        Args:
            symbol: Trading symbol
            start_date: Start date (None for earliest available)
            end_date: End date (None for latest available)
            max_age_days: Override default max age
            
        Returns:
            pd.DataFrame: OHLCV data with date index
        """
        max_age = max_age_days or self.max_age_days
        today = date.today()
        
        # Get existing data range from database
        date_range = self.database.get_date_range(symbol)
        
        if date_range is None:
            # No cached data - fetch everything
            self.cache_misses += 1
            self.logger.info(f"No cached data for {symbol}, fetching from source")
            return self._fetch_and_cache(symbol, start_date, end_date)
        
        cached_start, cached_end = date_range
        
        # Determine if cache is fresh enough
        cache_age_days = (today - cached_end).days
        is_cache_fresh = cache_age_days <= max_age
        
        # Determine what data we need
        effective_start = start_date or cached_start
        effective_end = end_date or today
        
        # Check if we need to fetch additional data
        needs_earlier_data = effective_start < cached_start
        needs_later_data = effective_end > cached_end or not is_cache_fresh
        
        # Add tolerance for small gaps (e.g., weekends, holidays)
        gap_tolerance_days = 7  # Allow up to 1 week gap without fetching
        
        if needs_earlier_data:
            gap_days = (cached_start - effective_start).days
            if gap_days <= gap_tolerance_days:
                # Small gap - use available data instead of fetching
                self.logger.debug(f"Small gap ({gap_days} days) for {symbol}, using available data from {cached_start}")
                needs_earlier_data = False
                effective_start = cached_start
        
        if needs_earlier_data or needs_later_data:
            # Need to fetch additional data
            if needs_earlier_data and needs_later_data:
                # Fetch full range
                self.logger.info(f"Cache miss for {symbol}: fetching full range {effective_start} to {effective_end}")
                new_data = self._fetch_and_cache(symbol, effective_start, effective_end)
            elif needs_earlier_data:
                # Fetch earlier data
                self.logger.info(f"Cache miss for {symbol}: fetching earlier data {effective_start} to {cached_start}")
                new_data = self._fetch_and_cache(symbol, effective_start, cached_start - timedelta(days=1))
            else:
                # Fetch later data
                fetch_start = cached_end + timedelta(days=1) if is_cache_fresh else cached_end
                self.logger.info(f"Cache miss for {symbol}: fetching later data {fetch_start} to {effective_end}")
                new_data = self._fetch_and_cache(symbol, fetch_start, effective_end)
            
            self.cache_misses += 1
        else:
            self.cache_hits += 1
            self.logger.debug(f"Cache hit for {symbol}")
        
        # Get the requested data from cache
        cached_data = self.database.get_ohlcv_data(symbol, effective_start, effective_end)
        
        return cached_data
    
    def _fetch_and_cache(self, symbol: str, start_date: date = None, end_date: date = None) -> pd.DataFrame:
        """
        Fetch data from source and cache it.
        
        Args:
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            
        Returns:
            pd.DataFrame: Fetched data
        """
        self.fetch_count += 1
        
        try:
            # Convert dates to strings for YahooFetcher
            start_str = start_date.isoformat() if start_date else None
            end_str = end_date.isoformat() if end_date else None
            
            # Fetch data
            if start_str and end_str:
                data = self.fetcher.fetch_data(symbol, start_date=start_str, end_date=end_str)
            else:
                # Fetch maximum available data
                data = self.fetcher.fetch_data(symbol, period='max')
            
            if not data.empty:
                # Store in database
                stored_count = self.database.store_ohlcv_data(symbol, data)
                self.logger.info(f"Fetched and cached {stored_count} records for {symbol}")
            else:
                self.logger.warning(f"No data fetched for {symbol}")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to fetch data for {symbol}: {e}")
            return pd.DataFrame()
    
    def update_symbol_cache(self, symbol: str, force_refresh: bool = False) -> bool:
        """
        Update cache for specific symbol.
        
        Args:
            symbol: Symbol to update
            force_refresh: Whether to force a full refresh
            
        Returns:
            bool: True if update was successful
        """
        try:
            if force_refresh:
                # Delete existing data and fetch fresh
                self.database.delete_symbol_data(symbol)
                self._fetch_and_cache(symbol)
            else:
                # Intelligent update
                self.get_cached_data(symbol, max_age_days=0)  # Force fresh data
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update cache for {symbol}: {e}")
            return False
    
    def warm_cache(self, symbols: List[str], period: str = 'max'):
        """
        Pre-populate cache for common symbols.
        
        Args:
            symbols: List of symbols to cache
            period: Time period to cache ('1y', '2y', 'max')
        """
        self.logger.info(f"Warming cache for {len(symbols)} symbols")
        
        for symbol in symbols:
            try:
                # Check if symbol already has recent data
                date_range = self.database.get_date_range(symbol)
                
                if date_range:
                    cached_start, cached_end = date_range
                    cache_age = (date.today() - cached_end).days
                    
                    if cache_age <= self.max_age_days:
                        self.logger.debug(f"Skipping {symbol} - cache is fresh")
                        continue
                
                # Fetch and cache data
                data = self.fetcher.fetch_data(symbol, period=period)
                if not data.empty:
                    stored_count = self.database.store_ohlcv_data(symbol, data)
                    self.logger.info(f"Warmed cache for {symbol}: {stored_count} records")
                else:
                    self.logger.warning(f"No data available for {symbol}")
                    
            except Exception as e:
                self.logger.error(f"Failed to warm cache for {symbol}: {e}")
                continue
        
        self.logger.info(f"Cache warming completed for {len(symbols)} symbols")
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache performance statistics.
        
        Returns:
            Dict: Cache statistics
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        # Get database stats
        db_stats = self.database.get_data_stats()
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2),
            'fetch_count': self.fetch_count,
            'symbols_cached': db_stats.get('symbol_count', 0),
            'total_records': db_stats.get('total_records', 0),
            'earliest_date': db_stats.get('earliest_date'),
            'latest_date': db_stats.get('latest_date')
        }
    
    def clear_old_data(self, days_to_keep: int = 365):
        """
        Clear old data to save space.
        
        Args:
            days_to_keep: Number of days of data to keep
        """
        cutoff_date = date.today() - timedelta(days=days_to_keep)
        
        with self.database.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM ohlcv_data 
                WHERE date < ?
            """, (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            self.logger.info(f"Deleted {deleted_count} old records (before {cutoff_date})")
    
    def get_symbol_cache_info(self, symbol: str) -> Dict:
        """
        Get cache information for specific symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dict: Symbol cache information
        """
        stats = self.database.get_data_stats(symbol)
        date_range = self.database.get_date_range(symbol)
        
        cache_age_days = None
        if date_range:
            cache_age_days = (date.today() - date_range[1]).days
        
        return {
            'symbol': symbol,
            'record_count': stats.get('record_count', 0),
            'date_range': date_range,
            'cache_age_days': cache_age_days,
            'is_fresh': cache_age_days is not None and cache_age_days <= self.max_age_days
        }
    
    def check_cache_freshness(self, symbols: List[str] = None) -> Dict[str, Dict]:
        """
        Check cache freshness for multiple symbols.
        
        Args:
            symbols: List of symbols to check (None for all symbols)
            
        Returns:
            Dict: Cache freshness info for each symbol
        """
        if symbols is None:
            # Get all symbols from database
            try:
                symbols_info = self.database.get_symbols_info()
                symbols = [symbol_info.symbol for symbol_info in symbols_info]
            except Exception as e:
                self.logger.warning(f"Could not auto-detect symbols: {e}")
                return {}
        
        freshness_info = {}
        for symbol in symbols:
            try:
                freshness_info[symbol] = self.get_symbol_cache_info(symbol)
            except Exception as e:
                self.logger.error(f"Error checking freshness for {symbol}: {e}")
                freshness_info[symbol] = {'error': str(e)}
        
        return freshness_info
    
    def refresh_stale_caches(self, symbols: List[str] = None, max_age_override: int = None) -> Dict[str, bool]:
        """
        Refresh stale caches for specified symbols.
        
        Args:
            symbols: List of symbols to refresh (None for all stale symbols)
            max_age_override: Override max age for this operation
            
        Returns:
            Dict: Success status for each symbol refresh
        """
        max_age = max_age_override or self.max_age_days
        
        if symbols is None:
            # Find all stale symbols
            freshness_info = self.check_cache_freshness()
            symbols = [symbol for symbol, info in freshness_info.items() 
                      if 'cache_age_days' in info and info['cache_age_days'] is not None 
                      and info['cache_age_days'] > max_age]
            
            if not symbols:
                self.logger.info("No stale caches found")
                return {}
        
        refresh_results = {}
        for symbol in symbols:
            try:
                self.logger.info(f"Refreshing stale cache for {symbol}")
                # Force fetch recent data by requesting data up to today
                self.get_cached_data(symbol, end_date=date.today(), max_age_days=max_age)
                refresh_results[symbol] = True
                self.logger.info(f"Successfully refreshed cache for {symbol}")
            except Exception as e:
                self.logger.error(f"Failed to refresh cache for {symbol}: {e}")
                refresh_results[symbol] = False
        
        return refresh_results
