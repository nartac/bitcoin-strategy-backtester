"""
SQLite database manager for OHLCV data storage.
Provides high-performance data persistence for backtesting.
"""

import sqlite3
import pandas as pd
import logging
from typing import Optional, List, Dict, Tuple, Union
from datetime import datetime, date, timedelta
from pathlib import Path
from contextlib import contextmanager

from .models import OHLCVRecord, SymbolInfo, DataValidator


class OHLCVDatabase:
    """
    High-performance SQLite database manager for OHLCV data storage.
    
    Features:
    - Optimized schema with proper indexing
    - Data integrity validation
    - Efficient batch operations
    - Intelligent duplicate handling
    - Query optimization for backtesting
    """
    
    def __init__(self, db_path: str = "data/ohlcv_data.db"):
        """
        Initialize database with optimized settings.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with optimized settings."""
        with self.get_connection() as conn:
            # Enable WAL mode for better performance
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            
            # Create schema if it doesn't exist
            self.create_schema(conn)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic closing."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        try:
            yield conn
        finally:
            conn.close()
    
    def create_schema(self, conn: Optional[sqlite3.Connection] = None):
        """
        Create optimized database schema.
        
        Args:
            conn: Optional database connection (creates new if None)
        """
        schema_sql = """
        -- Table: symbols (metadata for tracked assets)
        CREATE TABLE IF NOT EXISTS symbols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            name TEXT,
            asset_type TEXT, -- 'crypto', 'stock'
            exchange TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Table: ohlcv_data (main price data storage)
        CREATE TABLE IF NOT EXISTS ohlcv_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol_id INTEGER NOT NULL,
            date DATE NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER NOT NULL,
            dividends REAL DEFAULT 0,
            stock_splits REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol_id) REFERENCES symbols(id),
            UNIQUE(symbol_id, date)
        );

        -- Indexes for query performance
        CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_date ON ohlcv_data(symbol_id, date);
        CREATE INDEX IF NOT EXISTS idx_ohlcv_date ON ohlcv_data(date);
        CREATE INDEX IF NOT EXISTS idx_symbols_symbol ON symbols(symbol);
        
        -- Trigger to update symbol updated_at timestamp
        CREATE TRIGGER IF NOT EXISTS update_symbol_timestamp 
        AFTER INSERT ON ohlcv_data
        BEGIN
            UPDATE symbols SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.symbol_id;
        END;
        """
        
        if conn is None:
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
                conn.commit()
        else:
            conn.executescript(schema_sql)
            conn.commit()
    
    def add_symbol(self, symbol: str, asset_type: str = None, name: str = None, exchange: str = None) -> int:
        """
        Add or update symbol metadata.
        
        Args:
            symbol: Trading symbol (e.g., 'BTC-USD', 'AAPL')
            asset_type: Type of asset ('crypto', 'stock')
            name: Human-readable name
            exchange: Exchange name
            
        Returns:
            int: Symbol ID
        """
        with self.get_connection() as conn:
            # Try to get existing symbol
            cursor = conn.execute("SELECT id FROM symbols WHERE symbol = ?", (symbol,))
            result = cursor.fetchone()
            
            if result:
                # Update existing symbol
                symbol_id = result[0]
                conn.execute("""
                    UPDATE symbols 
                    SET name = COALESCE(?, name),
                        asset_type = COALESCE(?, asset_type),
                        exchange = COALESCE(?, exchange),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (name, asset_type, exchange, symbol_id))
                
                self.logger.debug(f"Updated symbol {symbol} with ID {symbol_id}")
            else:
                # Insert new symbol
                cursor = conn.execute("""
                    INSERT INTO symbols (symbol, name, asset_type, exchange)
                    VALUES (?, ?, ?, ?)
                """, (symbol, name, asset_type, exchange))
                symbol_id = cursor.lastrowid
                
                self.logger.info(f"Added new symbol {symbol} with ID {symbol_id}")
            
            conn.commit()
            return symbol_id
    
    def get_symbol_id(self, symbol: str) -> Optional[int]:
        """Get symbol ID, adding symbol if it doesn't exist."""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT id FROM symbols WHERE symbol = ?", (symbol,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                # Add symbol with auto-detection of type
                asset_type = 'crypto' if any(crypto in symbol.upper() for crypto in ['BTC', 'ETH', 'DOGE']) else 'stock'
                return self.add_symbol(symbol, asset_type=asset_type)
    
    def store_ohlcv_data(self, symbol: str, data: pd.DataFrame, validate: bool = True) -> int:
        """
        Store OHLCV data with duplicate prevention.
        
        Args:
            symbol: Trading symbol
            data: DataFrame with OHLCV data (date index)
            validate: Whether to validate data before storing
            
        Returns:
            int: Number of records stored
        """
        if data.empty:
            self.logger.warning(f"No data to store for symbol {symbol}")
            return 0
        
        # Validate data if requested
        if validate:
            errors = DataValidator.validate_dataframe(data, symbol)
            if errors:
                self.logger.warning(f"Data validation warnings for {symbol}: {errors}")
                data = DataValidator.clean_dataframe(data)
                self.logger.info(f"Cleaned data for {symbol}, {len(data)} records remaining")
        
        # Get or create symbol ID
        symbol_id = self.get_symbol_id(symbol)
        
        # Prepare data for insertion
        records = []
        for date_index, row in data.iterrows():
            try:
                record = OHLCVRecord.from_pandas_row(symbol, row)
                records.append((
                    symbol_id,
                    record.date.isoformat(),
                    record.open,
                    record.high,
                    record.low,
                    record.close,
                    record.volume,
                    record.dividends,
                    record.stock_splits
                ))
            except ValueError as e:
                self.logger.warning(f"Skipping invalid record for {symbol} on {date_index}: {e}")
                continue
        
        if not records:
            self.logger.warning(f"No valid records to store for symbol {symbol}")
            return 0
        
        # Batch insert with IGNORE for duplicate handling
        with self.get_connection() as conn:
            cursor = conn.executemany("""
                INSERT OR IGNORE INTO ohlcv_data 
                (symbol_id, date, open, high, low, close, volume, dividends, stock_splits)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)
            
            rows_affected = cursor.rowcount
            conn.commit()
            
            self.logger.info(f"Stored {rows_affected} new records for {symbol} (attempted {len(records)})")
            return rows_affected
    
    def get_ohlcv_data(self, symbol: str, start_date: date = None, end_date: date = None) -> pd.DataFrame:
        """
        Retrieve OHLCV data with optimized queries.
        
        Args:
            symbol: Trading symbol
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            pd.DataFrame: OHLCV data with date index
        """
        with self.get_connection() as conn:
            # Build query with optional date filtering
            query = """
                SELECT o.date, o.open, o.high, o.low, o.close, o.volume, 
                       o.dividends, o.stock_splits
                FROM ohlcv_data o
                JOIN symbols s ON o.symbol_id = s.id
                WHERE s.symbol = ?
            """
            params = [symbol]
            
            if start_date:
                query += " AND o.date >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND o.date <= ?"
                params.append(end_date.isoformat())
            
            query += " ORDER BY o.date"
            
            # Execute query and create DataFrame
            df = pd.read_sql_query(query, conn, params=params, parse_dates=['date'], index_col='date')
            
            self.logger.debug(f"Retrieved {len(df)} records for {symbol}")
            return df
    
    def get_date_range(self, symbol: str) -> Optional[Tuple[date, date]]:
        """
        Get earliest and latest dates for symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Tuple[date, date]: (earliest_date, latest_date) or None if no data
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT MIN(o.date), MAX(o.date)
                FROM ohlcv_data o
                JOIN symbols s ON o.symbol_id = s.id
                WHERE s.symbol = ?
            """, (symbol,))
            
            result = cursor.fetchone()
            if result and result[0] and result[1]:
                min_date = datetime.fromisoformat(result[0]).date()
                max_date = datetime.fromisoformat(result[1]).date()
                return (min_date, max_date)
            
            return None
    
    def get_missing_dates(self, symbol: str, start_date: date, end_date: date) -> List[date]:
        """
        Identify missing dates for intelligent fetching.
        
        Args:
            symbol: Trading symbol
            start_date: Start date to check
            end_date: End date to check
            
        Returns:
            List[date]: List of missing dates
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT o.date
                FROM ohlcv_data o
                JOIN symbols s ON o.symbol_id = s.id
                WHERE s.symbol = ? AND o.date BETWEEN ? AND ?
                ORDER BY o.date
            """, (symbol, start_date.isoformat(), end_date.isoformat()))
            
            existing_dates = {datetime.fromisoformat(row[0]).date() for row in cursor.fetchall()}
        
        # Generate all dates in range (excluding weekends for stocks)
        all_dates = []
        current_date = start_date
        while current_date <= end_date:
            all_dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Find missing dates
        missing_dates = [d for d in all_dates if d not in existing_dates]
        
        self.logger.debug(f"Found {len(missing_dates)} missing dates for {symbol}")
        return missing_dates
    
    def get_symbols_info(self) -> List[SymbolInfo]:
        """Get information about all tracked symbols."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT symbol, name, asset_type, exchange, created_at, updated_at
                FROM symbols
                ORDER BY symbol
            """)
            
            symbols = []
            for row in cursor.fetchall():
                symbols.append(SymbolInfo(
                    symbol=row[0],
                    name=row[1],
                    asset_type=row[2],
                    exchange=row[3],
                    created_at=datetime.fromisoformat(row[4]) if row[4] else None,
                    updated_at=datetime.fromisoformat(row[5]) if row[5] else None
                ))
            
            return symbols
    
    def get_data_stats(self, symbol: str = None) -> Dict:
        """
        Get database statistics.
        
        Args:
            symbol: Optional symbol to get stats for (all symbols if None)
            
        Returns:
            Dict: Database statistics
        """
        with self.get_connection() as conn:
            if symbol:
                cursor = conn.execute("""
                    SELECT COUNT(*) as record_count,
                           MIN(o.date) as earliest_date,
                           MAX(o.date) as latest_date
                    FROM ohlcv_data o
                    JOIN symbols s ON o.symbol_id = s.id
                    WHERE s.symbol = ?
                """, (symbol,))
                
                result = cursor.fetchone()
                return {
                    'symbol': symbol,
                    'record_count': result[0],
                    'earliest_date': result[1],
                    'latest_date': result[2]
                }
            else:
                # Overall stats
                cursor = conn.execute("""
                    SELECT 
                        COUNT(DISTINCT s.symbol) as symbol_count,
                        COUNT(o.id) as total_records,
                        MIN(o.date) as earliest_date,
                        MAX(o.date) as latest_date
                    FROM ohlcv_data o
                    JOIN symbols s ON o.symbol_id = s.id
                """)
                
                result = cursor.fetchone()
                return {
                    'symbol_count': result[0],
                    'total_records': result[1],
                    'earliest_date': result[2],
                    'latest_date': result[3]
                }
    
    def vacuum_database(self):
        """Optimize database by running VACUUM."""
        with self.get_connection() as conn:
            conn.execute("VACUUM")
            self.logger.info("Database VACUUM completed")
    
    def delete_symbol_data(self, symbol: str) -> int:
        """
        Delete all data for a symbol.
        
        Args:
            symbol: Symbol to delete
            
        Returns:
            int: Number of records deleted
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM ohlcv_data 
                WHERE symbol_id IN (
                    SELECT id FROM symbols WHERE symbol = ?
                )
            """, (symbol,))
            
            deleted_count = cursor.rowcount
            
            # Also delete the symbol metadata
            conn.execute("DELETE FROM symbols WHERE symbol = ?", (symbol,))
            
            conn.commit()
            self.logger.info(f"Deleted {deleted_count} records for symbol {symbol}")
            return deleted_count
