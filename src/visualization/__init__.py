"""
Visualization module for bitcoin-strategy-backtester.
Provides advanced matplotlib-based charting capabilities for OHLCV data.
"""

from .chart_engine import OHLCVChart
from .styles import ChartStyler, COLORS
from .indicators import TechnicalIndicators, VolumeIndicators
from .formatters import DateAxisFormatter, PriceAxisFormatter, VolumeAxisFormatter

__all__ = [
    'OHLCVChart',
    'ChartStyler', 
    'COLORS',
    'TechnicalIndicators',
    'VolumeIndicators',
    'DateAxisFormatter',
    'PriceAxisFormatter', 
    'VolumeAxisFormatter'
]

# Version info
__version__ = "1.0.0"
