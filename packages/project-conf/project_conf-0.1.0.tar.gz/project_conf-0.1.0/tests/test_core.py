"""
Tests for the core functionality of project-conf.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any
import pytest

from project_conf import setup, get_config, ProjectConfig
from project_conf.core import (
    _find_project_root,
    _load_env_file,
    _convert_value,
    _global_config
)


class TestProjectConfig:
    """Test the ProjectConfig class."""
    
    def test_dict_interface(self, temp_project_dir: Path):
        """Test that ProjectConfig behaves like a dictionary."""
        config_data = {'key1': 'value1', 'key2': 42}
        config = ProjectConfig(config_data, temp_project_dir)
        
        # Test dictionary access
        assert config['key1'] == 'value1'
        assert config['key2'] == 42
        
        # Test dictionary methods
        assert config.get('key1') == 'value1'
        assert config.get('nonexistent', 'default') == 'default'
        assert len(config) == 2
        assert list(config.keys()) == ['key1', 'key2']
        assert list(config.values()) == ['value1', 42]
        
        # Test modification
        config['key3'] = 'value3'
        assert config['key3'] == 'value3'
        
        config.update({'key4': 'value4'})
        assert config['key4'] == 'value4'
    
    def test_project_root_property(self, temp_project_dir: Path):
        """Test the project_root property."""
        config = ProjectConfig({}, temp_project_dir)
        assert config.project_root == str(temp_project_dir)
    
    def test_path_helpers(self, temp_project_dir: Path):
        """Test path helper methods."""
        config = ProjectConfig({}, temp_project_dir)
        
        # Test directory creation
        data_dir = config.data_path()
        assert data_dir == str(temp_project_dir / 'data')
        assert Path(data_dir).exists()
        
        # Test file path creation
        db_file = config.data_path('test.db')
        assert db_file == str(temp_project_dir / 'data' / 'test.db')
        assert Path(db_file).parent.exists()
        
        # Test different directory names
        logs_dir = config.logs_path()
        assert logs_dir == str(temp_project_dir / 'logs')
        
        cache_file = config.cache_path('cache.json')
        assert cache_file == str(temp_project_dir / 'cache' / 'cache.json')
    
    def test_path_helper_error_handling(self, temp_project_dir: Path):
        """Test error handling for invalid path helper calls."""
        config = ProjectConfig({}, temp_project_dir)
        
        # Should raise AttributeError for non-_path methods
        with pytest.raises(AttributeError) as exc_info:
            config.data('file.db')
        
        assert "Did you mean 'data_path'?" in str(exc_info.value)
        assert "Only *_path methods are supported" in str(exc_info.value)
        
        with pytest.raises(AttributeError):
            config.nonexistent_method
    
    def test_copy(self, temp_project_dir: Path):
        """Test the copy method."""
        original_data = {'key1': 'value1', 'key2': 42}
        config = ProjectConfig(original_data, temp_project_dir)
        
        # Create a copy
        config_copy = config.copy()
        
        # Verify it's a separate object
        assert config_copy is not config
        assert isinstance(config_copy, ProjectConfig)
        
        # Verify data is copied
        assert config_copy['key1'] == 'value1'
        assert config_copy['key2'] == 42
        
        # Verify path helpers work
        assert config_copy.data_path() == str(temp_project_dir / 'data')
        
        # Verify modifications don't affect original
        config_copy['key3'] = 'value3'
        assert 'key3' not in config


class TestProjectRootDetection:
    """Test project root detection functionality."""
    
    def test_find_project_root_with_git(self):
        """Test finding project root with .git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            git_dir = project_path / '.git'
            git_dir.mkdir()
            
            # Create nested directory
            nested_dir = project_path / 'src' / 'package'
            nested_dir.mkdir(parents=True)
            
            # Should find project root from nested directory
            root = _find_project_root(nested_dir)
            assert root.resolve() == project_path.resolve()
    
    def test_find_project_root_with_pyproject_toml(self):
        """Test finding project root with pyproject.toml."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / 'pyproject.toml').touch()
            
            nested_dir = project_path / 'deep' / 'nested' / 'dir'
            nested_dir.mkdir(parents=True)
            
            root = _find_project_root(nested_dir)
            assert root.resolve() == project_path.resolve()
    
    def test_find_project_root_fallback(self):
        """Test fallback to current directory when no markers found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_dir = Path(temp_dir) / 'empty'
            empty_dir.mkdir()
            
            # Should fallback to current working directory
            root = _find_project_root(empty_dir)
            assert root == Path.cwd()


class TestEnvFileLoading:
    """Test .env file loading functionality."""
    
    def test_load_env_file(self, temp_project_dir: Path, create_env_file):
        """Test loading environment variables from .env file."""
        env_vars = _load_env_file(temp_project_dir)
        
        assert env_vars['database_url'] == 'postgresql://localhost/prod'
        assert env_vars['debug'] == 'true'
        assert env_vars['max_workers'] == '8'
        assert env_vars['timeout'] == '60.0'
        assert env_vars['api_key'] == 'secret-key-123'
        assert env_vars['features'] == '["auth", "cache", "admin"]'
        assert env_vars['quoted_value'] == 'quoted string'
        assert env_vars['single_quoted'] == 'single quoted'
    
    def test_load_env_file_nonexistent(self, temp_project_dir: Path):
        """Test loading from non-existent .env file."""
        env_vars = _load_env_file(temp_project_dir)
        assert env_vars == {}
    
    def test_load_env_file_malformed(self, temp_project_dir: Path):
        """Test loading from malformed .env file."""
        env_file = temp_project_dir / '.env'
        env_file.write_text("malformed content without equals")
        
        env_vars = _load_env_file(temp_project_dir)
        assert env_vars == {}


