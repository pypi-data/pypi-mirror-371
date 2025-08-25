#!/usr/bin/env python3
"""
Basic usage example for project-conf.

This example demonstrates the core functionality of project-conf:
- Setting up configuration with defaults
- Dictionary-style access and modification
- Path helpers for file and directory management
- Environment variable integration
"""

from project_conf import setup, get_config


def main():
    print("🚀 project-conf Basic Usage Example")
    print("=" * 50)
    
    # 1. Setup configuration with defaults
    print("\n1️⃣ Setting up configuration...")
    setup({
        'database_url': 'sqlite:///myapp.db',
        'debug': False,
        'max_workers': 4,
        'timeout': 30.0,
        'api_key': '',
        'features': ['auth', 'cache'],
        'log_level': 'INFO'
    })
    
    # 2. Get the global configuration object
    config = get_config()
    print(f"   ✅ Configuration initialized")
    print(f"   📁 Project root: {config.project_root}")
    
    # 3. Dictionary-style access
    print("\n2️⃣ Dictionary-style access:")
    print(f"   config['database_url'] = {config['database_url']}")
    print(f"   config.get('debug', True) = {config.get('debug', True)}")
    print(f"   config.get('nonexistent', 'default') = {config.get('nonexistent', 'default')}")
    
    # 4. Dictionary methods
    print(f"   len(config) = {len(config)}")
    print(f"   'debug' in config = {'debug' in config}")
    
    # 5. Runtime modification
    print("\n3️⃣ Runtime modification:")
    original_debug = config['debug']
    config['debug'] = True
    config['new_setting'] = 'added at runtime'
    
    print(f"   Changed debug: {original_debug} -> {config['debug']}")
    print(f"   Added new setting: {config['new_setting']}")
    
    # 6. Bulk updates
    config.update({
        'max_workers': 8,
        'timeout': 60.0,
        'cache_enabled': True
    })
    print(f"   After bulk update: workers={config['max_workers']}, timeout={config['timeout']}")
    
    # 7. Path helpers
    print("\n4️⃣ Path helpers:")
    
    # Directory paths (creates directories automatically)
    data_dir = config.data_path()
    logs_dir = config.logs_path()
    cache_dir = config.cache_path()
    
    print(f"   config.data_path() = {data_dir}")
    print(f"   config.logs_path() = {logs_dir}")
    print(f"   config.cache_path() = {cache_dir}")
    
    # File paths (creates parent directories)
    db_file = config.data_path('myapp.db')
    log_file = config.logs_path('application.log')
    cache_file = config.cache_path('session.json')
    
    print(f"   config.data_path('myapp.db') = {db_file}")
    print(f"   config.logs_path('application.log') = {log_file}")
    print(f"   config.cache_path('session.json') = {cache_file}")
    
    # Custom directory names
    uploads_dir = config.uploads_path()
    models_file = config.models_path('gpt4.bin')
    
    print(f"   config.uploads_path() = {uploads_dir}")
    print(f"   config.models_path('gpt4.bin') = {models_file}")
    
    # 8. Show final configuration state
    print("\n5️⃣ Final configuration state:")
    for key, value in sorted(config.items()):
        if isinstance(value, str) and len(value) > 40:
            print(f"   {key}: {value[:37]}...")
        else:
            print(f"   {key}: {value}")
    
    # 9. Demonstrate global nature
    print("\n6️⃣ Global configuration:")
    config2 = get_config()
    print(f"   Same object? {config is config2}")
    print(f"   config2['new_setting'] = {config2['new_setting']}")
    
    print("\n✅ Basic usage example completed!")
    print("\n💡 Try setting environment variables and running again:")
    print("   export DEBUG=true")
    print("   export MAX_WORKERS=16")
    print("   export DATABASE_URL=postgresql://localhost/prod")


if __name__ == "__main__":
    main()
