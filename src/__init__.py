"""
Bitcoin Strategy Backtester - Core Package
A comprehensive Python-based tool for backtesting Bitcoin trading strategies.
"""

__version__ = "1.0.0"
__author__ = "Jason"
__description__ = "A comprehensive Python-based tool for backtesting Bitcoin trading strategies"

# Import main components
from .data import YahooFetcher, OHLCVDatabase, CacheManager
from .utils.config import DATABASE_CONFIG, DEFAULT_SYMBOLS
from .visualization import OHLCVChart

__all__ = [
    'YahooFetcher',
    'OHLCVDatabase', 
    'CacheManager',
    'OHLCVChart',
    'DATABASE_CONFIG',
    'DEFAULT_SYMBOLS'
]
