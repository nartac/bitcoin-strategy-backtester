"""
Axis formatting utilities for financial charts.
"""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


class DateAxisFormatter:
    """Handles intelligent date axis formatting."""
    
    @staticmethod
    def format_date_axis(ax, data_index: pd.DatetimeIndex, timeframe: str) -> None:
        """
        Format x-axis dates based on timeframe and data density.
        
        Args:
            ax: Matplotlib axes object
            data_index: DateTime index of the data
            timeframe: Timeframe string ('5D', '1M', '3M', '6M', 'YTD', '1Y', '5Y', 'MAX')
        """
        # Calculate data span
        data_span = (data_index.max() - data_index.min()).days
        data_points = len(data_index)
        
        # Determine appropriate formatting based on timeframe and data density
        if timeframe in ['5D', '1M'] or data_span <= 31:
            # Daily labels for short timeframes
            if data_points <= 10:
                # Few points - show all dates
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            elif data_points <= 31:
                # Weekly intervals for month view
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            else:
                # Every few days to avoid crowding
                interval = max(1, data_points // 10)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
                
        elif timeframe in ['3M', '6M'] or data_span <= 183:
            # Weekly/bi-weekly labels for medium timeframes
            if data_span <= 90:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
                
        elif timeframe in ['YTD', '1Y'] or data_span <= 365:
            # Monthly labels for yearly view
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, data_span // 365 + 1)))
            
        elif timeframe == '5Y' or data_span <= 1825:
            # Quarterly or semi-annual labels
            if data_span <= 730:  # 2 years
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
                
        else:  # MAX or very long timeframes
            # Yearly labels for maximum data
            if data_span <= 3650:  # 10 years
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                ax.xaxis.set_major_locator(mdates.YearLocator())
            else:  # More than 10 years
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                # Fix: YearLocator doesn't accept interval parameter
                ax.xaxis.set_major_locator(mdates.YearLocator())
        
        # Rotate labels to prevent overlap
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Add minor ticks for better granularity
        if timeframe in ['5D', '1M']:
            ax.xaxis.set_minor_locator(mdates.DayLocator())
        elif timeframe in ['3M', '6M']:
            ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
        else:
            ax.xaxis.set_minor_locator(mdates.MonthLocator())


class PriceAxisFormatter:
    """Handles intelligent price axis formatting."""
    
    @staticmethod
    def format_price_axis(ax, symbol: str, price_data: pd.Series) -> None:
        """
        Format y-axis for price display with appropriate currency/number formatting.
        
        Args:
            ax: Matplotlib axes object
            symbol: Trading symbol (e.g., 'BTC-USD', 'AAPL')
            price_data: Series of price data to determine formatting
        """
        # Analyze price range
        price_min, price_max = price_data.min(), price_data.max()
        price_range = price_max - price_min
        
        # Determine if this is a crypto symbol
        crypto_indicators = ['BTC', 'ETH', 'DOGE', 'ADA', 'DOT', 'LINK', 'UNI', 'MATIC', 'SOL', 'AVAX']
        is_crypto = any(crypto in symbol.upper() for crypto in crypto_indicators) or 'USD' in symbol
        
        # Create appropriate formatter based on price range and symbol type
        if is_crypto or 'USD' in symbol or '$' in symbol:
            formatter = PriceAxisFormatter._create_currency_formatter(price_min, price_max)
        else:
            formatter = PriceAxisFormatter._create_number_formatter(price_min, price_max)
            
        ax.yaxis.set_major_formatter(formatter)
        
        # Set appropriate number of ticks
        num_ticks = min(8, max(4, int(price_range / (price_max * 0.05))))  # 5% increments as baseline
        ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=num_ticks, prune='both'))
    
    @staticmethod
    def _create_currency_formatter(price_min: float, price_max: float) -> FuncFormatter:
        """Create currency formatter based on price range."""
        
        def currency_formatter(x, p):
            if x == 0:
                return '$0'
            elif abs(x) >= 1000000:
                return f'${x/1000000:.1f}M'
            elif abs(x) >= 1000:
                return f'${x:,.0f}'
            elif abs(x) >= 1:
                if price_max < 100:
                    return f'${x:.2f}'
                else:
                    return f'${x:,.2f}'
            elif abs(x) >= 0.01:
                return f'${x:.4f}'
            else:
                return f'${x:.6f}'
                
        return FuncFormatter(currency_formatter)
    
    @staticmethod
    def _create_number_formatter(price_min: float, price_max: float) -> FuncFormatter:
        """Create number formatter for non-currency symbols."""
        
        def number_formatter(x, p):
            if x == 0:
                return '0'
            elif abs(x) >= 1000000:
                return f'{x/1000000:.1f}M'
            elif abs(x) >= 1000:
                return f'{x:,.0f}'
            elif abs(x) >= 1:
                return f'{x:,.2f}'
            else:
                return f'{x:.4f}'
                
        return FuncFormatter(number_formatter)


class VolumeAxisFormatter:
    """Handles volume axis formatting."""
    
    @staticmethod
    def format_volume_axis(ax, volume_data: pd.Series) -> None:
        """
        Format volume axis with appropriate scaling.
        
        Args:
            ax: Matplotlib axes object
            volume_data: Series of volume data
        """
        volume_max = volume_data.max()
        
        def volume_formatter(x, p):
            if x == 0:
                return '0'
            elif abs(x) >= 1e9:
                return f'{x/1e9:.1f}B'
            elif abs(x) >= 1e6:
                return f'{x/1e6:.1f}M'
            elif abs(x) >= 1e3:
                return f'{x/1e3:.1f}K'
            else:
                return f'{x:.0f}'
                
        ax.yaxis.set_major_formatter(FuncFormatter(volume_formatter))
        ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=4, prune='both'))


def apply_chart_formatting(ax, symbol: str, data: pd.DataFrame, timeframe: str, 
                         chart_type: str = 'price') -> None:
    """
    Apply comprehensive formatting to a chart axis.
    
    Args:
        ax: Matplotlib axes object
        symbol: Trading symbol
        data: OHLCV DataFrame
        timeframe: Timeframe string
        chart_type: Type of chart ('price' or 'volume')
    """
    # Format date axis
    DateAxisFormatter.format_date_axis(ax, data.index, timeframe)
    
    # Format appropriate y-axis
    if chart_type == 'volume':
        VolumeAxisFormatter.format_volume_axis(ax, data['volume'])
        ax.set_ylabel('Volume', fontsize=11)
    else:
        PriceAxisFormatter.format_price_axis(ax, symbol, data['close'])
        ax.set_ylabel('Price', fontsize=11)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