class TestValueConversion:
    """Test environment variable value conversion."""
    
    def test_convert_string_values(self):
        """Test string value conversion."""
        assert _convert_value('hello', 'default') == 'hello'
        assert _convert_value('123', 'default') == '123'
    
    def test_convert_boolean_values(self):
        """Test boolean value conversion."""
        assert _convert_value('true', False) is True
        assert _convert_value('True', False) is True
        assert _convert_value('1', False) is True
        assert _convert_value('yes', False) is True
        assert _convert_value('on', False) is True
        
        assert _convert_value('false', True) is False
        assert _convert_value('0', True) is False
        assert _convert_value('no', True) is False
        assert _convert_value('off', True) is False
    
    def test_convert_integer_values(self):
        """Test integer value conversion."""
        assert _convert_value('42', 0) == 42
        assert _convert_value('-10', 0) == -10
        assert _convert_value('invalid', 5) == 5  # Fallback to default
    
    def test_convert_float_values(self):
        """Test float value conversion."""
        assert _convert_value('3.14', 0.0) == 3.14
        assert _convert_value('-2.5', 0.0) == -2.5
        assert _convert_value('invalid', 1.0) == 1.0  # Fallback to default
    
    def test_convert_list_values(self):
        """Test list value conversion."""
        # JSON array
        assert _convert_value('["a", "b", "c"]', []) == ["a", "b", "c"]
        assert _convert_value('[1, 2, 3]', []) == [1, 2, 3]
        
        # Single value becomes single-item list
        assert _convert_value('single', []) == ['single']
        
        # Invalid JSON becomes single-item list
        assert _convert_value('[invalid json', []) == ['[invalid json']


class TestGlobalConfiguration:
    """Test global configuration management."""
    
    def test_setup_and_get_config(self, temp_project_dir: Path, sample_defaults: Dict[str, Any]):
        """Test basic setup and retrieval of global configuration."""
        setup(sample_defaults, temp_project_dir)
        
        config = get_config()
        assert isinstance(config, ProjectConfig)
        assert config['database_url'] == 'sqlite:///test.db'
        assert config['debug'] is False
        assert config['max_workers'] == 4
        assert Path(config.project_root).resolve() == temp_project_dir.resolve()
    
    def test_get_config_before_setup(self):
        """Test that get_config raises error before setup."""
        with pytest.raises(RuntimeError) as exc_info:
            get_config()
        
        assert "Configuration not initialized" in str(exc_info.value)
        assert "Call setup(defaults) first" in str(exc_info.value)
    
    def test_environment_variable_override(self, temp_project_dir: Path, sample_defaults: Dict[str, Any], mock_env_vars):
        """Test environment variable override of defaults."""
        mock_env_vars({
            'DATABASE_URL': 'postgresql://localhost/prod',
            'DEBUG': 'true',
            'MAX_WORKERS': '8',
            'TIMEOUT': '60.0'
        })
        
        setup(sample_defaults, temp_project_dir)
        config = get_config()
        
        assert config['database_url'] == 'postgresql://localhost/prod'
        assert config['debug'] is True
        assert config['max_workers'] == 8
        assert config['timeout'] == 60.0
    
    def test_env_file_override(self, temp_project_dir: Path, sample_defaults: Dict[str, Any], create_env_file):
        """Test .env file override of defaults."""
        setup(sample_defaults, temp_project_dir)
        config = get_config()
        
        assert config['database_url'] == 'postgresql://localhost/prod'
        assert config['debug'] is True
        assert config['max_workers'] == 8
        assert config['timeout'] == 60.0
        assert config['api_key'] == 'secret-key-123'
    
    def test_project_root_from_env(self, sample_defaults: Dict[str, Any], mock_env_vars):
        """Test PROJECT_ROOT environment variable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_env_vars({'PROJECT_ROOT': temp_dir})
            
            setup(sample_defaults)
            config = get_config()
            
            assert Path(config.project_root).resolve() == Path(temp_dir).resolve()

    def test_runtime_modification(self, temp_project_dir: Path, sample_defaults: Dict[str, Any]):
        """Test runtime modification of configuration."""
        setup(sample_defaults, temp_project_dir)
        config = get_config()

        # Test dictionary-style modification
        config['new_setting'] = 'new_value'
        assert config['new_setting'] == 'new_value'

        # Test bulk update
        config.update({
            'debug': True,
            'max_workers': 16,
            'runtime_setting': 'added'
        })

        assert config['debug'] is True
        assert config['max_workers'] == 16
        assert config['runtime_setting'] == 'added'

        # Verify changes persist in global config
        config2 = get_config()
        assert config2['new_setting'] == 'new_value'
        assert config2['runtime_setting'] == 'added'
