"""
Technical indicators for OHLCV data visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional


class TechnicalIndicators:
    """Calculate technical indicators for chart visualization."""
    
    @staticmethod
    def moving_average(data: pd.Series, window: int) -> pd.Series:
        """
        Calculate simple moving average.
        
        Args:
            data: Price series (typically close prices)
            window: Number of periods for the moving average
            
        Returns:
            Moving average series (NaN for insufficient data periods)
        """
        # Use min_periods=window to ensure proper MA calculation
        # This will return NaN for the first (window-1) periods
        return data.rolling(window=window, min_periods=window).mean()
    
    @staticmethod
    def exponential_moving_average(data: pd.Series, window: int) -> pd.Series:
        """
        Calculate exponential moving average.
        
        Args:
            data: Price series
            window: Number of periods for the EMA
            
        Returns:
            Exponential moving average series
        """
        return data.ewm(span=window).mean()
    
    @staticmethod
    def bollinger_bands(data: pd.Series, window: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            data: Price series
            window: Period for moving average and standard deviation
            std_dev: Number of standard deviations for bands
            
        Returns:
            Dictionary with upper, middle, and lower bands
        """
        sma = data.rolling(window=window).mean()
        std = data.rolling(window=window).std()
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
    
    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            data: Price series
            window: Period for RSI calculation
            
        Returns:
            RSI series
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            data: Price series
            fast: Fast EMA period
            slow: Slow EMA period  
            signal: Signal line EMA period
            
        Returns:
            Dictionary with MACD line, signal line, and histogram
        """
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def volume_profile(price_data: pd.Series, volume_data: pd.Series, bins: int = 50) -> Dict[str, np.ndarray]:
        """
        Calculate volume profile for the price range.
        
        Args:
            price_data: Price series (typically close prices)
            volume_data: Volume series
            bins: Number of price bins
            
        Returns:
            Dictionary with price levels and corresponding volumes
        """
        price_min, price_max = price_data.min(), price_data.max()
        price_bins = np.linspace(price_min, price_max, bins)
        
        # Digitize prices into bins
        price_bin_indices = np.digitize(price_data, price_bins)
        
        # Sum volume for each price bin
        volume_profile = np.zeros(len(price_bins))
        for i, bin_idx in enumerate(price_bin_indices):
            if 0 < bin_idx < len(volume_profile):
                volume_profile[bin_idx] += volume_data.iloc[i]
                
        return {
            'price_levels': price_bins,
            'volume_profile': volume_profile
        }


class VolumeIndicators:
    """Volume-based technical indicators."""
    
    @staticmethod
    def on_balance_volume(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        Calculate On-Balance Volume.
        
        Args:
            close: Closing prices
            volume: Volume data
            
        Returns:
            OBV series
        """
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
                
        return obv
    
    @staticmethod
    def volume_moving_average(volume: pd.Series, window: int = 20) -> pd.Series:
        """
        Calculate volume moving average.
        
        Args:
            volume: Volume series
            window: Moving average period
            
        Returns:
            Volume MA series
        """
        return volume.rolling(window=window).mean()
    
    @staticmethod
    def volume_rate_of_change(volume: pd.Series, period: int = 10) -> pd.Series:
        """
        Calculate Volume Rate of Change.
        
        Args:
            volume: Volume series
            period: Period for rate of change calculation
            
        Returns:
            Volume ROC series
        """
        return ((volume - volume.shift(period)) / volume.shift(period)) * 100


def calculate_chart_indicators(data: pd.DataFrame, indicators: str) -> Dict[str, pd.Series]:
    """
    Calculate indicators based on the indicators parameter.
    
    Args:
        data: OHLCV DataFrame
        indicators: Indicator specification ('MA50', 'MA200', 'BOTH', or None)
        
    Returns:
        Dictionary of calculated indicators
    """
    result = {}
    
    if indicators is None:
        return result
    
    close_prices = data['close']
    
    if indicators == 'MA50' or indicators == 'BOTH':
        result['MA50'] = TechnicalIndicators.moving_average(close_prices, 50)
    
    if indicators == 'MA200' or indicators == 'BOTH':
        result['MA200'] = TechnicalIndicators.moving_average(close_prices, 200)
        
    return result


def prepare_volume_data(data: pd.DataFrame, close_col: str = 'close', volume_col: str = 'volume') -> Tuple[pd.Series, pd.Series]:
    """
    Prepare volume data with up/down colors based on price movement.
    
    Args:
        data: OHLCV DataFrame
        close_col: Name of close price column
        volume_col: Name of volume column
        
    Returns:
        Tuple of (volume_up, volume_down) series for coloring
    """
    close = data[close_col]
    volume = data[volume_col]
    
    # Determine up/down days
    price_change = close.diff()
    
    volume_up = volume.where(price_change >= 0, 0)
    volume_down = volume.where(price_change < 0, 0)
    
    return volume_up, volume_down
