#!/usr/bin/env python3
"""
Quick Chart Test - Simple test for the charting system.
Demonstrates basic usage and verifies the system works.
"""

import sys
import os
from datetime import datetime

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if os.path.basename(current_dir) == 'examples':
    sys.path.insert(0, parent_dir)
else:
    sys.path.insert(0, '.')

from src.visualization import OHLCVChart


def quick_chart_test():
    """Quick test of chart functionality."""
    print("🚀 QUICK CHART TEST")
    print("=" * 40)
    
    try:
        # Test basic line chart
        print("📊 Creating basic Bitcoin line chart...")
        chart = OHLCVChart(symbol='BTC-USD')
        chart.plot().save('examples/charts/test_basic.png')
        print("✅ Basic chart saved successfully!")
        
        # Test advanced chart
        print("📈 Creating advanced TSLA candlestick chart...")
        chart = OHLCVChart(symbol='TSLA')
        chart.plot(
            timeframe='6M',
            style='candlestick', 
            indicators='MA50',
            volume='subplot'
        ).save('examples/charts/test_advanced.png')
        print("✅ Advanced chart saved successfully!")
        
        print("\n🎉 All tests passed! Charts saved in examples/charts/")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = quick_chart_test()
    exit(0 if success else 1)
