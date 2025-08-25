#!/usr/bin/env python3
"""
Web application example using project-conf.

This example shows how to use project-conf in a realistic web application
with multiple modules that need configuration access.
"""

import os
import tempfile
from pathlib import Path
from project_conf import setup, get_config


# =============================================================================
# Configuration Setup Module
# =============================================================================

def initialize_config():
    """Initialize application configuration."""
    
    # Define application defaults
    defaults = {
        'database_url': 'sqlite:///webapp.db',
        'redis_url': 'redis://localhost:6379',
        'debug': False,
        'secret_key': 'dev-secret-key',
        'max_workers': 4,
        'timeout': 30.0,
        'api_key': '',
        'log_level': 'INFO',
        'features': {
            'auth': True,
            'admin': False,
            'analytics': True,
            'caching': True
        },
        'upload_max_size': 10485760,  # 10MB
        'session_timeout': 3600       # 1 hour
    }
    
    # Setup configuration (will auto-detect project root)
    setup(defaults)
    
    print("✅ Web application configuration initialized")
    return get_config()


# =============================================================================
# Database Module
# =============================================================================

def setup_database():
    """Setup database connection using configuration."""
    config = get_config()
    
    # Get database configuration
    db_url = config['database_url']
    timeout = config.get('timeout', 30)
    
    print(f"🗄️ Setting up database connection:")
    print(f"   URL: {db_url}")
    print(f"   Timeout: {timeout}s")
    
    # Use path helper for SQLite databases
    if 'sqlite' in db_url:
        # Get actual file path using path helper
        db_file = config.data_path('webapp.db')
        actual_url = f"sqlite:///{db_file}"
        
        print(f"   SQLite file: {db_file}")
        
        # Update config with actual database path
        config['actual_database_path'] = db_file
        
        return f"Database connection: {actual_url}"
    else:
        return f"Database connection: {db_url}"


def backup_database():
    """Create database backup."""
    config = get_config()
    
    # Use path helper for backup location
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = config.backups_path(f"webapp_backup_{timestamp}.sql")
    
    print(f"💾 Creating database backup: {backup_file}")
    
    # Simulate backup process
    Path(backup_file).touch()
    
    return backup_file


# =============================================================================
# Web Server Module
# =============================================================================

def create_web_app():
    """Create and configure web application."""
    config = get_config()
    
    # Get web server configuration
    debug = config['debug']
    secret_key = config['secret_key']
    
    print(f"🌐 Creating web application:")
    print(f"   Debug mode: {debug}")
    print(f"   Secret key: {'*' * len(secret_key) if secret_key else 'NOT SET'}")
    
    # Setup static and upload directories using path helpers
    static_dir = config.static_path()
    uploads_dir = config.uploads_path()
    templates_dir = config.templates_path()
    
    print(f"   Static files: {static_dir}")
    print(f"   Upload directory: {uploads_dir}")
    print(f"   Templates: {templates_dir}")
    
    # Runtime configuration based on environment
    if not config.get('api_key'):
        if debug:
            config['api_key'] = 'development-api-key-123'
            print("   ⚠️ Using development API key")
        else:
            print("   ❌ No API key configured for production!")
    
    # Configure upload limits
    max_size = config['upload_max_size']
    print(f"   Max upload size: {max_size / 1024 / 1024:.1f}MB")
    
    app_config = {
        'debug': debug,
        'secret_key': config['secret_key'],
        'static_folder': static_dir,
        'upload_folder': uploads_dir,
        'templates_folder': templates_dir,
        'max_content_length': max_size
    }
    
    return f"WebApp({app_config})"


def setup_logging():
    """Setup application logging."""
    config = get_config()
    
    # Get logging configuration
    log_level = config.get('log_level', 'INFO')
    debug = config['debug']
    
    # Use path helpers for log files
    app_log = config.logs_path('webapp.log')
    error_log = config.logs_path('errors.log')
    access_log = config.logs_path('access.log')
    
    print(f"📝 Setting up logging:")
    print(f"   Level: {log_level}")
    print(f"   App log: {app_log}")
    print(f"   Error log: {error_log}")
    print(f"   Access log: {access_log}")
    
    # Update config with log file paths
    config.update({
        'log_files': {
            'app': app_log,
            'error': error_log,
            'access': access_log
        }
    })
    
    return f"Logging configured: level={log_level}"


