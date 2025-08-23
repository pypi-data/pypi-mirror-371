# Tests Directory

This directory contains all test files for the `certbot-dns-f5xc` plugin.

## Naming Conventions

The test files follow consistent naming conventions for easy identification:

- **`test_*.py`**: Main test suite files (run with pytest)
- **`debug_*.py`**: Debugging and development scripts
- **`util_*.py`**: Utility and helper scripts
- **`cleanup_*.py`**: Cleanup and maintenance scripts

## Directory Structure

```
tests/
├── __init__.py                 # Tests package
├── README.md                   # This file
├── test_plugin.py             # Main plugin tests
├── debug/                      # Debug and development tests
│   ├── __init__.py
│   ├── debug_api.py           # F5XC API debugging script
│   ├── debug_plugin_auth.py   # Plugin authentication tests
│   ├── debug_api_token.py     # API token format tests
│   ├── util_check_zone.py     # Zone inspection script
│   └── util_cleanup_rrsets.py # Cleanup old test RRSets
└── temp/                       # Temporary test files
    └── __init__.py
```

## File Descriptions

### Main Tests (`test_*.py`)

- **`test_plugin.py`**: Core plugin functionality tests

### Debug Tests (`debug/`)

- **`debug_api.py`**: Direct F5XC API testing and debugging
- **`debug_plugin_auth.py`**: Mimics plugin authentication for debugging
- **`debug_api_token.py`**: Tests different API token header formats

### Utility Scripts (`util_*.py`)

- **`util_check_zone.py`**: Inspects F5XC zone data without modification
- **`util_cleanup_rrsets.py`**: Removes old test RRSets from zones

### Temporary Tests (`temp/`)

- Reserved for temporary test files during development

## Usage

### Running Main Tests

```bash
python -m pytest tests/
```

### Running Specific Tests

```bash
python -m pytest tests/test_plugin.py
```

### Debug Scripts

```bash
# Test F5XC API directly
python tests/debug/debug_api.py

# Check zone data
python tests/debug/util_check_zone.py

# Clean up test data
python tests/debug/util_cleanup_rrsets.py
```

## Notes

- Debug scripts are for development/testing only
- Always clean up after using debug scripts
- Test files in `debug/` are not part of the main test suite
- Files in `temp/` should be cleaned up regularly
