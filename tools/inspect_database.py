#!/usr/bin/env python3
"""
Visual Database Inspector for OHLCV Data
Interactive tool to explore and visualize data stored in the SQLite database.
"""

import sys
import pandas as pd
import os
from datetime import datetime, date, timedelta
from tabulate import tabulate
import argparse

# Add project root to path (handle both direct execution and running from root)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if os.path.basename(current_dir) == 'tools':
    sys.path.insert(0, parent_dir)
else:
    sys.path.insert(0, '.')

from src.data.database import OHLCVDatabase
from src.utils.config import DATABASE_CONFIG


class DatabaseInspector:
    """Visual inspector for the OHLCV database."""
    
    def __init__(self):
        """Initialize database inspector."""
        self.db = OHLCVDatabase(DATABASE_CONFIG['db_path'])
        print(f"🗄️  Connected to database: {DATABASE_CONFIG['db_path']}")
    
    def list_symbols(self):
        """List all symbols in the database."""
        print("\n📊 SYMBOLS IN DATABASE")
        print("=" * 50)
        
        symbols_info = self.db.get_symbols_info()
        if not symbols_info:
            print("❌ No symbols found in database")
            return
        
        # Prepare data for table
        table_data = []
        for info in symbols_info:
            # Get date range for this symbol
            date_range = self.db.get_date_range(info.symbol)
            date_range_str = f"{date_range[0]} to {date_range[1]}" if date_range else "No data"
            
            # Get record count
            stats = self.db.get_data_stats(info.symbol)
            record_count = stats.get('record_count', 0)
            
            table_data.append([
                info.symbol,
                info.asset_type or 'Unknown',
                info.name or 'N/A',
                record_count,
                date_range_str,
                info.updated_at.strftime('%Y-%m-%d %H:%M') if info.updated_at else 'Never'
            ])
        
        headers = ['Symbol', 'Type', 'Name', 'Records', 'Date Range', 'Last Updated']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    def show_symbol_data(self, symbol: str, start_date: str = None, end_date: str = None, 
                        limit: int = 10, tail: bool = False):
        """
        Show data for a specific symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'TSLA', 'BTC-USD')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Number of records to show
            tail: Show last N records instead of first N
        """
        print(f"\n📈 DATA FOR {symbol.upper()}")
        print("=" * 60)
        
        # Parse dates
        start_dt = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        
        # Get data
        data = self.db.get_ohlcv_data(symbol, start_dt, end_dt)
        
        if data.empty:
            print(f"❌ No data found for {symbol}")
            return
        
        # Show summary
        print(f"📊 Total records: {len(data):,}")
        print(f"📅 Date range: {data.index.min().date()} to {data.index.max().date()}")
        print(f"💰 Price range: ${data['low'].min():.2f} - ${data['high'].max():.2f}")
        print(f"📈 Latest close: ${data['close'].iloc[-1]:.2f}")
        
        # Show sample data
        if tail:
            sample_data = data.tail(limit)
            print(f"\n🔍 LAST {limit} RECORDS:")
        else:
            sample_data = data.head(limit)
            print(f"\n🔍 FIRST {limit} RECORDS:")
        
        # Format data for display
        display_data = sample_data.copy()
        display_data.index = display_data.index.strftime('%Y-%m-%d')
        
        # Round numeric columns
        for col in ['open', 'high', 'low', 'close']:
            display_data[col] = display_data[col].round(2)
        
        display_data['volume'] = display_data['volume'].astype(int)
        
        # Create table
        table_data = []
        for idx, row in display_data.iterrows():
            table_data.append([
                idx,
                f"${row['open']:>8.2f}",
                f"${row['high']:>8.2f}",
                f"${row['low']:>8.2f}",
                f"${row['close']:>8.2f}",
                f"{row['volume']:>12,}",
                f"{row['dividends']:>6.2f}",
                f"{row['stock_splits']:>6.2f}"
            ])
        
        headers = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Splits']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    def show_specific_date(self, symbol: str, target_date: str):
        """
        Show data for a specific date.
        
        Args:
            symbol: Trading symbol
            target_date: Date to show (YYYY-MM-DD)
        """
        print(f"\n📅 DATA FOR {symbol.upper()} ON {target_date}")
        print("=" * 50)
        
        # Parse target date
        target_dt = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # Get data for just that date
        data = self.db.get_ohlcv_data(symbol, target_dt, target_dt)
        
        if data.empty:
            print(f"❌ No data found for {symbol} on {target_date}")
            
            # Check if symbol exists at all
            all_data = self.db.get_ohlcv_data(symbol)
            if all_data.empty:
                print(f"❌ Symbol {symbol} not found in database")
            else:
                date_range = self.db.get_date_range(symbol)
                print(f"📊 Available data range: {date_range[0]} to {date_range[1]}")
                
                # Find closest dates
                all_dates = all_data.index.date
                earlier_dates = [d for d in all_dates if d < target_dt]
                later_dates = [d for d in all_dates if d > target_dt]
                
                if earlier_dates:
                    closest_earlier = max(earlier_dates)
                    print(f"📅 Closest earlier date: {closest_earlier}")
                
                if later_dates:
                    closest_later = min(later_dates)
                    print(f"📅 Closest later date: {closest_later}")
            
            return
        
        # Show the data
        row = data.iloc[0]
        print(f"✅ Data found for {target_date}:")
        print(f"   💰 Open:      ${row['open']:>8.2f}")
        print(f"   📈 High:      ${row['high']:>8.2f}")
        print(f"   📉 Low:       ${row['low']:>8.2f}")
        print(f"   💼 Close:     ${row['close']:>8.2f}")
        print(f"   📊 Volume:    {row['volume']:>12,}")
        print(f"   💵 Dividends: ${row['dividends']:>8.2f}")
        print(f"   🔄 Splits:    {row['stock_splits']:>8.2f}")
        
        # Calculate daily stats
        daily_change = row['close'] - row['open']
        daily_change_pct = (daily_change / row['open']) * 100
        daily_range = row['high'] - row['low']
        daily_range_pct = (daily_range / row['open']) * 100
        
        print(f"\n📊 DAILY STATISTICS:")
        print(f"   📈 Daily Change: ${daily_change:>6.2f} ({daily_change_pct:>+6.2f}%)")
        print(f"   📏 Daily Range:  ${daily_range:>6.2f} ({daily_range_pct:>6.2f}%)")
    
    def search_dates_around(self, symbol: str, target_date: str, days_around: int = 5):
        """
        Show data around a specific date.
        
        Args:
            symbol: Trading symbol
            target_date: Center date (YYYY-MM-DD)
            days_around: Number of days before and after to show
        """
        target_dt = datetime.strptime(target_date, '%Y-%m-%d').date()
        start_dt = target_dt - timedelta(days=days_around)
        end_dt = target_dt + timedelta(days=days_around)
        
        print(f"\n📅 DATA FOR {symbol.upper()} AROUND {target_date}")
        print(f"   📊 Showing {days_around} days before and after")
        print("=" * 60)
        
        self.show_symbol_data(symbol, start_dt.isoformat(), end_dt.isoformat(), 
                            limit=days_around*2+1)


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Visual Database Inspector for OHLCV Data')
    parser.add_argument('--symbols', action='store_true', help='List all symbols in database')
    parser.add_argument('--symbol', type=str, help='Symbol to inspect (e.g., TSLA, BTC-USD)')
    parser.add_argument('--date', type=str, help='Specific date to show (YYYY-MM-DD)')
    parser.add_argument('--start', type=str, help='Start date for range (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='End date for range (YYYY-MM-DD)')
    parser.add_argument('--limit', type=int, default=10, help='Number of records to show')
    parser.add_argument('--tail', action='store_true', help='Show last N records instead of first N')
    parser.add_argument('--around', type=int, help='Show N days around the specified date')
    
    args = parser.parse_args()
    
    inspector = DatabaseInspector()
    
    if args.symbols:
        inspector.list_symbols()
    elif args.symbol:
        if args.date:
            if args.around:
                inspector.search_dates_around(args.symbol, args.date, args.around)
            else:
                inspector.show_specific_date(args.symbol, args.date)
        else:
            inspector.show_symbol_data(args.symbol, args.start, args.end, args.limit, args.tail)
    else:
        # Interactive mode
        print("🔍 INTERACTIVE DATABASE INSPECTOR")
        print("=" * 40)
        inspector.list_symbols()
        
        while True:
            print("\n" + "="*50)
            symbol = input("\n🔍 Enter symbol to inspect (or 'quit'): ").strip().upper()
            
            if symbol.lower() in ['quit', 'exit', 'q']:
                break
            
            if not symbol:
                continue
            
            # Check if specific date is requested
            date_input = input("📅 Enter specific date (YYYY-MM-DD) or press Enter for recent data: ").strip()
            
            if date_input:
                try:
                    # Validate date format
                    datetime.strptime(date_input, '%Y-%m-%d')
                    inspector.show_specific_date(symbol, date_input)
                except ValueError:
                    print("❌ Invalid date format. Use YYYY-MM-DD")
            else:
                inspector.show_symbol_data(symbol, limit=10, tail=True)


if __name__ == "__main__":
    main()
