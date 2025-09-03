#!/usr/bin/env python3
"""
Chart Examples - Comprehensive demonstration of the charting system.
Shows various chart styles, timeframes, and technical indicators.
"""

import sys
import os
from datetime import datetime

# Add project root to path (handle both direct execution and running from root)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if os.path.basename(current_dir) == 'examples':
    sys.path.insert(0, parent_dir)
else:
    sys.path.insert(0, '.')

from src.visualization import OHLCVChart
from src.data.database import OHLCVDatabase
from src.utils.config import DATABASE_CONFIG, DEFAULT_SYMBOLS


def demo_basic_charts():
    """Demonstrate basic chart functionality."""
    print("📊 BASIC CHART EXAMPLES")
    print("=" * 50)
    
    # Initialize chart with default database
    db_path = DATABASE_CONFIG.get('db_path', 'data/ohlcv_data.db')
    db = OHLCVDatabase(db_path)
    
    symbols_to_demo = ['BTC-USD', 'AAPL', 'TSLA']
    
    for symbol in symbols_to_demo:
        print(f"\n📈 Creating charts for {symbol}...")
        
        try:
            chart = OHLCVChart(db, symbol)
            
            # 1. Basic line chart (default)
            print(f"   ✅ Line chart (1Y default)")
            chart.plot().save(f'examples/charts/{symbol}_line_1y.png')
            
            # 2. Area chart with 6M timeframe
            print(f"   ✅ Area chart (6M)")
            chart.plot(timeframe='6M', style='area').save(f'examples/charts/{symbol}_area_6m.png')
            
            # 3. Candlestick with moving averages
            print(f"   ✅ Candlestick with MA indicators")
            chart.plot(style='candlestick', indicators='BOTH', volume='subplot').save(f'examples/charts/{symbol}_candlestick_ma.png')
            
        except Exception as e:
            print(f"   ❌ Error creating charts for {symbol}: {e}")


def demo_timeframes():
    """Demonstrate different timeframes."""
    print("\n⏱️ TIMEFRAME EXAMPLES")
    print("=" * 50)
    
    symbol = 'BTC-USD'  # Use Bitcoin for timeframe demo
    chart = OHLCVChart(symbol=symbol)
    
    timeframes = ['5D', '1M', '3M', '6M', 'YTD', '1Y', '5Y', 'MAX']
    
    for tf in timeframes:
        try:
            print(f"   📅 {tf} timeframe...")
            chart.plot(timeframe=tf, title=f'{symbol} - {tf} Timeframe').save(f'examples/charts/BTC_timeframe_{tf}.png')
            print(f"   ✅ Saved BTC_timeframe_{tf}.png")
        except Exception as e:
            print(f"   ❌ Error with {tf} timeframe: {e}")


def demo_chart_styles():
    """Demonstrate different chart styles."""
    print("\n🎨 CHART STYLE EXAMPLES")  
    print("=" * 50)
    
    symbol = 'TSLA'  # Use Tesla for style demo
    chart = OHLCVChart(symbol=symbol)
    
    styles = ['line', 'area', 'candlestick', 'ohlc']
    
    for style in styles:
        try:
            print(f"   🎨 {style.capitalize()} style...")
            chart.plot(timeframe='3M', style=style, title=f'{symbol} - {style.capitalize()} Chart').save(f'examples/charts/TSLA_style_{style}.png')
            print(f"   ✅ Saved TSLA_style_{style}.png")
        except Exception as e:
            print(f"   ❌ Error with {style} style: {e}")


def demo_technical_indicators():
    """Demonstrate technical indicators."""
    print("\n📊 TECHNICAL INDICATOR EXAMPLES")
    print("=" * 50)
    
    symbol = 'AAPL'  # Use Apple for indicators demo
    chart = OHLCVChart(symbol=symbol)
    
    indicator_configs = [
        ('MA50', '50-day Moving Average'),
        ('MA200', '200-day Moving Average'), 
        ('BOTH', 'Both Moving Averages')
    ]
    
    for indicator, description in indicator_configs:
        try:
            print(f"   📈 {description}...")
            chart.plot(timeframe='1Y', indicators=indicator, title=f'{symbol} - {description}').save(f'examples/charts/AAPL_indicators_{indicator}.png')
            print(f"   ✅ Saved AAPL_indicators_{indicator}.png")
        except Exception as e:
            print(f"   ❌ Error with {indicator} indicators: {e}")


