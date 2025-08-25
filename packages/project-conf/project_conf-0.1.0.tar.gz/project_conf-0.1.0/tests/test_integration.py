"""
Integration tests for project-conf.
"""

import tempfile
from pathlib import Path
import pytest

from project_conf import setup, get_config


class TestIntegration:
    """Integration tests that test the full workflow."""
    
    def test_real_world_usage(self):
        """Test a realistic usage scenario."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create project structure
            (project_path / '.git').mkdir()
            (project_path / 'src').mkdir()
            (project_path / 'data').mkdir()
            
            # Create .env file
            env_content = """
DATABASE_URL=postgresql://localhost/myapp
DEBUG=false
MAX_WORKERS=8
REDIS_URL=redis://localhost:6379
API_KEY=prod-key-123
FEATURES=["auth", "admin", "analytics"]
"""
            (project_path / '.env').write_text(env_content)
            
            # Setup configuration
            defaults = {
                'database_url': 'sqlite:///dev.db',
                'debug': True,
                'max_workers': 2,
                'redis_url': 'redis://localhost:6379',
                'api_key': '',
                'features': ['auth'],
                'log_level': 'INFO'
            }
            
            setup(defaults, project_path)
            config = get_config()
            
            # Verify environment overrides work
            assert config['database_url'] == 'postgresql://localhost/myapp'
            assert config['debug'] is False
            assert config['max_workers'] == 8
            assert config['api_key'] == 'prod-key-123'
            assert config['features'] == ['auth', 'admin', 'analytics']
            
            # Verify defaults for non-overridden values
            assert config['log_level'] == 'INFO'
            
            # Test path helpers
            db_path = config.data_path('app.db')
            expected_db_path = project_path / 'data' / 'app.db'
            assert Path(db_path).resolve() == expected_db_path.resolve()
            assert Path(db_path).parent.exists()

            log_path = config.logs_path('app.log')
            expected_log_path = project_path / 'logs' / 'app.log'
            assert Path(log_path).resolve() == expected_log_path.resolve()
            assert Path(log_path).parent.exists()
            
            # Test runtime modifications
            config['cache_enabled'] = True
            config.update({
                'timeout': 30,
                'new_feature': 'enabled'
            })
            
            # Verify modifications persist
            config2 = get_config()
            assert config2['cache_enabled'] is True
            assert config2['timeout'] == 30
            assert config2['new_feature'] == 'enabled'
    
    def test_multiple_path_helpers(self):
        """Test using multiple different path helpers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / '.git').mkdir()
            
            setup({'debug': True}, project_path)
            config = get_config()
            
            # Test various path helpers
            paths = {
                'data': config.data_path('file.db'),
                'logs': config.logs_path('app.log'),
                'cache': config.cache_path('cache.json'),
                'uploads': config.uploads_path('image.jpg'),
                'models': config.models_path('model.bin'),
                'static': config.static_path('style.css'),
                'my_custom_dir': config.my_custom_dir_path('file.txt')
            }
            
            # Verify all paths are correct and directories are created
            for dir_name, file_path in paths.items():
                expected_path = project_path / dir_name / Path(file_path).name
                assert Path(file_path).resolve() == expected_path.resolve()
                assert expected_path.parent.exists()
    
    def test_config_as_dict_in_functions(self):
        """Test passing config to functions that expect dictionaries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / '.git').mkdir()
            
            setup({
                'database_url': 'sqlite:///test.db',
                'debug': True,
                'workers': 4
            }, project_path)
            
            config = get_config()
            
            # Function that expects a dictionary
            def process_config(cfg_dict):
                return {
                    'db': cfg_dict['database_url'],
                    'debug_mode': cfg_dict.get('debug', False),
                    'worker_count': cfg_dict.get('workers', 1),
                    'keys': list(cfg_dict.keys())
                }
            
            # Should work seamlessly as a dictionary
            result = process_config(config)
            
            assert result['db'] == 'sqlite:///test.db'
            assert result['debug_mode'] is True
            assert result['worker_count'] == 4
            assert 'database_url' in result['keys']
            assert 'debug' in result['keys']
            assert 'workers' in result['keys']
    
    def test_config_serialization(self):
        """Test that config can be serialized/deserialized."""
        import json
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / '.git').mkdir()
            
            setup({
                'database_url': 'sqlite:///test.db',
                'debug': True,
                'workers': 4,
                'features': ['auth', 'cache']
            }, project_path)
            
            config = get_config()
            
            # Should be serializable as JSON (since it's a dict)
            config_dict = dict(config)
            json_str = json.dumps(config_dict)
            
            # Should be deserializable
            restored_dict = json.loads(json_str)
            
            assert restored_dict['database_url'] == 'sqlite:///test.db'
            assert restored_dict['debug'] is True
            assert restored_dict['workers'] == 4
            assert restored_dict['features'] == ['auth', 'cache']
    
    def test_error_handling_edge_cases(self):
        """Test error handling in edge cases."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / '.git').mkdir()
            
            # Test with empty defaults
            setup({}, project_path)
            config = get_config()
            
            # Should still have project_root
            assert 'project_root' in config
            assert Path(config.project_root).resolve() == project_path.resolve()

            # Path helpers should still work
            data_path = config.data_path('test.txt')
            expected_data_path = project_path / 'data' / 'test.txt'
            assert Path(data_path).resolve() == expected_data_path.resolve()
            
            # Test invalid path helper names
            with pytest.raises(AttributeError):
                config.invalid_method()
            
            with pytest.raises(AttributeError):
                config.data('file.txt')  # Missing _path suffix
