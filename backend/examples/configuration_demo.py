#!/usr/bin/env python3
"""
Configuration Management System Demo

This example demonstrates the unified configuration management system
including hierarchical loading, service-specific configuration generation,
and hot reloading capabilities.

Run this demo to see the configuration system in action.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.configuration_manager import (
    ConfigurationManager,
    ConfigurationChangeEvent,
    initialize_configuration
)
from app.core.service_config_generator import (
    ServiceConfigGenerator,
    ServiceDefinition,
    ServiceType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_demo_project():
    """Create a demo project structure with configuration files"""
    import tempfile
    
    temp_dir = Path(tempfile.mkdtemp(prefix="config_demo_"))
    print(f"Creating demo project in: {temp_dir}")
    
    # Create directory structure
    (temp_dir / "frontend").mkdir()
    (temp_dir / "backend").mkdir()
    (temp_dir / "services").mkdir()
    
    # Create root .env file
    (temp_dir / ".env").write_text("""
# Global Configuration
JWT_SECRET=demo_jwt_secret_32_characters_long
SECRET_KEY=demo_secret_key_32_characters_long
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=demo_db
POSTGRES_USER=demo_user
POSTGRES_PASSWORD=demo_postgres_password_12345678
REDIS_HOST=localhost
REDIS_PORT=6379
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=demo_neo4j_password_12345678
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
""".strip())
    
    # Create frontend .env.local
    (temp_dir / "frontend" / ".env.local").write_text("""
# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=demo_nextauth_secret_32_characters
NODE_ENV=development
FRONTEND_PORT=3000
""".strip())
    
    # Create backend .env
    (temp_dir / "backend" / ".env").write_text("""
# Backend Configuration
POSTGRES_PASSWORD=backend_postgres_password_12345678
NEO4J_PASSWORD=backend_neo4j_password_12345678
BACKEND_PORT=8000
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
""".strip())
    
    # Create environment-specific file
    (temp_dir / ".env.development").write_text("""