def demo_volume_options():
    """Demonstrate volume visualization options."""
    print("\n📊 VOLUME VISUALIZATION EXAMPLES")
    print("=" * 50)
    
    symbol = 'BTC-USD'  # Use Bitcoin for volume demo
    chart = OHLCVChart(symbol=symbol)
    
    volume_configs = [
        ('subplot', 'Volume Subplot'),
        ('overlay', 'Volume Overlay')
    ]
    
    for volume_type, description in volume_configs:
        try:
            print(f"   📊 {description}...")
            chart.plot(timeframe='1M', style='candlestick', volume=volume_type, title=f'{symbol} - {description}').save(f'examples/charts/BTC_volume_{volume_type}.png')
            print(f"   ✅ Saved BTC_volume_{volume_type}.png")
        except Exception as e:
            print(f"   ❌ Error with {volume_type} volume: {e}")


def demo_logarithmic_scale():
    """Demonstrate logarithmic price scaling."""
    print("\n📈 LOGARITHMIC SCALE EXAMPLES")
    print("=" * 50)
    
    symbol = 'BTC-USD'  # Bitcoin is ideal for log scale due to massive price growth
    chart = OHLCVChart(symbol=symbol)
    
    scales = [
        ('linear', 'Linear Scale'),
        ('log', 'Logarithmic Scale')
    ]
    
    for scale, description in scales:
        try:
            print(f"   📊 {description}...")
            chart.plot(timeframe='MAX', scale=scale, title=f'{symbol} - {description} (All Time)').save(f'examples/charts/BTC_scale_{scale}.png')
            print(f"   ✅ Saved BTC_scale_{scale}.png")
        except Exception as e:
            print(f"   ❌ Error with {scale} scale: {e}")


def demo_advanced_combinations():
    """Demonstrate advanced chart combinations."""
    print("\n🚀 ADVANCED COMBINATION EXAMPLES")
    print("=" * 50)
    
    advanced_configs = [
        {
            'symbol': 'BTC-USD',
            'timeframe': '1Y', 
            'style': 'candlestick',
            'scale': 'linear',
            'indicators': 'BOTH',
            'volume': 'subplot',
            'filename': 'BTC_advanced_complete.png',
            'description': 'Bitcoin: 1Y Candlestick with MAs and Volume'
        },
        {
            'symbol': 'TSLA',
            'timeframe': '6M',
            'style': 'area', 
            'scale': 'linear',
            'indicators': 'MA50',
            'volume': 'overlay',
            'filename': 'TSLA_advanced_area.png',
            'description': 'Tesla: 6M Area Chart with MA50 and Volume Overlay'
        },
        {
            'symbol': 'AAPL',
            'timeframe': '5Y',  # Fixed: changed from '2Y' to valid '5Y'
            'style': 'line',
            'scale': 'log',
            'indicators': 'MA200', 
            'volume': False,
            'filename': 'AAPL_advanced_log.png',
            'description': 'Apple: Multi-year Line Chart with Log Scale and MA200'
        }
    ]
    
    for config in advanced_configs:
        try:
            print(f"   🎯 {config['description']}...")
            chart = OHLCVChart(symbol=config['symbol'])
            chart.plot(
                timeframe=config['timeframe'],
                style=config['style'],
                scale=config['scale'], 
                indicators=config['indicators'],
                volume=config['volume'],
                title=config['description']
            ).save(f"examples/charts/{config['filename']}")
            print(f"   ✅ Saved {config['filename']}")
        except Exception as e:
            print(f"   ❌ Error with advanced config: {e}")


def create_charts_directory():
    """Create charts directory if it doesn't exist."""
    charts_dir = 'examples/charts'
    os.makedirs(charts_dir, exist_ok=True)
    return charts_dir


def main():
    """Run all chart examples."""
    print("🎨 BITCOIN STRATEGY BACKTESTER - CHART EXAMPLES")
    print("=" * 60)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create output directory
    charts_dir = create_charts_directory()
    print(f"📁 Charts will be saved to: {charts_dir}")
    
    try:
        # Run all demos
        demo_basic_charts()
        demo_timeframes()
        demo_chart_styles()
        demo_technical_indicators()
        demo_volume_options()
        demo_logarithmic_scale()
        demo_advanced_combinations()
        
        print("\n" + "=" * 60)
        print("🎉 ALL CHART EXAMPLES COMPLETED SUCCESSFULLY!")
        print(f"📁 Check the '{charts_dir}' directory for generated charts")
        print("💡 Tip: Open the PNG files to see the professional financial charts")
        
    except Exception as e:
        print(f"\n❌ Error running chart examples: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
