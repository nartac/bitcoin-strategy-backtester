"""
Chart styling and themes for professional financial charts.
"""

import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.dates as mdates
from typing import Dict, Any

# Professional color palette
COLORS = {
    'primary': '#2E86C1',      # Professional blue
    'secondary': '#F39C12',     # Orange accent
    'success': '#27AE60',       # Green for gains
    'danger': '#E74C3C',        # Red for losses
    'warning': '#F39C12',       # Orange for warnings
    'info': '#3498DB',          # Light blue
    'dark': '#2C3E50',          # Dark grey
    'light': '#ECF0F1',         # Light grey
    'grid': '#BDC3C7',          # Grid color
    'text': '#2C3E50',          # Text color
    
    # Candlestick colors
    'bull': '#27AE60',          # Green for bullish candles
    'bear': '#E74C3C',          # Red for bearish candles
    
    # Moving average colors
    'ma50': '#F39C12',          # Orange for 50-day MA
    'ma200': '#8E44AD',         # Purple for 200-day MA
    
    # Volume colors
    'volume_up': '#27AE60',     # Green volume bars
    'volume_down': '#E74C3C',   # Red volume bars
    'volume_alpha': 0.3,        # Volume transparency
}

# Chart style configurations
CHART_STYLES = {
    'professional': {
        'figure.figsize': (12, 8),
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'axes.edgecolor': COLORS['grid'],
        'axes.linewidth': 0.8,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'axes.grid': True,
        'grid.color': COLORS['grid'],
        'grid.linestyle': '-',
        'grid.linewidth': 0.5,
        'grid.alpha': 0.3,  # Fixed: moved from axes.grid.alpha
        'axes.axisbelow': True,
        'font.size': 10,
        'font.family': 'sans-serif',
        'axes.titlesize': 14,
        'axes.labelsize': 11,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'legend.frameon': True,
        'legend.fancybox': True,
        'legend.shadow': True,
        'legend.framealpha': 0.9,
    },
    
    'dark': {
        'figure.figsize': (12, 8),
        'figure.facecolor': '#1E1E1E',
        'axes.facecolor': '#1E1E1E',
        'axes.edgecolor': '#404040',
        'axes.labelcolor': 'white',
        'text.color': 'white',
        'xtick.color': 'white',
        'ytick.color': 'white',
        'grid.color': '#404040',
        'grid.alpha': 0.3,
        'axes.spines.top': False,
        'axes.spines.right': False,
    }
}


class ChartStyler:
    """Manages chart styling and themes."""
    
    def __init__(self, style: str = 'professional'):
        """Initialize with specified style theme."""
        self.style = style
        self.colors = COLORS
        
    def apply_style(self) -> None:
        """Apply the chart style to matplotlib."""
        style_config = CHART_STYLES.get(self.style, CHART_STYLES['professional'])
        
        # Apply matplotlib rcParams
        for key, value in style_config.items():
            rcParams[key] = value
            
    def get_candlestick_colors(self) -> Dict[str, str]:
        """Get candlestick color configuration."""
        return {
            'up': self.colors['bull'],
            'down': self.colors['bear'],
            'wick_up': self.colors['bull'],
            'wick_down': self.colors['bear'],
        }
        
    def get_volume_colors(self) -> Dict[str, Any]:
        """Get volume bar color configuration."""
        return {
            'up': self.colors['volume_up'],
            'down': self.colors['volume_down'],
            'alpha': self.colors['volume_alpha'],
        }
        
    def get_ma_colors(self) -> Dict[str, str]:
        """Get moving average line colors."""
        return {
            'ma50': self.colors['ma50'],
            'ma200': self.colors['ma200'],
        }
        
    def format_price_axis(self, ax, symbol: str) -> None:
        """Format y-axis for price display."""
        # Determine if this is a crypto symbol
        is_crypto = any(crypto in symbol.upper() for crypto in ['BTC', 'ETH', 'DOGE', 'ADA', 'DOT'])
        
        if is_crypto or 'USD' in symbol:
            # Format as currency
            from matplotlib.ticker import FuncFormatter
            
            def currency_formatter(x, p):
                if x >= 1000:
                    return f'${x:,.0f}'
                elif x >= 1:
                    return f'${x:,.2f}'
                else:
                    return f'${x:.4f}'
                    
            ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
        else:
            # Format as regular number
            from matplotlib.ticker import FuncFormatter
            
            def number_formatter(x, p):
                if x >= 1000:
                    return f'{x:,.0f}'
                else:
                    return f'{x:,.2f}'
                    
            ax.yaxis.set_major_formatter(FuncFormatter(number_formatter))
            
    def format_date_axis(self, ax, timeframe: str) -> None:
        """Format x-axis for date display based on timeframe."""
        if timeframe in ['5D', '1M']:
            # Daily labels
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(ax.get_xticklabels()) // 10)))
        elif timeframe in ['3M', '6M']:
            # Weekly labels
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=max(1, len(ax.get_xticklabels()) // 8)))
        elif timeframe in ['YTD', '1Y']:
            # Monthly labels
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, len(ax.get_xticklabels()) // 6)))
        else:  # 5Y, MAX
            # Yearly labels
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.xaxis.set_major_locator(mdates.YearLocator())
            
        # Rotate labels to prevent overlap
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
    def create_figure(self, subplot_spec: tuple = None) -> tuple:
        """Create a properly styled figure and axes."""
        self.apply_style()
        
        if subplot_spec:
            fig, axes = plt.subplots(*subplot_spec, figsize=(12, 8 if subplot_spec[0] == 1 else 10))
            if subplot_spec[0] == 1:
                axes = [axes]
        else:
            fig, ax = plt.subplots(figsize=(12, 8))
            axes = ax
            
        return fig, axes
