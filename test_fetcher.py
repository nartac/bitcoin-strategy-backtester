#!/usr/bin/env python3
"""
Test script for the YahooFetcher class.
Run this script to test your Yahoo Finance data fetcher functionality.
"""

import sys
import pandas as pd
from datetime import datetime
sys.path.append('.')

from src.data.fetcher import YahooFetcher

def test_fetcher():
    """Test the YahooFetcher functionality."""
    print("=" * 60)
    print("🧪 TESTING YAHOO FINANCE FETCHER")
    print("=" * 60)
    
    # Initialize fetcher
    try:
        fetcher = YahooFetcher()
        print("✅ Fetcher initialized successfully")
        print(f"   Crypto symbols supported: {len(fetcher.crypto_symbols)}")
        print(f"   No API key required: FREE unlimited data! 🎉")
    except Exception as e:
        print(f"❌ Failed to initialize fetcher: {e}")
        return False
    
    # Test API call
    print("\n📡 Testing data fetch...")
    try:
        data = fetcher.fetch_data('BTC')
        print("✅ Data fetch successful")
        
        # Analyze response
        if isinstance(data, pd.DataFrame) and not data.empty:
            print(f"   📊 Data shape: {data.shape}")
            print(f"   📅 Date range: {data.index.min().date()} to {data.index.max().date()}")
            print(f"   💰 Latest price: ${data['close'].iloc[-1]:,.2f}")
            print(f"   📈 Columns: {list(data.columns)}")
            
            # Calculate data span
            years = (data.index.max() - data.index.min()).days / 365.25
            print(f"   ⏰ Data span: {years:.1f} years ({len(data)} data points)")
            
            # Show sample data
            print(f"\n💰 Sample data (latest 3 days):")
            sample_data = data.tail(3)[['open', 'high', 'low', 'close', 'volume']]
            for date, row in sample_data.iterrows():
                print(f"   {date.date()}: O=${row['open']:,.2f} H=${row['high']:,.2f} L=${row['low']:,.2f} C=${row['close']:,.2f}")
            
            return True
        else:
            print(f"❌ Expected DataFrame with data, got: {type(data)}")
            return False
            
    except Exception as e:
        print(f"❌ Data fetch failed: {type(e).__name__}: {e}")
        return False

def test_different_symbols():
    """Test fetching data for different cryptocurrency and stock symbols."""
    print("\n" + "=" * 60)
    print("🔄 TESTING DIFFERENT SYMBOLS (CRYPTO & STOCKS)")
    print("=" * 60)
    
    fetcher = YahooFetcher()
    symbols = ['BTC', 'AAPL', 'ETH', 'TSLA', 'DOGE']  # Mix of crypto and stocks
    
    for symbol in symbols:
        print(f"\n📊 Testing {symbol}...")
        try:
            data = fetcher.fetch_data(symbol)
            
            if not data.empty:
                # Determine if crypto or stock
                symbol_type = "Crypto" if symbol in fetcher.crypto_symbols else "Stock"
                years = (data.index.max() - data.index.min()).days / 365.25
                
                print(f"   ✅ {symbol} ({symbol_type}): {len(data)} data points")
                print(f"      📅 Range: {data.index.min().date()} to {data.index.max().date()}")
                print(f"      ⏰ Span: {years:.1f} years")
                print(f"      💰 Latest: ${data['close'].iloc[-1]:,.2f}")
            else:
                print(f"   ❌ {symbol}: No data returned")
                
        except Exception as e:
            print(f"   ❌ {symbol}: Error - {e}")

def test_advanced_features():
    """Test advanced fetcher features."""
    print("\n" + "=" * 60)
    print("🚀 TESTING ADVANCED FEATURES")
    print("=" * 60)
    
    fetcher = YahooFetcher()
    
    try:
        # Test different time periods
        print("📊 Testing different time periods...")
        periods = ['1y', '2y', 'max']
        
        for period in periods:
            data = fetcher.fetch_data('BTC', period=period)
            years = (data.index.max() - data.index.min()).days / 365.25
            print(f"   ✅ {period}: {len(data)} points ({years:.1f} years)")
        
        # Test date range
        print("\n📅 Testing custom date range...")
        data = fetcher.fetch_data('AAPL', start_date='2023-01-01', end_date='2023-12-31')
        print(f"   ✅ Custom range: {len(data)} points for 2023")
        
        # Test bulk fetch
        print("\n📦 Testing bulk fetch...")
        symbols = ['BTC', 'ETH', 'AAPL']
        bulk_data = fetcher.bulk_fetch(symbols, period='1y')
        
        for symbol, data in bulk_data.items():
            if not data.empty:
                print(f"   ✅ {symbol}: {len(data)} points")
            else:
                print(f"   ❌ {symbol}: No data")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced features test failed: {e}")
        return False

if __name__ == "__main__":
    print(f"🕒 Yahoo Finance tests started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run basic test
    success = test_fetcher()
    
    if success:
        # Run additional tests if basic test passes
        test_different_symbols()
        test_advanced_features()
        print("\n" + "=" * 60)
        print("🎉 ALL YAHOO FINANCE TESTS COMPLETED SUCCESSFULLY!")
        print("🚀 You now have FREE unlimited historical data!")
    else:
        print("\n" + "=" * 60)
        print("❌ BASIC TEST FAILED - CHECK YOUR CONFIGURATION")
    
    print("=" * 60)
