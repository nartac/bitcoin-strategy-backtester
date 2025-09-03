#!/usr/bin/env python3
"""
Chart Explorer CLI - Interactive Financial Chart Explorer
A user-friendly command-line interface for the Bitcoin Strategy Backtester project.

Usage:
    python chart_explorer.py TSLA --timeframe 6M --style candlestick --indicators MA50 --volume subplot
    python chart_explorer.py  # Interactive mode
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from src.visualization.chart_engine import OHLCVChart
except ImportError as e:
    print(f"❌ Error importing chart engine: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Configuration
VALID_TIMEFRAMES = ['5D', '1M', '3M', '6M', 'YTD', '1Y', '5Y', 'MAX']
VALID_STYLES = ['line', 'area', 'candlestick', 'ohlc']
VALID_SCALES = ['linear', 'log']
VALID_INDICATORS = [None, 'MA50', 'MA200', 'BOTH']
VALID_VOLUME = [None, 'subplot', 'overlay']

HISTORY_FILE = '.chart_history.json'
FAVORITES_FILE = '.chart_favorites.json'

class ChartExplorer:
    """Interactive Chart Explorer CLI."""
    
    def __init__(self):
        self.history = self._load_history()
        self.favorites = self._load_favorites()
    
    def _load_history(self) -> list:
        """Load chart generation history."""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def _save_history(self, entry: Dict[str, Any]) -> None:
        """Save chart generation to history."""
        try:
            entry['timestamp'] = datetime.now().isoformat()
            self.history.insert(0, entry)
            # Keep only last 20 entries
            self.history = self.history[:20]
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception:
            pass
    
    def _load_favorites(self) -> list:
        """Load favorite chart configurations."""
        try:
            if os.path.exists(FAVORITES_FILE):
                with open(FAVORITES_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def _save_favorites(self) -> None:
        """Save favorites to file."""
        try:
            with open(FAVORITES_FILE, 'w') as f:
                json.dump(self.favorites, f, indent=2)
        except Exception:
            pass
    
    def print_colored(self, text: str, color: str = Colors.END) -> None:
        """Print colored text to terminal."""
        print(f"{color}{text}{Colors.END}")
    
    def print_header(self, text: str) -> None:
        """Print a formatted header."""
        self.print_colored(f"\n{'='*60}", Colors.CYAN)
        self.print_colored(f"{text:^60}", Colors.BOLD + Colors.CYAN)
        self.print_colored(f"{'='*60}", Colors.CYAN)
    
    def print_help(self) -> None:
        """Print detailed help information."""
        self.print_header("📊 FINANCIAL CHART EXPLORER")
        
        print(f"\n{Colors.BOLD}USAGE:{Colors.END}")
        print(f"  {Colors.GREEN}python chart_explorer.py [TICKER] [OPTIONS]{Colors.END}")
        print(f"  {Colors.GREEN}python chart_explorer.py{Colors.END} (interactive mode)")
        
        print(f"\n{Colors.BOLD}EXAMPLES:{Colors.END}")
        print(f"  {Colors.YELLOW}python chart_explorer.py TSLA --timeframe 6M --style candlestick{Colors.END}")
        print(f"  {Colors.YELLOW}python chart_explorer.py BTC-USD --timeframe 1Y --indicators BOTH --volume subplot{Colors.END}")
        
        print(f"\n{Colors.BOLD}PARAMETERS:{Colors.END}")
        print(f"  {Colors.BLUE}Timeframes:{Colors.END} {', '.join(VALID_TIMEFRAMES)}")
        print(f"  {Colors.BLUE}Chart Styles:{Colors.END} {', '.join(VALID_STYLES)}")
        print(f"  {Colors.BLUE}Price Scales:{Colors.END} {', '.join(VALID_SCALES)}")
        print(f"  {Colors.BLUE}Indicators:{Colors.END} None, MA50, MA200, BOTH")
        print(f"  {Colors.BLUE}Volume Display:{Colors.END} None, subplot, overlay")
        
        print(f"\n{Colors.BOLD}POPULAR TICKERS:{Colors.END}")
        popular = ["BTC-USD", "ETH-USD", "AAPL", "TSLA", "GOOGL", "MSFT", "AMZN", "NVDA"]
        print(f"  {', '.join(popular)}")
    
    def get_user_input(self, prompt: str, valid_options: list = None, default: str = None) -> str:
        """Get user input with validation."""
        while True:
            if default:
                user_input = input(f"{prompt} [{default}]: ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"{prompt}: ").strip()
            
            if not user_input and not default:
                self.print_colored("❌ Input cannot be empty.", Colors.RED)
                continue
            
            if valid_options and user_input not in valid_options:
                self.print_colored(f"❌ Invalid option. Choose from: {', '.join(map(str, valid_options))}", Colors.RED)
                continue
            
            return user_input
    
    def interactive_mode(self) -> Dict[str, Any]:
        """Run interactive mode to get chart parameters."""
        self.print_header("🔧 INTERACTIVE CHART CONFIGURATION")
        
        # Show recent history
        if self.history:
            print(f"\n{Colors.BOLD}📚 Recent Charts:{Colors.END}")
            for i, entry in enumerate(self.history[:5], 1):
                timestamp = entry.get('timestamp', 'Unknown')[:16]
                print(f"  {i}. {entry['symbol']} - {entry['timeframe']} - {entry['style']} ({timestamp})")
        
        # Show favorites
        if self.favorites:
            print(f"\n{Colors.BOLD}⭐ Favorites:{Colors.END}")
            for i, fav in enumerate(self.favorites, 1):
                print(f"  {i}. {fav['name']}: {fav['symbol']} - {fav['timeframe']} - {fav['style']}")
        
        print(f"\n{Colors.BOLD}Configure your chart:{Colors.END}")
        
        # Get parameters
        symbol = self.get_user_input(f"{Colors.CYAN}Enter ticker symbol{Colors.END}").upper()
        
        print(f"\n{Colors.BLUE}Available timeframes:{Colors.END} {', '.join(VALID_TIMEFRAMES)}")
        timeframe = self.get_user_input(f"{Colors.CYAN}Select timeframe{Colors.END}", VALID_TIMEFRAMES, '1Y')
        
        print(f"\n{Colors.BLUE}Available styles:{Colors.END} {', '.join(VALID_STYLES)}")
        style = self.get_user_input(f"{Colors.CYAN}Select chart style{Colors.END}", VALID_STYLES, 'line')
        
        print(f"\n{Colors.BLUE}Available scales:{Colors.END} {', '.join(VALID_SCALES)}")
        scale = self.get_user_input(f"{Colors.CYAN}Select price scale{Colors.END}", VALID_SCALES, 'linear')
        
        print(f"\n{Colors.BLUE}Available indicators:{Colors.END} None, MA50, MA200, BOTH")
        indicators_input = self.get_user_input(f"{Colors.CYAN}Select indicators{Colors.END}", ['None', 'MA50', 'MA200', 'BOTH'], 'None')
        indicators = None if indicators_input == 'None' else indicators_input
        
        print(f"\n{Colors.BLUE}Volume options:{Colors.END} None, subplot, overlay")
        volume_input = self.get_user_input(f"{Colors.CYAN}Select volume display{Colors.END}", ['None', 'subplot', 'overlay'], 'None')
        volume = False if volume_input == 'None' else volume_input
        
        output = self.get_user_input(f"{Colors.CYAN}Output filename (optional){Colors.END}", default="")
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'style': style,
            'scale': scale,
            'indicators': indicators,
            'volume': volume,
            'output': output if output else None
        }
    
    def create_chart(self, params: Dict[str, Any]) -> bool:
        """Create and save the chart."""
        try:
            symbol = params['symbol']
            self.print_colored(f"\n🚀 Creating chart for {symbol}...", Colors.YELLOW)
            
            # Show progress
            self.print_colored("📡 Fetching data...", Colors.BLUE)
            
            # Create chart
            chart = OHLCVChart(symbol=symbol)
            
            self.print_colored("📊 Generating chart...", Colors.BLUE)
            
            result = chart.plot(
                timeframe=params['timeframe'],
                style=params['style'],
                scale=params['scale'],
                indicators=params['indicators'],
                volume=params['volume']
            )
            
            # Generate filename if not provided
            if not params['output'] or not params['output'].strip():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chart_{symbol}_{params['timeframe']}_{params['style']}_{timestamp}.png"
                output_path = os.path.join('examples', 'charts', filename)
            else:
                output_path = params['output'].strip()
                # If no directory specified, save to examples/charts
                if not os.path.dirname(output_path):
                    output_path = os.path.join('examples', 'charts', output_path)
                # Ensure file has an extension
                if not output_path.endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                    output_path += '.png'
            
            # Ensure directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:  # Only create directory if there's a directory path
                os.makedirs(output_dir, exist_ok=True)
            
            self.print_colored("💾 Saving chart...", Colors.BLUE)
            result.save(output_path)
            
            self.print_colored(f"✅ Chart saved successfully to: {output_path}", Colors.GREEN)
            
            # Try to display chart
            try:
                result.show()
                self.print_colored("👀 Chart displayed!", Colors.GREEN)
            except Exception:
                self.print_colored("ℹ️  Chart saved but cannot be displayed in this environment.", Colors.YELLOW)
            
            # Save to history
            history_entry = params.copy()
            history_entry['output_path'] = output_path
            self._save_history(history_entry)
            
            # Ask if user wants to save as favorite
            try:
                save_fav = input(f"\n{Colors.CYAN}Save this configuration as a favorite? (y/N): {Colors.END}").lower()
                if save_fav == 'y':
                    name = input(f"{Colors.CYAN}Enter a name for this favorite: {Colors.END}").strip()
                    if name:
                        favorite = params.copy()
                        favorite['name'] = name
                        self.favorites.append(favorite)
                        self._save_favorites()
                        self.print_colored(f"⭐ Saved as favorite: {name}", Colors.GREEN)
            except (EOFError, KeyboardInterrupt):
                # Handle EOF or Ctrl+C gracefully
                pass
            
            return True
            
        except Exception as e:
            self.print_colored(f"❌ Error creating chart: {e}", Colors.RED)
            return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Interactive Financial Chart Explorer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chart_explorer.py TSLA --timeframe 6M --style candlestick --indicators MA50 --volume subplot
  python chart_explorer.py BTC-USD --timeframe 1Y --indicators BOTH
  python chart_explorer.py  # Interactive mode

Available Options:
  Timeframes: 5D, 1M, 3M, 6M, YTD, 1Y, 5Y, MAX
  Styles: line, area, candlestick, ohlc
  Scales: linear, log
  Indicators: MA50, MA200, BOTH
  Volume: subplot, overlay
        """
    )
    
    parser.add_argument('symbol', nargs='?', help='Ticker symbol (e.g., TSLA, BTC-USD)')
    parser.add_argument('--timeframe', '-t', choices=VALID_TIMEFRAMES, default='1Y',
                       help='Chart timeframe (default: 1Y)')
    parser.add_argument('--style', '-s', choices=VALID_STYLES, default='line',
                       help='Chart style (default: line)')
    parser.add_argument('--scale', choices=VALID_SCALES, default='linear',
                       help='Price scale (default: linear)')
    parser.add_argument('--indicators', '-i', choices=['MA50', 'MA200', 'BOTH'],
                       help='Technical indicators')
    parser.add_argument('--volume', '-v', choices=['subplot', 'overlay'],
                       help='Volume display mode')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--help-detailed', action='store_true',
                       help='Show detailed help and exit')
    
    return parser.parse_args()

def main():
    """Main function."""
    explorer = ChartExplorer()
    
    args = parse_arguments()
    
    if args.help_detailed:
        explorer.print_help()
        return
    
    # Determine if we're in interactive mode
    if not args.symbol:
        # Interactive mode
        params = explorer.interactive_mode()
    else:
        # Command line mode
        params = {
            'symbol': args.symbol.upper(),
            'timeframe': args.timeframe,
            'style': args.style,
            'scale': args.scale,
            'indicators': args.indicators,
            'volume': args.volume or False,
            'output': args.output
        }
        
        explorer.print_header("📊 CHART GENERATION")
        print(f"{Colors.BOLD}Configuration:{Colors.END}")
        for key, value in params.items():
            if value:
                print(f"  {Colors.BLUE}{key.title()}:{Colors.END} {value}")
    
    # Create the chart
    success = explorer.create_chart(params)
    
    if success:
        explorer.print_colored("\n🎉 Chart generation completed successfully!", Colors.GREEN)
    else:
        explorer.print_colored("\n💥 Chart generation failed!", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Operation cancelled by user.{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.END}")
        sys.exit(1)
