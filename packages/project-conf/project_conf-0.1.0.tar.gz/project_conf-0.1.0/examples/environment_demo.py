#!/usr/bin/env python3
"""
Environment variable integration demo for project-conf.

This example demonstrates how project-conf handles environment variables
and .env files, including type conversion and precedence rules.
"""

import os
import tempfile
from pathlib import Path
from project_conf import setup, get_config


def create_sample_env_file(project_dir: Path) -> Path:
    """Create a sample .env file for demonstration."""
    env_content = """
# Database Configuration
DATABASE_URL=postgresql://localhost/myapp_prod
REDIS_URL=redis://localhost:6379/1

# Application Settings
DEBUG=false
SECRET_KEY=super-secret-production-key

# Numeric Settings
MAX_WORKERS=8
TIMEOUT=45.5
UPLOAD_MAX_SIZE=20971520

# Boolean Settings
CACHE_ENABLED=true
ANALYTICS_ENABLED=false

# List Settings (JSON format)
FEATURES=["auth", "admin", "analytics", "caching"]
ALLOWED_HOSTS=["localhost", "myapp.com", "api.myapp.com"]

# Nested Configuration (not directly supported, but can be handled)
LOG_LEVEL=WARNING

# Empty and quoted values
EMPTY_VALUE=
QUOTED_VALUE="This is a quoted string"
SINGLE_QUOTED='Single quoted string'

# Comments and malformed lines are ignored
# This is a comment
MALFORMED_LINE_WITHOUT_EQUALS
"""
    
    env_file = project_dir / '.env'
    env_file.write_text(env_content.strip())
    return env_file


def demonstrate_type_conversion():
    """Demonstrate automatic type conversion from environment variables."""
    print("🔄 Type Conversion Demonstration")
    print("-" * 40)
    
    # Setup configuration with various types
    defaults = {
        'string_value': 'default_string',
        'boolean_value': False,
        'integer_value': 10,
        'float_value': 3.14,
        'list_value': ['default'],
        'empty_string': '',
    }
    
    # Set environment variables with string values
    env_vars = {
        'STRING_VALUE': 'env_string',
        'BOOLEAN_VALUE': 'true',
        'INTEGER_VALUE': '42',
        'FLOAT_VALUE': '2.718',
        'LIST_VALUE': '["env", "list", "values"]',
        'EMPTY_STRING': '',
    }
    
    # Temporarily set environment variables
    original_env = {}
    for key, value in env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        setup(defaults)
        config = get_config()
        
        print("Environment Variable -> Converted Value:")
        print(f"  STRING_VALUE='env_string' -> {config['string_value']} ({type(config['string_value']).__name__})")
        print(f"  BOOLEAN_VALUE='true' -> {config['boolean_value']} ({type(config['boolean_value']).__name__})")
        print(f"  INTEGER_VALUE='42' -> {config['integer_value']} ({type(config['integer_value']).__name__})")
        print(f"  FLOAT_VALUE='2.718' -> {config['float_value']} ({type(config['float_value']).__name__})")
        print(f"  LIST_VALUE='[\"env\", \"list\", \"values\"]' -> {config['list_value']} ({type(config['list_value']).__name__})")
        print(f"  EMPTY_STRING='' -> '{config['empty_string']}' ({type(config['empty_string']).__name__})")
        
    finally:
        # Restore original environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value


def demonstrate_boolean_conversion():
    """Demonstrate boolean value conversion from strings."""
    print("\n🔘 Boolean Conversion Examples")
    print("-" * 40)
    
    # Test various boolean representations
    boolean_tests = [
        ('true', True),
        ('True', True),
        ('TRUE', True),
        ('1', True),
        ('yes', True),
        ('on', True),
        ('false', False),
        ('False', False),
        ('FALSE', False),
        ('0', False),
        ('no', False),
        ('off', False),
        ('anything_else', False),
    ]
    
    for env_value, expected in boolean_tests:
        os.environ['TEST_BOOL'] = env_value
        
        setup({'test_bool': True})  # Default is True
        config = get_config()
        
        result = config['test_bool']
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{env_value}' -> {result}")
        
        # Clean up
        os.environ.pop('TEST_BOOL', None)


