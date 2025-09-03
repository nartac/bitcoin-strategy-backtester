#!/usr/bin/env python3
"""
Repository Cleanup Script
Removes temporary files, cache directories, and auto-generated content.
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_repository():
    """Clean up temporary files and directories."""
    print("🧹 Repository Cleanup Script")
    print("=" * 40)
    
    cleanup_items = [
        # Python cache files and directories
        ("__pycache__ directories", "__pycache__"),
        ("*.pyc files", "*.pyc"),
        ("*.pyo files", "*.pyo"),
        
        # Test and coverage files
        (".pytest_cache", ".pytest_cache"),
        (".coverage files", ".coverage*"),
        ("htmlcov directory", "htmlcov"),
        
        # Chart Explorer files
        ("Chart history", ".chart_history.json"),
        ("Chart favorites", ".chart_favorites.json"),
        
        # Auto-generated chart files (timestamped)
        ("Auto-generated charts", "examples/charts/chart_*_????????_??????.png"),
        
        # Temporary files
        ("Temporary .tmp files", "*.tmp"),
        ("Temporary .temp files", "*.temp"),
        ("Backup files", "*~"),
        
        # OS-specific files
        (".DS_Store files", ".DS_Store"),
        ("Thumbs.db files", "Thumbs.db"),
        
        # SQLite database files (symbol names)
        ("SQLite symbol databases", "BTC-USD"),
        ("SQLite symbol databases", "ETH-USD"),
        ("SQLite symbol databases", "AAPL"),
        ("SQLite symbol databases", "TSLA"),
        ("SQLite symbol databases", "GOOGL"),
        ("SQLite symbol databases", "MSFT"),
        ("SQLite symbol databases", "AMZN"),
        ("SQLite symbol databases", "NVDA"),
    ]
    
    removed_count = 0
    
    for description, pattern in cleanup_items:
        try:
            if pattern.startswith(".") and not "*" in pattern and not "/" in pattern:
                # Single file or directory
                if os.path.exists(pattern):
                    if os.path.isdir(pattern):
                        shutil.rmtree(pattern)
                        print(f"✅ Removed {description}: {pattern}/")
                    else:
                        os.remove(pattern)
                        print(f"✅ Removed {description}: {pattern}")
                    removed_count += 1
            else:
                # Pattern matching
                if pattern == "__pycache__":
                    # Find all __pycache__ directories
                    for root, dirs, files in os.walk("."):
                        if "__pycache__" in dirs:
                            pycache_path = os.path.join(root, "__pycache__")
                            if "venv" not in pycache_path:  # Don't touch venv
                                shutil.rmtree(pycache_path)
                                print(f"✅ Removed {description}: {pycache_path}")
                                removed_count += 1
                else:
                    # Use glob for pattern matching
                    matches = glob.glob(pattern, recursive=True)
                    for match in matches:
                        if "venv" not in match:  # Don't touch venv
                            if os.path.isdir(match):
                                shutil.rmtree(match)
                                print(f"✅ Removed {description}: {match}/")
                            else:
                                os.remove(match)
                                print(f"✅ Removed {description}: {match}")
                            removed_count += 1
        except Exception as e:
            print(f"⚠️  Could not remove {description} ({pattern}): {e}")
    
    print(f"\n🎉 Cleanup completed! Removed {removed_count} items.")
    print("\n💡 This script preserves:")
    print("   - Source code and tests")
    print("   - Virtual environment")
    print("   - Meaningful example charts")
    print("   - Documentation and configuration")

if __name__ == "__main__":
    try:
        cleanup_repository()
    except KeyboardInterrupt:
        print("\n⚠️  Cleanup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
