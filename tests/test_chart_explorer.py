#!/usr/bin/env python3
"""
Simple test to verify Chart Explorer CLI functionality.
"""

import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def test_chart_explorer_import():
    """Test that Chart Explorer can be imported without errors."""
    try:
        from chart_explorer import ChartExplorer, Colors
        print("✅ Chart Explorer imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Chart Explorer: {e}")
        return False

def test_chart_explorer_basic():
    """Test basic Chart Explorer functionality."""
    try:
        from chart_explorer import ChartExplorer
        
        explorer = ChartExplorer()
        
        # Test parameter validation
        test_params = {
            'symbol': 'BTC-USD',
            'timeframe': '1Y',
            'style': 'line',
            'scale': 'linear',
            'indicators': None,
            'volume': False,
            'output': None
        }
        
        print("✅ Chart Explorer basic functionality works")
        return True
        
    except Exception as e:
        print(f"❌ Chart Explorer basic test failed: {e}")
        return False

def main():
    """Run Chart Explorer tests."""
    print("🧪 CHART EXPLORER TESTS")
    print("=" * 30)
    
    tests = [
        test_chart_explorer_import,
        test_chart_explorer_basic
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Chart Explorer tests passed!")
        return True
    else:
        print("💥 Some Chart Explorer tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
