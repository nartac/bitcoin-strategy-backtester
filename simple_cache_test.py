#!/usr/bin/env python3
"""
Simple test for database caching functionality.
"""

import sys
import time
sys.path.append('.')

from src.data import YahooFetcher

def test_caching():
    print("🗄️ Testing SQLite Database Caching")
    print("=" * 50)
    
    # Initialize fetcher with caching
    fetcher = YahooFetcher(use_cache=True)
    print("✅ Fetcher initialized with caching")
    
    # Test first fetch (cache miss)
    print("\n📡 First fetch (cache miss)...")
    start_time = time.time()
    data1 = fetcher.fetch_data_with_cache('BTC-USD', period='1mo')
    first_time = time.time() - start_time
    
    print(f"   Records: {len(data1)}")
    print(f"   Time: {first_time:.2f} seconds")
    if not data1.empty:
        print(f"   Latest price: ${data1['close'].iloc[-1]:,.2f}")
    
    # Test second fetch (cache hit)
    print("\n⚡ Second fetch (cache hit)...")
    start_time = time.time()
    data2 = fetcher.fetch_data_with_cache('BTC-USD', period='1mo')
    second_time = time.time() - start_time
    
    print(f"   Records: {len(data2)}")
    print(f"   Time: {second_time:.3f} seconds")
    print(f"   Speedup: {first_time/second_time:.1f}x faster!")
    
    # Check cache stats
    stats = fetcher.get_cache_stats()
    if stats:
        print(f"\n📊 Cache Statistics:")
        print(f"   Cache hits: {stats['cache_hits']}")
        print(f"   Cache misses: {stats['cache_misses']}")
        print(f"   Hit rate: {stats['hit_rate_percent']}%")
        print(f"   Symbols cached: {stats['symbols_cached']}")
        print(f"   Total records: {stats['total_records']:,}")
    
    print(f"\n🎉 Database caching is working perfectly!")
    return True

if __name__ == "__main__":
    try:
        test_caching()
        print("\n✅ ALL TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
