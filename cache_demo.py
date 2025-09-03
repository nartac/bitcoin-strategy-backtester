#!/usr/bin/env python3
"""
Cache Expiry System Summary & Demo
==================================

This script demonstrates the cache expiry functionality implemented in the 
Bitcoin Strategy Backtester project.

Key Features:
1. Automatic cache expiry based on configurable max_age_days
2. Smart data refresh - only fetches missing/stale portions, not entire datasets
3. Cache freshness monitoring and management
4. Integration with Chart Explorer CLI for easy cache management

Usage Examples:
  python chart_explorer.py --cache-status        # Show all cache status
  python chart_explorer.py --cache-refresh       # Refresh stale caches
  python chart_explorer.py --cache-info BTC-USD  # Show specific cache info
"""

import sys
import os
from datetime import date, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.cache_manager import CacheManager

def demo_cache_expiry():
    """Demonstrate cache expiry functionality."""
    
    print("🎯 CACHE EXPIRY SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Create cache managers with different max_age settings
    cache_fresh = CacheManager(max_age_days=7)   # 7 days - more lenient
    cache_strict = CacheManager(max_age_days=1)  # 1 day - very strict
    
    print(f"\n📅 Today's date: {date.today()}")
    print(f"🔧 Testing with max_age settings: 7 days vs 1 day")
    
    # Test symbol
    symbol = "BTC-USD"
    
    print(f"\n🔍 CACHE ANALYSIS FOR {symbol}")
    print("-" * 40)
    
    # Check cache info with lenient setting
    info_fresh = cache_fresh.get_symbol_cache_info(symbol)
    if info_fresh['date_range']:
        start_date, end_date = info_fresh['date_range']
        print(f"📊 Data Range: {start_date} to {end_date}")
        print(f"📈 Records: {info_fresh['record_count']:,}")
        print(f"⏰ Cache Age: {info_fresh['cache_age_days']} days")
        print(f"")
        print(f"✅ Lenient (7 days): {'Fresh' if info_fresh['is_fresh'] else 'Stale'}")
        
        # Check with strict setting
        info_strict = cache_strict.get_symbol_cache_info(symbol)
        print(f"❌ Strict (1 day): {'Fresh' if info_strict['is_fresh'] else 'Stale'}")
        
        print(f"\n💡 KEY INSIGHTS:")
        print(f"   • Cache expiry is configurable per CacheManager instance")
        print(f"   • Same data can be 'fresh' or 'stale' depending on requirements")
        print(f"   • When cache is stale, system automatically fetches recent data")
        print(f"   • Only missing/recent data is fetched, not entire dataset")
        
    else:
        print(f"📂 No cached data found for {symbol}")
        print(f"💡 Generate a chart first: python chart_explorer.py {symbol}")
    
    print(f"\n🛠️  CACHE MANAGEMENT COMMANDS:")
    print(f"   python chart_explorer.py --cache-status")
    print(f"   python chart_explorer.py --cache-refresh")
    print(f"   python chart_explorer.py --cache-info {symbol}")
    
    print(f"\n✨ HOW CACHE EXPIRY WORKS:")
    print(f"   1. When data is requested, system checks cache age")
    print(f"   2. If cache_age_days > max_age_days, cache is 'stale'")
    print(f"   3. For stale cache, system fetches recent data to fill gap")
    print(f"   4. Only the missing portion is fetched (efficient!)")
    print(f"   5. Old data is preserved, recent data is added")
    
    print(f"\n🎯 EXPIRY LOGIC IN ACTION:")
    print(f"   • Today: {date.today()}")
    print(f"   • Latest cached data: {end_date if info_fresh['date_range'] else 'None'}")
    
    if info_fresh['date_range']:
        gap_days = (date.today() - end_date).days
        print(f"   • Gap: {gap_days} days")
        print(f"   • Max allowed gap (lenient): {cache_fresh.max_age_days} days")
        print(f"   • Max allowed gap (strict): {cache_strict.max_age_days} days")
        
        if gap_days > cache_strict.max_age_days:
            print(f"   → Strict setting would trigger refresh")
        if gap_days > cache_fresh.max_age_days:
            print(f"   → Lenient setting would also trigger refresh")
        else:
            print(f"   → Lenient setting considers cache fresh")

if __name__ == "__main__":
    demo_cache_expiry()
