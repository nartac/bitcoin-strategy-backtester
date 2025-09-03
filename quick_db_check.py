#!/usr/bin/env python3
"""
Quick Database Checker - Simple interface for common database queries
"""

import sys
from datetime import datetime, date, timedelta

# Add project root to path
sys.path.append('.')

from inspect_database import DatabaseInspector


def quick_check():
    """Interactive quick checker."""
    inspector = DatabaseInspector()
    
    print("🚀 QUICK DATABASE CHECKER")
    print("=" * 40)
    
    # Show available symbols
    print("\n📊 Available symbols:")
    symbols_info = inspector.db.get_symbols_info()
    for info in symbols_info:
        date_range = inspector.db.get_date_range(info.symbol)
        stats = inspector.db.get_data_stats(info.symbol)
        print(f"   {info.symbol:<8} - {stats['record_count']:>4} records ({date_range[0]} to {date_range[1]})")
    
    # Quick examples
    print(f"\n💡 EXAMPLES:")
    print(f"   python quick_db_check.py TSLA 2025-09-02")
    print(f"   python quick_db_check.py BTC-USD yesterday")
    print(f"   python quick_db_check.py AAPL today")
    print(f"   python quick_db_check.py SPY recent")


def main():
    """Main function for command line usage."""
    if len(sys.argv) < 2:
        quick_check()
        return
    
    symbol = sys.argv[1].upper()
    
    if len(sys.argv) < 3:
        # Show recent data
        inspector = DatabaseInspector()
        inspector.show_symbol_data(symbol, limit=5, tail=True)
        return
    
    date_arg = sys.argv[2].lower()
    
    # Parse date argument
    today = date.today()
    
    if date_arg == 'today':
        target_date = today
    elif date_arg == 'yesterday':
        target_date = today - timedelta(days=1)
    elif date_arg == 'recent':
        inspector = DatabaseInspector()
        inspector.show_symbol_data(symbol, limit=10, tail=True)
        return
    else:
        try:
            target_date = datetime.strptime(date_arg, '%Y-%m-%d').date()
        except ValueError:
            print(f"❌ Invalid date format: {date_arg}")
            print("   Use YYYY-MM-DD, 'today', 'yesterday', or 'recent'")
            return
    
    # Show data for specific date
    inspector = DatabaseInspector()
    inspector.show_specific_date(symbol, target_date.isoformat())


if __name__ == "__main__":
    main()