def demonstrate_precedence():
    """Demonstrate configuration precedence: defaults < .env file < environment variables."""
    print("\n📊 Configuration Precedence Demo")
    print("-" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir)
        
        # Create project markers
        (project_dir / '.git').mkdir()
        
        # Create .env file
        env_file = create_sample_env_file(project_dir)
        print(f"Created .env file: {env_file}")
        
        # Set some environment variables (these should override .env)
        os.environ['DEBUG'] = 'true'  # Override .env value (false)
        os.environ['MAX_WORKERS'] = '16'  # Override .env value (8)
        
        try:
            # Setup with defaults
            defaults = {
                'database_url': 'sqlite:///default.db',  # Should be overridden by .env
                'debug': True,                           # Should be overridden by env var
                'max_workers': 2,                        # Should be overridden by env var
                'timeout': 30.0,                         # Should be overridden by .env
                'secret_key': 'default-secret',          # Should be overridden by .env
                'new_setting': 'only_in_defaults',       # Should remain as default
            }
            
            setup(defaults, project_dir)
            config = get_config()
            
            print("\nConfiguration Sources and Final Values:")
            print("  Setting              | Default           | .env File         | Env Var    | Final Value")
            print("  " + "-" * 85)
            
            test_cases = [
                ('database_url', 'sqlite:///default.db', 'postgresql://localhost/myapp_prod', None),
                ('debug', True, 'false', 'true'),
                ('max_workers', 2, '8', '16'),
                ('timeout', 30.0, '45.5', None),
                ('secret_key', 'default-secret', 'super-secret-production-key', None),
                ('new_setting', 'only_in_defaults', None, None),
            ]
            
            for setting, default, env_file_val, env_var_val in test_cases:
                final_val = config[setting]
                
                # Format values for display
                default_str = str(default)[:15] + "..." if len(str(default)) > 15 else str(default)
                env_file_str = str(env_file_val)[:15] + "..." if env_file_val and len(str(env_file_val)) > 15 else str(env_file_val or '-')
                env_var_str = str(env_var_val)[:8] + "..." if env_var_val and len(str(env_var_val)) > 8 else str(env_var_val or '-')
                final_str = str(final_val)[:15] + "..." if len(str(final_val)) > 15 else str(final_val)
                
                print(f"  {setting:<18} | {default_str:<17} | {env_file_str:<17} | {env_var_str:<10} | {final_str}")
            
            print(f"\n📋 Precedence Rules:")
            print(f"  1. Defaults (lowest priority)")
            print(f"  2. .env file values")
            print(f"  3. Environment variables (highest priority)")
            
        finally:
            # Clean up environment variables
            os.environ.pop('DEBUG', None)
            os.environ.pop('MAX_WORKERS', None)


def demonstrate_env_file_features():
    """Demonstrate .env file parsing features."""
    print("\n📄 .env File Features Demo")
    print("-" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir)
        (project_dir / '.git').mkdir()
        
        # Create .env file with various formats
        env_content = """
# Comments are ignored
SIMPLE_VALUE=hello

# Quoted values
DOUBLE_QUOTED="This is double quoted"
SINGLE_QUOTED='This is single quoted'

# Empty values
EMPTY_VALUE=
EMPTY_QUOTED=""

# Values with spaces
SPACED_VALUE=  value with spaces  

# Special characters
SPECIAL_CHARS=value!@#$%^&*()

# JSON arrays
JSON_ARRAY=["item1", "item2", "item3"]

# Boolean-like values
BOOL_TRUE=true
BOOL_FALSE=false
BOOL_YES=yes
BOOL_NO=no

# Numeric values
INTEGER=42
FLOAT=3.14159

# Lines without equals are ignored
This line will be ignored
# So will this comment
"""
        
        env_file = project_dir / '.env'
        env_file.write_text(env_content)
        
        # Setup configuration
        defaults = {
            'simple_value': 'default',
            'double_quoted': 'default',
            'single_quoted': 'default',
            'empty_value': 'default',
            'empty_quoted': 'default',
            'spaced_value': 'default',
            'special_chars': 'default',
            'json_array': [],
            'bool_true': False,
            'bool_false': True,
            'bool_yes': False,
            'bool_no': True,
            'integer': 0,
            'float': 0.0,
        }
        
        setup(defaults, project_dir)
        config = get_config()
        
        print("Parsed .env file values:")
        for key in defaults.keys():
            value = config[key]
            value_type = type(value).__name__
            print(f"  {key}: {value} ({value_type})")


def main():
    """Main demonstration function."""
    print("🌐 project-conf Environment Integration Demo")
    print("=" * 60)
    
    demonstrate_type_conversion()
    demonstrate_boolean_conversion()
    demonstrate_precedence()
    demonstrate_env_file_features()
    
    print("\n✅ Environment integration demo completed!")
    print("\n💡 Key takeaways:")
    print("  • Environment variables automatically override defaults")
    print("  • .env files provide a middle layer of configuration")
    print("  • Type conversion is automatic based on default types")
    print("  • Boolean conversion supports many common formats")
    print("  • JSON arrays in environment variables are parsed automatically")


if __name__ == "__main__":
    main()
