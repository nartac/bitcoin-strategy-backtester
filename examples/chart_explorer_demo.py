#!/usr/bin/env python3
"""
Demo Script for Chart Explorer CLI
Shows the capabilities of the Chart Explorer without requiring interactive input.
"""

import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from chart_explorer import ChartExplorer

def demo_chart_explorer():
    """Demonstrate Chart Explorer capabilities."""
    print("🎬 CHART EXPLORER DEMO")
    print("=" * 50)
    
    explorer = ChartExplorer()
    
    # Demo configurations
    demo_configs = [
        {
            'symbol': 'BTC-USD',
            'timeframe': '1Y',
            'style': 'line',
            'scale': 'linear',
            'indicators': None,
            'volume': False,
            'output': None
        },
        {
            'symbol': 'TSLA',
            'timeframe': '6M',
            'style': 'candlestick',
            'scale': 'linear',
            'indicators': 'MA50',
            'volume': 'subplot',
            'output': None
        },
        {
            'symbol': 'AAPL',
            'timeframe': '5Y',
            'style': 'area',
            'scale': 'linear',
            'indicators': 'BOTH',
            'volume': False,
            'output': None
        }
    ]
    
    print(f"\n📊 Generating {len(demo_configs)} demo charts...")
    
    for i, config in enumerate(demo_configs, 1):
        print(f"\n--- Demo Chart {i}/{len(demo_configs)} ---")
        print(f"Configuration: {config['symbol']} - {config['timeframe']} - {config['style']}")
        
        try:
            success = explorer.create_chart(config)
            if success:
                print(f"✅ Demo chart {i} completed successfully!")
            else:
                print(f"❌ Demo chart {i} failed!")
        except Exception as e:
            print(f"❌ Error in demo chart {i}: {e}")
    
    print(f"\n🎉 Demo completed! Check examples/charts/ for generated charts.")
    print(f"\n💡 To use interactively, run: python chart_explorer.py")
    print(f"💡 For command line usage, run: python chart_explorer.py SYMBOL --options")

if __name__ == "__main__":
    demo_chart_explorer()