# =============================================================================
# Worker/Task Module
# =============================================================================

def start_background_workers():
    """Start background worker processes."""
    config = get_config()
    
    # Get worker configuration
    max_workers = config['max_workers']
    redis_url = config['redis_url']
    
    print(f"🏃 Starting background workers:")
    print(f"   Max workers: {max_workers}")
    print(f"   Redis URL: {redis_url}")
    
    # Use path helper for worker PID files
    pids_dir = config.pids_path()
    print(f"   PID files: {pids_dir}")
    
    # Simulate load-based scaling
    import random
    current_load = random.random()
    
    if current_load > 0.7:
        # Scale up for high load
        scaled_workers = min(max_workers * 2, 16)
        config['current_workers'] = scaled_workers
        print(f"   📈 High load detected, scaling to {scaled_workers} workers")
    else:
        config['current_workers'] = max_workers
        print(f"   📊 Normal load, using {max_workers} workers")
    
    return f"WorkerPool(workers={config['current_workers']}, redis={redis_url})"


# =============================================================================
# Feature Management
# =============================================================================

def configure_features():
    """Configure application features based on settings."""
    config = get_config()
    
    features = config.get('features', {})
    
    print(f"🎯 Configuring features:")
    
    enabled_features = []
    for feature, enabled in features.items():
        status = "✅" if enabled else "❌"
        print(f"   {status} {feature}: {enabled}")
        if enabled:
            enabled_features.append(feature)
    
    # Runtime feature toggles based on environment
    if config['debug']:
        # Enable admin panel in debug mode
        if not features.get('admin'):
            config['features']['admin'] = True
            enabled_features.append('admin')
            print("   🔧 Enabled admin panel for debug mode")
    
    config['enabled_features'] = enabled_features
    return enabled_features


# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main web application startup."""
    print("🚀 Starting Web Application with project-conf")
    print("=" * 60)
    
    # 1. Initialize configuration
    config = initialize_config()
    print(f"   Project root: {config.project_root}")
    
    # 2. Show initial configuration
    print(f"\n📋 Initial configuration:")
    important_keys = ['database_url', 'debug', 'max_workers', 'log_level']
    for key in important_keys:
        print(f"   {key}: {config[key]}")
    
    # 3. Initialize application components
    print(f"\n🏗️ Initializing components:")
    
    db_conn = setup_database()
    print(f"   Database: {db_conn}")
    
    web_app = create_web_app()
    print(f"   Web app: {web_app}")
    
    logging_setup = setup_logging()
    print(f"   Logging: {logging_setup}")
    
    worker_pool = start_background_workers()
    print(f"   Workers: {worker_pool}")
    
    enabled_features = configure_features()
    print(f"   Features: {', '.join(enabled_features)}")
    
    # 4. Create a backup
    backup_file = backup_database()
    print(f"   Backup: {backup_file}")
    
    # 5. Show final configuration state
    print(f"\n📊 Final configuration state:")
    final_config = get_config()
    
    # Show key configuration values
    key_configs = [
        'database_url', 'debug', 'current_workers', 'api_key',
        'enabled_features', 'actual_database_path'
    ]
    
    for key in key_configs:
        if key in final_config:
            value = final_config[key]
            if key == 'api_key' and value:
                value = '*' * len(value)
            elif isinstance(value, list) and len(value) > 3:
                value = f"[{', '.join(value[:3])}, ...]"
            print(f"   {key}: {value}")
    
    print(f"\n✅ Web application started successfully!")
    print(f"   Total config keys: {len(final_config)}")
    print(f"   Config is mutable: {id(config) == id(get_config())}")
    
    print(f"\n💡 Try setting environment variables:")
    print(f"   export DEBUG=true")
    print(f"   export MAX_WORKERS=8")
    print(f"   export DATABASE_URL=postgresql://localhost/webapp")


if __name__ == "__main__":
    main()
