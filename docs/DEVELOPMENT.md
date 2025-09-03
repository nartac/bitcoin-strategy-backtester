Lock versions later: Once everything works, run pip freeze > requirements-lock.txt to lock exact versions.

venv\Scripts\activate

# Run all tests
python -m pytest

# Run specific test file  
python -m pytest tests/test_cache_manager.py

# Run specific test
python -m pytest tests/test_cache_manager.py::TestCacheManager::test_cache_stats

# Run with verbose output
python -m pytest -v