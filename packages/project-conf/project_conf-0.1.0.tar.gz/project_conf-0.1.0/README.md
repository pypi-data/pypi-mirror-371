# project-conf

[![PyPI version](https://badge.fury.io/py/project-conf.svg)](https://badge.fury.io/py/project-conf)
[![Python Support](https://img.shields.io/pypi/pyversions/project-conf.svg)](https://pypi.org/project/project-conf/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Dictionary-style configuration with path helpers and automatic environment variable handling.**

A simple, powerful configuration system that behaves like a dictionary but provides convenient path helpers and automatic environment variable integration. Perfect for Python projects that need clean, flexible configuration management.

## ✨ Features

- **🗂️ Dictionary Interface**: Full dict compatibility - use `config['key']`, `config.get()`, `config.update()`, etc.
- **📁 Path Helpers**: Automatic directory creation with `config.data_path()`, `config.logs_path()`, etc.
- **🌐 Environment Integration**: Automatic override from environment variables and `.env` files
- **🎯 Type-Safe Conversion**: Smart type conversion based on your defaults
- **🚀 Auto Project Detection**: Finds your project root automatically
- **🔧 Runtime Modification**: Change configuration at runtime, visible globally
- **📦 Zero Dependencies**: Pure Python, no external dependencies

## 🚀 Quick Start

### Installation

```bash
pip install project-conf
```

### Basic Usage

```python
from project_conf import setup, get_config

# 1. Define your configuration schema with defaults
setup({
    'database_url': 'sqlite:///app.db',
    'debug': False,
    'max_workers': 4,
    'api_key': '',
    'features': ['auth', 'cache']
})

# 2. Use anywhere in your application
config = get_config()

# Dictionary-style access
print(config['database_url'])  # sqlite:///app.db
config['debug'] = True         # Runtime modification
config.update({'timeout': 30}) # Bulk updates

# Path helpers (creates directories automatically)
db_path = config.data_path('app.db')      # /project/data/app.db
log_file = config.logs_path('server.log') # /project/logs/server.log
cache_dir = config.cache_path()           # /project/cache/
```

## 📖 Documentation

### Environment Variable Override

Configuration values are automatically overridden by environment variables:

```python
# config.py
setup({
    'database_url': 'sqlite:///dev.db',
    'debug': True,
    'max_workers': 2
})
```

```bash
# Environment variables (case-insensitive, converts types)
export DATABASE_URL="postgresql://localhost/prod"
export DEBUG=false
export MAX_WORKERS=8
```

```python
config = get_config()
print(config['database_url'])  # postgresql://localhost/prod
print(config['debug'])         # False
print(config['max_workers'])   # 8
```

### .env File Support

Create a `.env` file in your project root:

```env
# .env
DATABASE_URL=postgresql://localhost/myapp
DEBUG=false
MAX_WORKERS=8
API_KEY=secret-key-123
FEATURES=["auth", "admin", "analytics"]
```

Values are automatically loaded and type-converted based on your defaults.

### Path Helpers

Any method ending with `_path` becomes a path helper:

```python
config = get_config()

# Directory paths (creates directories)
config.data_path()           # /project/data/
config.logs_path()           # /project/logs/
config.uploads_path()        # /project/uploads/
config.my_custom_path()      # /project/my_custom/

# File paths (creates parent directories)
config.data_path('app.db')           # /project/data/app.db
config.logs_path('server.log')       # /project/logs/server.log
config.uploads_path('image.jpg')     # /project/uploads/image.jpg
config.my_custom_path('file.txt')    # /project/my_custom/file.txt
```

### Type Conversion

Environment variables are automatically converted to match your default types:

```python
setup({
    'debug': False,        # bool: 'true'/'false', '1'/'0', 'yes'/'no'
    'workers': 4,          # int: '8' -> 8
    'timeout': 30.0,       # float: '45.5' -> 45.5
    'name': 'app',         # str: kept as string
    'features': ['auth']   # list: '["auth", "admin"]' -> ['auth', 'admin']
})
```

### Project Root Detection

The project root is automatically detected by looking for:

1. `.git` directory (most reliable)
2. `pyproject.toml`
3. `setup.py`
4. `requirements.txt`
5. `poetry.lock`
6. `Pipfile`
7. `package.json`
8. `.env`

You can also override with `PROJECT_ROOT` environment variable or pass it directly:

```python
setup(defaults, project_root='/custom/path')
```

## 🎯 Real-World Example

```python
# myproject/config.py
from project_conf import setup

# Single source of truth for configuration
DEFAULTS = {
    'database_url': 'sqlite:///myproject.db',
    'redis_url': 'redis://localhost:6379',
    'debug': False,
    'max_workers': 4,
    'timeout': 30.0,
    'api_key': '',
    'log_level': 'INFO',
    'features': {
        'auth': True,
        'admin': False,
        'analytics': True
    }
}

# Initialize configuration
setup(DEFAULTS)
```

```python
# myproject/database.py
from project_conf import get_config

def create_connection():
    config = get_config()
    
    # Use as dictionary
    db_url = config['database_url']
    timeout = config.get('timeout', 30)
    
    # Use path helper for file location
    if 'sqlite' in db_url:
        db_file = config.data_path('myproject.db')
        return f"sqlite://{db_file}"
    
    return db_url
```

```python
# myproject/api.py  
from project_conf import get_config

def setup_logging():
    config = get_config()
    
    # Runtime configuration changes
    if not config.get('api_key'):
        config['api_key'] = 'development-key'
    
    # Path helpers for log files
    log_file = config.logs_path('api.log')
    
    return setup_logger(
        level=config['log_level'],
        file=log_file
    )
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=project_conf --cov-report=html
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [PyPI Package](https://pypi.org/project/project-conf/)
- [Source Code](https://github.com/yourusername/project-conf)
- [Issue Tracker](https://github.com/yourusername/project-conf/issues)
- [Changelog](CHANGELOG.md)
