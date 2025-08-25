"""
Core configuration functionality for project-conf.

This module provides the main ProjectConfig class and global configuration management.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union


class ProjectConfig(dict):
    """
    Configuration object that behaves like a dictionary but provides path helpers.
    
    This class extends the built-in dict to provide convenient path helper methods
    while maintaining full dictionary compatibility.
    
    Args:
        config_data: Dictionary of configuration values
        project_root: Path to the project root directory
        
    Example:
        >>> config = ProjectConfig({'debug': True}, Path('/project'))
        >>> config['debug']  # Dictionary access
        True
        >>> config.data_path('app.db')  # Path helper
        '/project/data/app.db'
    """
    
    def __init__(self, config_data: Dict[str, Any], project_root: Path) -> None:
        """Initialize the configuration object."""
        super().__init__(config_data)
        self._project_root = project_root
    
    @property
    def project_root(self) -> str:
        """Get the project root path as a string."""
        return str(self._project_root)
    
    def __getattr__(self, name: str) -> Any:
        """
        Handle path helpers: Only allow *_path methods.
        
        Args:
            name: Attribute name to access
            
        Returns:
            Path helper function for *_path methods
            
        Raises:
            AttributeError: If the attribute doesn't end with '_path'
            
        Example:
            >>> config.data_path('file.db')  # Returns /project/data/file.db
            >>> config.logs_path()  # Returns /project/logs/
        """
        if not name.endswith('_path'):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'. "
                f"Did you mean '{name}_path'? "
                f"Only *_path methods are supported for path helpers."
            )
        
        # Extract directory name (remove '_path' suffix)
        dir_name = name[:-5]
        
        def path_helper(filename: str = "") -> str:
            """
            Create project-relative path.
            
            Args:
                filename: Optional filename to append
                
            Returns:
                Full path as string
            """
            base_path = self._project_root / dir_name
            
            if filename:
                # Ensure parent directory exists
                base_path.mkdir(parents=True, exist_ok=True)
                return str(base_path / filename)
            else:
                # Just return the directory path (create it)
                base_path.mkdir(parents=True, exist_ok=True)
                return str(base_path)
        
        return path_helper
    
    def copy(self) -> "ProjectConfig":
        """Return a copy that maintains path helper functionality."""
        return ProjectConfig(dict(self), self._project_root)


def _find_project_root(start_path: Optional[Path] = None) -> Path:
    """
    Find project root by looking for common project markers.
    
    Args:
        start_path: Starting directory for search (defaults to current directory)
        
    Returns:
        Path to the project root directory
    """
    if start_path is None:
        start_path = Path.cwd()
    
    current = Path(start_path).resolve()
    
    # Project markers in order of reliability
    markers = [
        '.git',              # Git repository (most reliable)
        'pyproject.toml',    # Modern Python packaging
        'setup.py',          # Traditional Python packaging
        'requirements.txt',  # Python dependencies
        'poetry.lock',       # Poetry projects
        'Pipfile',          # Pipenv projects
        'package.json',     # Node.js (for full-stack projects)
        '.env'              # Environment files
    ]
    
    while current != current.parent:
        if any((current / marker).exists() for marker in markers):
            return current
        current = current.parent
    
    # Fallback to current working directory
    return Path.cwd()


def _load_env_file(project_root: Path) -> Dict[str, str]:
    """
    Load .env file from project root if it exists.
    
    Args:
        project_root: Path to the project root directory
        
    Returns:
        Dictionary of environment variables from .env file
    """
    env_file = project_root / '.env'
    env_vars = {}
    
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().lower()
                        value = value.strip().strip('"\'')
                        env_vars[key] = value
        except Exception:
            pass  # Silently ignore env file errors
    
    return env_vars


def _convert_value(env_value: str, default_value: Any) -> Any:
    """
    Convert string environment variable to match default type.
    
    Args:
        env_value: String value from environment variable
        default_value: Default value to match type against
        
    Returns:
        Converted value matching the type of default_value
    """
    # Keep strings as strings
    if isinstance(default_value, str):
        return env_value
    
    # Convert to match default type
    if isinstance(default_value, bool):
        return env_value.lower() in ('true', '1', 'yes', 'on')
    elif isinstance(default_value, int):
        try:
            return int(env_value)
        except ValueError:
            return default_value
    elif isinstance(default_value, float):
        try:
            return float(env_value)
        except ValueError:
            return default_value
    elif isinstance(default_value, list):
        # Simple JSON-style lists only: ["item1", "item2"]
        if env_value.startswith('[') and env_value.endswith(']'):
            try:
                return json.loads(env_value)
            except json.JSONDecodeError:
                return [env_value]
        else:
            return [env_value]
    
    return env_value


# Global configuration state
_global_config: Optional[ProjectConfig] = None


def setup(defaults: Dict[str, Any], project_root: Optional[Union[str, Path]] = None) -> None:
    """
    Setup global configuration with defaults and automatic environment override.
    
    Args:
        defaults: Dictionary of default values (defines schema and types)
        project_root: Optional override for project root (defaults to auto-detection)
        
    Example:
        >>> setup({
        ...     'database_url': 'sqlite:///app.db',
        ...     'debug': False,
        ...     'max_workers': 4
        ... })
    """
    global _global_config
    
    # 1. Determine project root
    if project_root:
        root_path = Path(project_root).resolve()
    elif 'PROJECT_ROOT' in os.environ:
        root_path = Path(os.environ['PROJECT_ROOT']).resolve()
    else:
        root_path = _find_project_root()
    
    # 2. Start with defaults
    final_config = defaults.copy()
    
    # 3. Override with environment variables
    for key, default_value in defaults.items():
        # Convert config key to environment variable name
        env_key = key.replace('.', '_').replace('-', '_').upper()
        
        if env_key in os.environ:
            env_value = os.environ[env_key]
            final_config[key] = _convert_value(env_value, default_value)
    
    # 4. Override with .env file values
    env_file_vars = _load_env_file(root_path)
    for key, default_value in defaults.items():
        # Check both original key and underscore version
        env_key = key.lower()
        underscore_key = key.replace('.', '_').replace('-', '_').lower()
        
        if env_key in env_file_vars:
            final_config[key] = _convert_value(env_file_vars[env_key], default_value)
        elif underscore_key in env_file_vars:
            final_config[key] = _convert_value(env_file_vars[underscore_key], default_value)
    
    # 5. Add project_root to config
    final_config['project_root'] = str(root_path)
    
    # 6. Create global config object
    _global_config = ProjectConfig(final_config, root_path)


def get_config() -> ProjectConfig:
    """
    Get the global configuration object (behaves like a dict with path helpers).
    
    Returns:
        ProjectConfig: Dictionary-like object with path helper methods
        
    Raises:
        RuntimeError: If setup() hasn't been called yet
        
    Example:
        >>> config = get_config()
        >>> config['debug']  # Dictionary access
        False
        >>> config.data_path('app.db')  # Path helper
        '/project/data/app.db'
    """
    if _global_config is None:
        raise RuntimeError(
            "Configuration not initialized. Call setup(defaults) first.\n"
            "Example: setup({'database_url': 'sqlite:///app.db', 'debug': False})"
        )
    return _global_config
