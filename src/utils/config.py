import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Data Configuration (no API keys needed for Yahoo Finance)
DEFAULT_TIMEFRAME = os.getenv('DEFAULT_TIMEFRAME', '1d')
DEFAULT_LOOKBACK_DAYS = int(os.getenv('DEFAULT_LOOKBACK_DAYS', '365'))

# Backtesting Configuration
DEFAULT_INITIAL_CAPITAL = float(os.getenv('DEFAULT_INITIAL_CAPITAL', '10000'))
DEFAULT_COMMISSION = float(os.getenv('DEFAULT_COMMISSION', '0.001'))

# Rate limiting for bulk operations (optional)
RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '0.1'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# Database Configuration
DATABASE_CONFIG = {
    'db_path': os.getenv('DB_PATH', 'data/ohlcv_data.db'),
    'cache_enabled': os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
    'max_cache_age_days': int(os.getenv('MAX_CACHE_AGE_DAYS', '1')),
    'batch_size': int(os.getenv('DB_BATCH_SIZE', '1000')),
    'enable_wal_mode': True,  # For better performance
    'vacuum_on_startup': False,
    'backup_enabled': True,
    'backup_interval_days': 7
}

# Symbol Configuration
DEFAULT_SYMBOLS = ['BTC-USD', 'ETH-USD', 'AAPL', 'TSLA', 'SPY']
CACHE_WARM_SYMBOLS = ['BTC-USD', 'ETH-USD']  # Pre-cache these popular symbols

# Data Quality Configuration
DATA_QUALITY_CONFIG = {
    'validate_on_store': True,
    'clean_invalid_data': True,
    'allow_weekends': True,  # Crypto trades on weekends
    'max_price_change_percent': 50.0,  # Alert if price changes more than 50% in one day
    'min_volume_threshold': 0  # Minimum volume threshold (0 = no threshold)
}