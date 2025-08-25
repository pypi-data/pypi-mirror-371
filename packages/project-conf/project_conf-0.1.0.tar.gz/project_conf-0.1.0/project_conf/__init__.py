"""
project-conf: Dictionary-style configuration with path helpers and automatic environment variable handling.

A simple, powerful configuration system that behaves like a dictionary but provides
convenient path helpers and automatic environment variable integration.

Example:
    >>> from project_conf import setup, get_config
    >>> setup({
    ...     'database_url': 'sqlite:///app.db',
    ...     'debug': False,
    ...     'max_workers': 4
    ... })
    >>> config = get_config()
    >>> config['database_url']  # Dictionary access
    'sqlite:///app.db'
    >>> config.data_path('app.db')  # Path helper
    '/project/data/app.db'
"""

__version__ = "0.1.0"
__author__ = "importal"
__email__ = "xychen@msn.com"

from .core import ProjectConfig, setup, get_config

__all__ = [
    "ProjectConfig",
    "setup", 
    "get_config",
    "__version__",
]
