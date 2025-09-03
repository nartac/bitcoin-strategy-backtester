"""
Core matplotlib charting engine for OHLCV data visualization.
Advanced charting system with multiple display options and technical indicators.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List, Union, Tuple
import warnings

# Suppress tight_layout warnings for better user experience
warnings.filterwarnings('ignore', message='This figure includes Axes that are not compatible with tight_layout')

# Import project modules
from ..data.database import OHLCVDatabase
from ..data.cache_manager import CacheManager
from ..data.fetcher import YahooFetcher
from ..utils.config import DATABASE_CONFIG
from .styles import ChartStyler, COLORS
from .indicators import TechnicalIndicators, calculate_chart_indicators, prepare_volume_data
from .formatters import apply_chart_formatting

# Optional mplfinance for advanced candlestick charts
try:
    import mplfinance as mpf
    HAS_MPLFINANCE = True
except ImportError:
    HAS_MPLFINANCE = False
    warnings.warn("mplfinance not installed. Candlestick charts will use basic implementation.")


class OHLCVChart:
    """
    Advanced OHLCV chart with multiple display options.
    
    Features:
    - Multiple timeframes (5D, 1M, 3M, 6M, YTD, 1Y, 5Y, MAX)
    - Different chart styles (line, area, candlestick, OHLC)
    - Price scales (linear, logarithmic)
    - Technical indicators (moving averages)
    - Volume visualization (subplot or overlay)
    - Professional styling and formatting
    """
    
    def __init__(self, data_source: Union[OHLCVDatabase, str] = None, symbol: str = None):
        """
        Initialize chart with data source and symbol.
        
        Args:
            data_source: Database instance, database path, or None for default
            symbol: Trading symbol (e.g., 'BTC-USD', 'AAPL')
        """
        # Initialize data sources
        if isinstance(data_source, str):
            self.database = OHLCVDatabase(data_source)
        elif isinstance(data_source, OHLCVDatabase):
            self.database = data_source
        else:
            # Use default database
            db_path = DATABASE_CONFIG.get('db_path', 'data/ohlcv_data.db')
            self.database = OHLCVDatabase(db_path)
            
        # Initialize fetcher for missing data
        self.fetcher = YahooFetcher()
        self.cache_manager = CacheManager(self.database, self.fetcher)
        
        # Chart configuration
        self.symbol = symbol
        self.styler = ChartStyler()
        
        # Chart state
        self.figure = None
        self.axes = None
        self.data = None
        
    def plot(self, timeframe: str = '1Y', scale: str = 'linear', style: str = 'line',
             price_type: str = 'close', indicators: Optional[str] = None, 
             volume: Union[bool, str] = False, title: Optional[str] = None) -> 'OHLCVChart':
        """
        Create chart with specified parameters.
        
        Args:
            timeframe: '5D', '1M', '3M', '6M', 'YTD', '1Y', '5Y', 'MAX'
            scale: 'linear' or 'log'
            style: 'line', 'area', 'candlestick', 'ohlc'
            price_type: 'close' or 'adjusted'
            indicators: None, 'MA50', 'MA200', 'BOTH'
            volume: False, 'subplot', 'overlay'
            title: Custom chart title
            
        Returns:
            Self for method chaining
        """
        # Validate parameters
        self._validate_parameters(timeframe, scale, style, price_type, indicators, volume)
        
        # Get data for the specified timeframe
        self.data = self._get_data(timeframe, price_type)
        
        if self.data.empty:
            raise ValueError(f"No data available for symbol {self.symbol} and timeframe {timeframe}")
        
        # Create figure and axes
        subplot_count = 2 if volume == 'subplot' else 1
        height_ratios = [3, 1] if volume == 'subplot' else [1]
        
        self.figure, self.axes = plt.subplots(
            subplot_count, 1, 
            figsize=(12, 8 if subplot_count == 1 else 10),
            gridspec_kw={'height_ratios': height_ratios, 'hspace': 0.1} if subplot_count > 1 else {}
        )
        
        if subplot_count == 1:
            self.axes = [self.axes]
        
        # Apply styling
        self.styler.apply_style()
        
        # Plot main chart
        self._plot_main_chart(style, scale, indicators, volume)
        
        # Plot volume if requested
        if volume == 'subplot':
            self._plot_volume_subplot()
        elif volume == 'overlay':
            self._plot_volume_overlay()
        
        # Format axes and add labels
        self._format_chart(timeframe, title)
        
        return self
    
    def show(self) -> None:
        """Display the chart."""
        if self.figure:
            try:
                plt.tight_layout()
            except:
                # If tight_layout fails, use constrained layout
                try:
                    self.figure.set_layout_engine('constrained')
                except:
                    # If that fails too, just continue without layout adjustment
                    pass
            plt.show()
            # Clean up after showing
            plt.close(self.figure)
            self.figure = None
            self.axes = None
        else:
            raise ValueError("No chart to display. Call plot() first.")
    
    def close(self) -> None:
        """Close the current figure and free memory."""
        if self.figure:
            plt.close(self.figure)
            self.figure = None
            self.axes = None
    
    def save(self, filename: str, dpi: int = 300, format: str = 'png') -> None:
        """
        Save chart to file.
        
        Args:
            filename: Output filename
            dpi: Resolution for raster formats
            format: File format ('png', 'pdf', 'svg', 'jpg')
        """
        if self.figure:
            try:
                plt.tight_layout()
            except:
                # If tight_layout fails, use constrained layout or bbox_inches
                try:
                    self.figure.set_layout_engine('constrained')
                except:
                    # If constrained layout also fails, continue without layout adjustment
                    pass
            
            self.figure.savefig(filename, dpi=dpi, format=format, bbox_inches='tight')
            # Clean up memory
            plt.close(self.figure)
            self.figure = None
            self.axes = None
        else:
            raise ValueError("No chart to save. Call plot() first.")
    
    def _validate_parameters(self, timeframe: str, scale: str, style: str, 
                           price_type: str, indicators: Optional[str], volume: Union[bool, str]) -> None:
        """Validate chart parameters."""
        valid_timeframes = ['5D', '1M', '3M', '6M', 'YTD', '1Y', '5Y', 'MAX']
        valid_scales = ['linear', 'log']
        valid_styles = ['line', 'area', 'candlestick', 'ohlc']
        valid_price_types = ['close', 'adjusted']
        valid_indicators = [None, 'MA50', 'MA200', 'BOTH']
        valid_volume = [False, 'subplot', 'overlay']
        
        if timeframe not in valid_timeframes:
            raise ValueError(f"Invalid timeframe. Must be one of: {valid_timeframes}")
        if scale not in valid_scales:
            raise ValueError(f"Invalid scale. Must be one of: {valid_scales}")
        if style not in valid_styles:
            raise ValueError(f"Invalid style. Must be one of: {valid_styles}")
        if price_type not in valid_price_types:
            raise ValueError(f"Invalid price_type. Must be one of: {valid_price_types}")
        if indicators not in valid_indicators:
            raise ValueError(f"Invalid indicators. Must be one of: {valid_indicators}")
        if volume not in valid_volume:
            raise ValueError(f"Invalid volume. Must be one of: {valid_volume}")
        if not self.symbol:
            raise ValueError("Symbol must be specified")
    
    def _get_data(self, timeframe: str, price_type: str) -> pd.DataFrame:
        """Get data for the specified timeframe."""
        # Calculate date range based on timeframe
        end_date = date.today()
        
        if timeframe == '5D':
            start_date = end_date - timedelta(days=7)  # Extra days for weekends
        elif timeframe == '1M':
            start_date = end_date - timedelta(days=35)  # ~1 month with buffer
        elif timeframe == '3M':
            start_date = end_date - timedelta(days=95)  # ~3 months with buffer
        elif timeframe == '6M':
            start_date = end_date - timedelta(days=190)  # ~6 months with buffer
        elif timeframe == 'YTD':
            start_date = date(end_date.year, 1, 1)
        elif timeframe == '1Y':
            start_date = end_date - timedelta(days=370)  # ~1 year with buffer
        elif timeframe == '5Y':
            start_date = end_date - timedelta(days=1830)  # ~5 years with buffer
        else:  # MAX
            start_date = None
        
        # Get cached data with fallback to fetcher
        data = self.cache_manager.get_cached_data(
            self.symbol, 
            start_date=start_date, 
            end_date=end_date
        )
        
        if data.empty:
            # Try direct fetch if cache fails
            period_map = {
                '5D': '5d', '1M': '1mo', '3M': '3mo', '6M': '6mo',
                'YTD': 'ytd', '1Y': '1y', '5Y': '5y', 'MAX': 'max'
            }
            data = self.fetcher.fetch_data(self.symbol, period=period_map.get(timeframe, '1y'))
        
        # Handle adjusted vs regular close
        if price_type == 'adjusted' and 'adj_close' in data.columns:
            data['close'] = data['adj_close']
        
        return data
    
    def _plot_main_chart(self, style: str, scale: str, indicators: Optional[str], volume: Union[bool, str]) -> None:
        """Plot the main price chart."""
        ax = self.axes[0]
        
        if style == 'line':
            self._plot_line_chart(ax, scale)
        elif style == 'area':
            self._plot_area_chart(ax, scale)
        elif style == 'candlestick':
            self._plot_candlestick_chart(ax, scale)
        elif style == 'ohlc':
            self._plot_ohlc_chart(ax, scale)
        
        # Add indicators if requested
        if indicators:
            self._add_indicators(ax, indicators)
        
        # Set scale
        if scale == 'log':
            ax.set_yscale('log')
    
    def _plot_line_chart(self, ax, scale: str) -> None:
        """Plot line chart with proper spacing."""
        # Use sequential positioning to eliminate weekend gaps
        x_positions = range(len(self.data))
        ax.plot(x_positions, self.data['close'], 
                color=COLORS['primary'], linewidth=2, label='Close')
        
        # Set custom x-axis labels with proper date formatting
        self._set_sequential_x_axis(ax, x_positions)
    
    def _plot_area_chart(self, ax, scale: str) -> None:
        """Plot area chart with proper spacing."""
        # Use sequential positioning to eliminate weekend gaps
        x_positions = range(len(self.data))
        ax.fill_between(x_positions, self.data['close'], 
                       color=COLORS['primary'], alpha=0.3, label='Close')
        ax.plot(x_positions, self.data['close'], 
                color=COLORS['primary'], linewidth=2)
        
        # Set custom x-axis labels with proper date formatting
        self._set_sequential_x_axis(ax, x_positions)
    
    def _plot_candlestick_chart(self, ax, scale: str) -> None:
        """Plot candlestick chart."""
        if HAS_MPLFINANCE and len(self.data) > 1:
            # Use mplfinance for professional candlesticks
            self._plot_mplfinance_candlesticks(ax)
        else:
            # Fallback to manual candlestick implementation
            self._plot_manual_candlesticks(ax)
    
    def _plot_mplfinance_candlesticks(self, ax) -> None:
        """Use mplfinance for professional candlestick charts."""
        # This would require more complex integration with mplfinance
        # For now, fall back to manual implementation
        self._plot_manual_candlesticks(ax)
    
    def _plot_manual_candlesticks(self, ax) -> None:
        """Manual candlestick implementation with proper spacing."""
        # Use sequential positioning to eliminate weekend gaps
        for i, (idx, row) in enumerate(self.data.iterrows()):
            open_price = row['open']
            high_price = row['high']
            low_price = row['low'] 
            close_price = row['close']
            
            # Use sequential position instead of date
            x_pos = i
            
            # Determine candle color
            is_bullish = close_price >= open_price
            color = COLORS['bull'] if is_bullish else COLORS['bear']
            
            # Draw wick (high-low line)
            ax.plot([x_pos, x_pos], [low_price, high_price], 
                   color=color, linewidth=1, alpha=0.8)
            
            # Draw body (open-close rectangle)
            body_height = abs(close_price - open_price)
            body_bottom = min(open_price, close_price)
            
            if body_height > 0:
                rect = Rectangle((x_pos - 0.3, body_bottom),
                               0.6, body_height,
                               facecolor=color, edgecolor=color, alpha=0.8)
                ax.add_patch(rect)
            else:
                # Doji - draw horizontal line
                ax.plot([x_pos - 0.3, x_pos + 0.3], 
                       [close_price, close_price], color=color, linewidth=2)
        
        # Set custom x-axis labels with proper date formatting
        x_positions = range(len(self.data))
        self._set_sequential_x_axis(ax, x_positions)
    
    def _plot_ohlc_chart(self, ax, scale: str) -> None:
        """Plot OHLC bar chart with proper spacing."""
        for i, (idx, row) in enumerate(self.data.iterrows()):
            open_price = row['open']
            high_price = row['high']
            low_price = row['low']
            close_price = row['close']
            
            # Use sequential position instead of date
            x_pos = i
            
            # Determine bar color
            is_bullish = close_price >= open_price
            color = COLORS['bull'] if is_bullish else COLORS['bear']
            
            # Draw vertical line (high-low)
            ax.plot([x_pos, x_pos], [low_price, high_price], 
                   color=color, linewidth=2)
            
            # Draw open tick (left)
            ax.plot([x_pos - 0.3, x_pos], [open_price, open_price], 
                   color=color, linewidth=2)
            
            # Draw close tick (right)
            ax.plot([x_pos, x_pos + 0.3], [close_price, close_price], 
                   color=color, linewidth=2)
        
        # Set custom x-axis labels with proper date formatting
        x_positions = range(len(self.data))
        self._set_sequential_x_axis(ax, x_positions)
    
    def _set_sequential_x_axis(self, ax, x_positions) -> None:
        """Set x-axis to use sequential positioning with proper date labels."""
        # Set x-axis to show proper dates without gaps
        ax.set_xlim(-0.5, len(self.data) - 0.5)
        
        # Calculate how many labels to show based on data length
        max_labels = 8
        step = max(1, len(self.data) // max_labels)
        
        # Select positions and corresponding dates for labels
        label_positions = list(range(0, len(self.data), step))
        if label_positions[-1] != len(self.data) - 1:
            label_positions.append(len(self.data) - 1)
        
        label_dates = [self.data.index[i].strftime('%m/%d') for i in label_positions]
        
        # Set custom tick positions and labels
        ax.set_xticks(label_positions)
        ax.set_xticklabels(label_dates, rotation=45, ha='right')
        
        # Enable grid for better readability
        ax.grid(True, alpha=0.3)
    
    def _add_indicators(self, ax, indicators: str) -> None:
        """Add technical indicators to the chart."""
        indicator_data = calculate_chart_indicators(self.data, indicators)
        
        ma_colors = self.styler.get_ma_colors()
        # Calculate indicators with sequential x positions
        x_positions = list(range(len(self.data)))
        
        if 'MA50' in indicator_data:
            ax.plot(x_positions, indicator_data['MA50'], 
                   color=ma_colors['ma50'], linewidth=2, label='MA50', alpha=0.8)
        
        if 'MA200' in indicator_data:
            ax.plot(x_positions, indicator_data['MA200'], 
                   color=ma_colors['ma200'], linewidth=2, label='MA200', alpha=0.8)
    
    def _plot_volume_subplot(self) -> None:
        """Plot volume in separate subplot with proper spacing."""
        ax = self.axes[1]
        volume_up, volume_down = prepare_volume_data(self.data)
        
        # Use sequential positioning for volume bars
        x_positions = list(range(len(self.data)))
        
        # Plot volume bars
        ax.bar(x_positions, volume_up, color=COLORS['volume_up'], 
               alpha=COLORS['volume_alpha'], label='Volume Up')
        ax.bar(x_positions, volume_down, color=COLORS['volume_down'], 
               alpha=COLORS['volume_alpha'], label='Volume Down')
        
        # Apply same x-axis formatting
        self._set_sequential_x_axis(ax, x_positions)
    
    def _plot_volume_overlay(self) -> None:
        """Plot volume as overlay on main chart."""
        ax = self.axes[0]
        ax2 = ax.twinx()
        
        volume_up, volume_down = prepare_volume_data(self.data)
        
        # Plot volume bars on secondary axis
        ax2.bar(self.data.index, volume_up, color=COLORS['volume_up'], 
                alpha=0.2, label='Volume Up')
        ax2.bar(self.data.index, volume_down, color=COLORS['volume_down'], 
                alpha=0.2, label='Volume Down')
        
        # Format volume axis
        ax2.set_ylabel('Volume', fontsize=11)
        ax2.tick_params(axis='y', labelsize=10)
    
    def _format_chart(self, timeframe: str, title: Optional[str]) -> None:
        """Apply formatting to the chart."""
        # Note: Skip date formatting for main axis since we use sequential positioning
        # Format main price axis (without date formatting to preserve sequential positioning)
        if len(self.axes) > 1:
            # For volume axis, apply full formatting
            apply_chart_formatting(self.axes[1], self.symbol, self.data, timeframe, 'volume')
        
        # Apply only price formatting to main axis (skip date formatting)
        from .formatters import PriceAxisFormatter
        PriceAxisFormatter.format_price_axis(self.axes[0], self.symbol, self.data['close'])
        self.axes[0].set_ylabel('Price', fontsize=11)
        
        # Add grid to main axis
        self.axes[0].grid(True, alpha=0.3)
        self.axes[0].tick_params(axis='both', labelsize=10)
        
        # Add title
        if title:
            chart_title = title
        else:
            chart_title = f"{self.symbol} - {timeframe}"
        
        self.axes[0].set_title(chart_title, fontsize=14, fontweight='bold', pad=20)
        
        # Add legend
        if self.axes[0].get_legend_handles_labels()[0]:
            self.axes[0].legend(loc='upper left', framealpha=0.9)
        
        # Remove x-axis labels from main chart if volume subplot exists
        if len(self.axes) > 1:
            self.axes[0].set_xlabel('')
            plt.setp(self.axes[0].get_xticklabels(), visible=False)
            self.axes[1].set_xlabel('Date', fontsize=11)
        else:
            self.axes[0].set_xlabel('Date', fontsize=11)
