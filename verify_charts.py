#!/usr/bin/env python3
"""
Quick verification that the chart system is working properly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.visualization.chart_engine import OHLCVChart

def test_chart_system():
    """Test that the chart system is working."""
    print("🎯 Testing Bitcoin Strategy Backtester Chart System")
    print("=" * 50)
    
    try:
        # Test chart creation
        chart = OHLCVChart(symbol='BTC-USD')
        print("✅ Chart engine initialized successfully")
        
        # Test plotting and saving
        chart.plot(
            timeframe='1Y',
            style='candlestick',
            indicators='BOTH',
            volume='subplot',
            scale='linear'
        ).save('test_verification.png')
        
        print("✅ Chart plotted and saved successfully")
        print("📁 Check 'test_verification.png' in current directory")
        
        # Clean up
        chart.close()
        print("✅ Chart closed and memory cleaned up")
        
        print("\n🎉 CHART SYSTEM VERIFICATION COMPLETE!")
        print("🚀 Your advanced matplotlib charting system is ready to use!")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_chart_system()
    sys.exit(0 if success else 1)