# Development Environment Overrides
DEBUG=true
LOG_LEVEL=DEBUG
RATE_LIMIT_PER_MINUTE=1000
""".strip())
    
    return temp_dir


def demo_configuration_loading(project_path: Path):
    """Demo: Configuration loading and hierarchical precedence"""
    print("\n" + "="*60)
    print("DEMO 1: Configuration Loading and Hierarchical Precedence")
    print("="*60)
    
    # Create configuration manager
    config_manager = ConfigurationManager(project_path)
    
    # Load configuration
    print("Loading configuration for development environment...")
    config = config_manager.load_configuration("development")
    
    print(f"✅ Loaded {len(config)} configuration entries")
    
    # Show configuration summary
    summary = config_manager.get_configuration_summary()
    print(f"\nConfiguration Summary:")
    print(f"  - Total entries: {summary['total_entries']}")
    print(f"  - Conflicts resolved: {summary['conflicts_resolved']}")
    print(f"  - Sources: {summary['sources']}")
    print(f"  - Secret keys: {summary['secret_keys']}")
    
    # Show some key values and their sources
    print(f"\nKey Configuration Values:")
    interesting_keys = [
        "POSTGRES_PASSWORD",  # Should be from backend/.env (service-specific)
        "DEBUG",              # Should be from .env.development (environment-specific)
        "JWT_SECRET",         # Should be from root .env (global)
        "NEXT_PUBLIC_API_URL" # Should be from frontend/.env.local (service-specific)
    ]
    
    for key in interesting_keys:
        if key in config_manager.configurations:
            entry = config_manager.configurations[key]
            masked_value = config_manager._mask_secret(key, entry.value)
            print(f"  - {key}: {masked_value} (from {entry.source.name})")
    
    # Show conflicts if any
    if config_manager.conflicts:
        print(f"\nResolved Conflicts ({len(config_manager.conflicts)}):")
        for conflict in config_manager.conflicts:
            print(f"  - {conflict.key}: {conflict.resolution_reason}")
    
    return config_manager


def demo_service_configuration(config_manager: ConfigurationManager):
    """Demo: Service-specific configuration generation"""
    print("\n" + "="*60)
    print("DEMO 2: Service-Specific Configuration Generation")
    print("="*60)
    
    # Create service configuration generator
    service_generator = ServiceConfigGenerator(config_manager)
    
    # Generate frontend configuration
    print("Generating frontend service configuration...")
    frontend_config = service_generator.generate_service_config("frontend")
    
    print(f"✅ Frontend configuration generated")
    print(f"  - Service: {frontend_config.service_name}")
    print(f"  - Configuration keys: {len(frontend_config.config)}")
    print(f"  - Dependencies: {frontend_config.dependencies}")
    
    print(f"\nFrontend Configuration Keys:")
    for key, value in sorted(frontend_config.config.items()):
        masked_value = service_generator._mask_secrets({key: value})[key]
        print(f"  - {key}: {masked_value}")
    
    # Generate backend configuration
    print(f"\nGenerating backend service configuration...")
    backend_config = service_generator.generate_service_config("backend")
    
    print(f"✅ Backend configuration generated")
    print(f"  - Service: {backend_config.service_name}")
    print(f"  - Configuration keys: {len(backend_config.config)}")
    print(f"  - Dependencies: {backend_config.dependencies}")
    
    print(f"\nBackend Configuration Keys:")
    for key, value in sorted(backend_config.config.items()):
        masked_value = service_generator._mask_secrets({key: value})[key]
        print(f"  - {key}: {masked_value}")
    
    # Show service isolation
    print(f"\nService Isolation Verification:")
    frontend_keys = set(frontend_config.config.keys())
    backend_keys = set(backend_config.config.keys())
    
    frontend_only = frontend_keys - backend_keys
    backend_only = backend_keys - frontend_keys
    shared_keys = frontend_keys & backend_keys
    
    print(f"  - Frontend-only keys: {len(frontend_only)} ({', '.join(sorted(list(frontend_only)[:5]))}...)")
    print(f"  - Backend-only keys: {len(backend_only)} ({', '.join(sorted(list(backend_only)[:5]))}...)")
    print(f"  - Shared keys: {len(shared_keys)} ({', '.join(sorted(shared_keys))})")
    
    return service_generator


def demo_configuration_export(service_generator: ServiceConfigGenerator):
    """Demo: Configuration export in different formats"""
    print("\n" + "="*60)
    print("DEMO 3: Configuration Export in Different Formats")
    print("="*60)
    
    # Export frontend config as .env format
    print("Exporting frontend configuration as .env format:")
    env_content = service_generator.export_service_config("frontend", format="env", mask_secrets=True)
    print("```")
    print(env_content[:300] + "..." if len(env_content) > 300 else env_content)
    print("```")
    
    # Export backend config as JSON format
    print(f"\nExporting backend configuration as JSON format:")
    json_content = service_generator.export_service_config("backend", format="json", mask_secrets=True)
    print("```json")
    print(json_content[:300] + "..." if len(json_content) > 300 else json_content)
    print("```")


def demo_change_propagation(config_manager: ConfigurationManager, service_generator: ServiceConfigGenerator):
    """Demo: Configuration change propagation"""
    print("\n" + "="*60)
    print("DEMO 4: Configuration Change Propagation")
    print("="*60)
    
    # Track change events
    change_events = []
    
    def track_changes(event: ConfigurationChangeEvent):
        change_events.append(event)
        print(f"  📢 Configuration change: {event.key} = {config_manager._mask_secret(event.key, event.new_value)}")
    
    def track_service_changes(service_name: str, event: ConfigurationChangeEvent):
        print(f"  🔄 Service {service_name} notified of change: {event.key}")
    
    # Add change listeners
    config_manager.add_change_listener(track_changes)
    service_generator.add_propagation_callback("frontend", track_service_changes)
    service_generator.add_propagation_callback("backend", track_service_changes)
    
    print("Setting up change listeners...")
    print("Making configuration changes...")
    
    # Update some configuration values
    updates = {
        "NEXT_PUBLIC_API_URL": "http://localhost:9000/api/v1",
        "JWT_SECRET": "updated_jwt_secret_32_characters_long",
        "DEBUG": "false"
    }
    
    config_manager.update_configuration(updates)
    
    print(f"\n✅ Configuration updates completed")
    print(f"  - Updates made: {len(updates)}")
    print(f"  - Change events fired: {len(change_events)}")
    
    # Show update queue
    if service_generator.update_queue:
        print(f"\nUpdate Queue ({len(service_generator.update_queue)} entries):")
        for update in service_generator.update_queue[-3:]:  # Show last 3
            print(f"  - {update.service_name}: {list(update.updated_keys.keys())} ({update.propagation_status})")


def demo_hot_reloading(config_manager: ConfigurationManager, project_path: Path):
    """Demo: Hot reloading capabilities"""
    print("\n" + "="*60)
    print("DEMO 5: Hot Reloading Capabilities")
    print("="*60)
    
    print("Enabling hot reloading...")
    config_manager.enable_hot_reloading()
    
    print("✅ Hot reloading enabled")
    print("  - Configuration files are now being monitored")
    print("  - Changes will be automatically detected and applied")
    
    # Simulate a file change
    print(f"\nSimulating configuration file change...")
    env_file = project_path / ".env"
    original_content = env_file.read_text()
    
    # Add a new configuration key
    new_content = original_content + "\nNEW_DEMO_KEY=demo_value_added_during_hot_reload"
    env_file.write_text(new_content)
    
    print("  - Added NEW_DEMO_KEY to .env file")
    print("  - Hot reload system should detect this change")
    
    # Wait a moment for file watcher to detect change
    time.sleep(2)
    
    # Check if the change was detected
    if "NEW_DEMO_KEY" in config_manager.configurations:
        print("✅ Hot reload successful - new key detected!")
        print(f"  - NEW_DEMO_KEY: {config_manager.configurations['NEW_DEMO_KEY'].value}")
    else:
        print("⚠️  Hot reload may take a moment to detect changes")
    
    # Restore original content
    env_file.write_text(original_content)
    
    print(f"\nDisabling hot reloading...")
    config_manager.disable_hot_reloading()
    print("✅ Hot reloading disabled")


def demo_service_status(service_generator: ServiceConfigGenerator):
    """Demo: Service status and management"""
    print("\n" + "="*60)
    print("DEMO 6: Service Status and Management")
    print("="*60)
    
    # Show all service status
    all_status = service_generator.get_all_service_status()
    
    print(f"Registered Services ({len(all_status)}):")
    for service_name, status in all_status.items():
        active_indicator = "🟢" if status['is_active'] else "🔴"
        print(f"\n{active_indicator} {service_name}")
        print(f"  - Type: {status['type']}")
        print(f"  - Dependencies: {', '.join(status['dependencies']) if status['dependencies'] else 'None'}")
        print(f"  - Required keys: {len(status['required_keys'])}")
        print(f"  - Optional keys: {len(status['optional_keys'])}")
        
        if status['config_file_path']:
            print(f"  - Config file: {status['config_file_path']}")
        
        if status['health_check_url']:
            print(f"  - Health check: {status['health_check_url']}")
    
    # Register a custom service
    print(f"\nRegistering custom service...")
    custom_service = ServiceDefinition(
        name="demo_service",
        service_type=ServiceType.BACKEND,
        required_keys={"DEMO_KEY", "DEMO_SECRET"},
        optional_keys={"DEMO_PORT"},
        key_prefixes=["DEMO_"],
        health_check_url="http://localhost:8080/health"
    )
    
    service_generator.register_service(custom_service)
    
    # Show updated status
    custom_status = service_generator.get_service_status("demo_service")
    print(f"✅ Custom service registered:")
    print(f"  - Name: {custom_status['name']}")
    print(f"  - Type: {custom_status['type']}")
    print(f"  - Required keys: {len(custom_status['required_keys'])}")


def main():
    """Run the configuration management demo"""
    print("Configuration Management System Demo")
    print("=" * 60)
    print("This demo showcases the unified configuration management system")
    print("including hierarchical loading, service-specific generation,")
    print("change propagation, and hot reloading capabilities.")
    
    try:
        # Create demo project
        project_path = create_demo_project()
        
        # Run demos
        config_manager = demo_configuration_loading(project_path)
        service_generator = demo_service_configuration(config_manager)
        demo_configuration_export(service_generator)
        demo_change_propagation(config_manager, service_generator)
        demo_hot_reloading(config_manager, project_path)
        demo_service_status(service_generator)
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY! 🎉")
        print("="*60)
        print("The unified configuration management system provides:")
        print("✅ Hierarchical configuration loading from multiple sources")
        print("✅ Configuration validation and type checking")
        print("✅ Precedence rules for conflicting variables")
        print("✅ Service-specific configuration generation")
        print("✅ Configuration change propagation")
        print("✅ Hot reloading capabilities")
        print("✅ Multiple export formats (env, json, yaml)")
        print("✅ Service status monitoring and management")
        
        print(f"\nDemo project created at: {project_path}")
        print("You can explore the generated configuration files and")
        print("experiment with the CLI tool using this project.")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logger.error(f"Demo failed: {e}")
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)