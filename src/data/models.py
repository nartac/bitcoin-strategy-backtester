"""
Data models and validation for OHLCV storage.
Ensures data integrity and consistency for bitcoin-strategy-backtester.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
import pandas as pd


@dataclass
class SymbolInfo:
    """Metadata information for a trading symbol."""
    symbol: str
    name: Optional[str] = None
    asset_type: Optional[str] = None  # 'crypto', 'stock'
    exchange: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class OHLCVRecord:
    """Validated OHLCV data record with integrity checks."""
    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    dividends: float = 0.0
    stock_splits: float = 0.0
    
    def __post_init__(self):
        """Validate data integrity after initialization."""
        self.validate()
    
    def validate(self) -> bool:
        """
        Validate OHLCV data integrity.
        
        Returns:
            bool: True if all validations pass
            
        Raises:
            ValueError: If validation fails
        """
        errors = []
        
        # Price validations
        if self.high < self.low:
            errors.append(f"High ({self.high}) cannot be less than Low ({self.low})")
        
        if self.open < 0 or self.high < 0 or self.low < 0 or self.close < 0:
            errors.append("Prices cannot be negative")
            
        if not (self.low <= self.open <= self.high):
            errors.append(f"Open ({self.open}) must be between Low ({self.low}) and High ({self.high})")
            
        if not (self.low <= self.close <= self.high):
            errors.append(f"Close ({self.close}) must be between Low ({self.low}) and High ({self.high})")
        
        # Volume validation
        if self.volume < 0:
            errors.append("Volume cannot be negative")
        
        # Symbol validation
        if not self.symbol or not self.symbol.strip():
            errors.append("Symbol cannot be empty")
        
        if errors:
            raise ValueError(f"OHLCV validation failed for {self.symbol} on {self.date}: " + "; ".join(errors))
        
        return True
    
    @classmethod
    def from_pandas_row(cls, symbol: str, row: pd.Series) -> 'OHLCVRecord':
        """
        Create OHLCVRecord from pandas Series row.
        
        Args:
            symbol: Trading symbol
            row: Pandas Series with OHLCV data
            
        Returns:
            OHLCVRecord: Validated OHLCV record
        """
        # Handle different possible column names
        open_price = row.get('open', row.get('Open', 0))
        high_price = row.get('high', row.get('High', 0))
        low_price = row.get('low', row.get('Low', 0))
        close_price = row.get('close', row.get('Close', 0))
        volume = int(row.get('volume', row.get('Volume', 0)))
        dividends = float(row.get('dividends', row.get('Dividends', 0.0)))
        stock_splits = float(row.get('stock_splits', row.get('Stock Splits', 0.0)))
        
        # Convert index to date if it's a timestamp
        record_date = row.name
        if hasattr(record_date, 'date'):
            record_date = record_date.date()
        elif isinstance(record_date, str):
            record_date = datetime.strptime(record_date, '%Y-%m-%d').date()
        
        return cls(
            symbol=symbol,
            date=record_date,
            open=float(open_price),
            high=float(high_price),
            low=float(low_price),
            close=float(close_price),
            volume=volume,
            dividends=dividends,
            stock_splits=stock_splits
        )
    
    def to_dict(self) -> dict:
        """Convert record to dictionary for database storage."""
        return {
            'symbol': self.symbol,
            'date': self.date.isoformat(),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'dividends': self.dividends,
            'stock_splits': self.stock_splits
        }


class DataValidator:
    """Additional validation utilities for OHLCV data."""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, symbol: str) -> list:
        """
        Validate entire DataFrame of OHLCV data.
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol for validation
            
        Returns:
            list: List of validation errors (empty if all valid)
        """
        errors = []
        
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
            return errors
        
        # Check for any NaN values in critical columns
        for col in required_columns:
            if df[col].isna().any():
                nan_count = df[col].isna().sum()
                errors.append(f"Found {nan_count} NaN values in column '{col}'")
        
        # Check for duplicate dates
        if df.index.duplicated().any():
            duplicate_count = df.index.duplicated().sum()
            errors.append(f"Found {duplicate_count} duplicate dates")
        
        # Validate price relationships for each row
        invalid_highs = (df['high'] < df['low']).sum()
        if invalid_highs > 0:
            errors.append(f"Found {invalid_highs} rows where high < low")
        
        invalid_opens = ((df['open'] < df['low']) | (df['open'] > df['high'])).sum()
        if invalid_opens > 0:
            errors.append(f"Found {invalid_opens} rows where open is outside high-low range")
        
        invalid_closes = ((df['close'] < df['low']) | (df['close'] > df['high'])).sum()
        if invalid_closes > 0:
            errors.append(f"Found {invalid_closes} rows where close is outside high-low range")
        
        return errors
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean DataFrame by removing invalid data and filling gaps.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Remove rows with NaN in critical columns
        critical_columns = ['open', 'high', 'low', 'close', 'volume']
        df_clean = df_clean.dropna(subset=critical_columns)
        
        # Remove duplicate dates (keep last)
        df_clean = df_clean[~df_clean.index.duplicated(keep='last')]
        
        # Remove rows where high < low (data error)
        df_clean = df_clean[df_clean['high'] >= df_clean['low']]
        
        # Remove rows where open/close are outside high-low range
        valid_open = (df_clean['open'] >= df_clean['low']) & (df_clean['open'] <= df_clean['high'])
        valid_close = (df_clean['close'] >= df_clean['low']) & (df_clean['close'] <= df_clean['high'])
        df_clean = df_clean[valid_open & valid_close]
        
        # Fill missing dividends and stock_splits with 0
        df_clean['dividends'] = df_clean['dividends'].fillna(0.0)
        df_clean['stock_splits'] = df_clean['stock_splits'].fillna(0.0)
        
        return df_clean
