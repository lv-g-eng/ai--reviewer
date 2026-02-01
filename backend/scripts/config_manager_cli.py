#!/usr/bin/env python3
"""
Configuration Manager CLI Tool

Command-line interface for the unified configuration management system.
Provides commands for loading, validating, generating, and managing configurations.

Usage:
    python config_manager_cli.py load --environment development
    python config_manager_cli.py validate
    python config_manager_cli.py generate --service frontend --format env
    python config_manager_cli.py export --service backend --output backend.env
    python config_manager_cli.py status
    python config_manager_cli.py watch --enable

Validates Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

# Add the parent directory to the path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.configuration_manager import (
    ConfigurationManager,
    get_configuration_manager,
    initialize_configuration
)
from app.core.service_config_generator import (
    ServiceConfigGenerator,
    get_service_config_generator,
    generate_service_configuration,
    export_service_configuration
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConfigManagerCLI:
    """Command-line interface for configuration management"""
    
    def __init__(self):
        self.config_manager: Optional[ConfigurationManager] = None
        self.service_generator: Optional[ServiceConfigGenerator] = None
    
    def setup_managers(self, project_path: Optional[str] = None):
        """Setup configuration managers"""
        if project_path:
            project_path = Path(project_path)
            self.config_manager = ConfigurationManager(project_path)
        else:
            self.config_manager = get_configuration_manager()
        
        self.service_generator = get_service_config_generator()
    
    def load_configuration(self, environment: str = "development", enable_hot_reload: bool = False) -> bool:
        """
        Load configuration for specified environment
        
        Args:
            environment: Target environment
            enable_hot_reload: Whether to enable hot reloading
            
        Returns:
            True if successful
        """
        try:
            print(f"Loading configuration for environment: {environment}")
            
            config = initialize_configuration(environment, enable_hot_reload)
            
            print(f"✅ Configuration loaded successfully")
            print(f"   - Total entries: {len(config)}")
            print(f"   - Environment: {environment}")
            print(f"   - Hot reload: {'enabled' if enable_hot_reload else 'disabled'}")
            
            # Show summary
            summary = self.config_manager.get_configuration_summary()
            print(f"   - Sources: {summary['sources']}")
            print(f"   - Conflicts resolved: {summary['conflicts_resolved']}")
            print(f"   - Secret keys: {summary['secret_keys']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            logger.error(f"Configuration loading failed: {e}")
            return False
    
    def validate_configuration(self) -> bool:
        """
        Validate current configuration
        
        Returns:
            True if validation passes
        """
        try:
            print("Validating configuration...")
            
            if not self.config_manager:
                print("❌ Configuration not loaded. Run 'load' command first.")
                return False
            
            # Get validation summary
            summary = self.config_manager.get_configuration_summary()
            
            print(f"✅ Configuration validation completed")
            print(f"   - Total entries: {summary['total_entries']}")
            print(f"   - Conflicts resolved: {summary['conflicts_resolved']}")
            print(f"   - Secret keys: {summary['secret_keys']}")
            
            # Show conflicts if any
            if self.config_manager.conflicts:
                print(f"\n📋 Resolved conflicts ({len(self.config_manager.conflicts)}):")
                for conflict in self.config_manager.conflicts:
                    print(f"   - {conflict.key}: {conflict.resolution_reason}")
            
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def generate_service_config(self, service_name: str, format: str = "env", include_deps: bool = True) -> bool:
        """
        Generate configuration for a specific service
        
        Args:
            service_name: Name of the service
            format: Output format (env, json, yaml)
            include_deps: Whether to include dependencies
            
        Returns:
            True if successful
        """
        try:
            print(f"Generating configuration for service: {service_name}")
            
            if not self.config_manager:
                print("❌ Configuration not loaded. Run 'load' command first.")
                return False
            
            # Generate service configuration
            service_config = generate_service_configuration(service_name, include_deps)
            
            print(f"✅ Service configuration generated")
            print(f"   - Service: {service_config.service_name}")
            print(f"   - Configuration keys: {len(service_config.config)}")
            print(f"   - Dependencies: {service_config.dependencies}")
            print(f"   - Required keys: {len(service_config.required_keys)}")
            print(f"   - Optional keys: {len(service_config.optional_keys)}")
            
            # Export in requested format
            config_content = export_service_configuration(service_name, format)
            
            print(f"\n📄 Configuration ({format.upper()} format):")
            print("-" * 50)
            print(config_content)
            print("-" * 50)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate service configuration: {e}")
            logger.error(f"Service configuration generation failed: {e}")
            return False
    
    def export_service_config(self, service_name: str, output_file: str, format: str = "env") -> bool:
        """
        Export service configuration to file
        
        Args:
            service_name: Name of the service
            output_file: Output file path
            format: Output format
            
        Returns:
            True if successful
        """
        try:
            print(f"Exporting {service_name} configuration to: {output_file}")
            
            if not self.config_manager:
                print("❌ Configuration not loaded. Run 'load' command first.")
                return False
            
            output_path = Path(output_file)
            
            # Export configuration
            config_content = export_service_configuration(service_name, format, output_path)
            
            print(f"✅ Configuration exported successfully")
            print(f"   - Service: {service_name}")
            print(f"   - Format: {format}")
            print(f"   - Output file: {output_path.absolute()}")
            print(f"   - File size: {output_path.stat().st_size} bytes")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to export service configuration: {e}")
            logger.error(f"Service configuration export failed: {e}")
            return False
    
    def show_status(self) -> bool:
        """
        Show configuration system status
        
        Returns:
            True if successful
        """
        try:
            print("Configuration System Status")
            print("=" * 50)
            
            if not self.config_manager:
                print("❌ Configuration not loaded")
                return False
            
            # Configuration manager status
            summary = self.config_manager.get_configuration_summary()
            print(f"Configuration Manager:")
            print(f"   - Total entries: {summary['total_entries']}")
            print(f"   - Conflicts resolved: {summary['conflicts_resolved']}")
            print(f"   - Hot reloading: {'enabled' if summary['hot_reloading_enabled'] else 'disabled'}")
            print(f"   - Secret keys: {summary['secret_keys']}")
            
            # Sources breakdown
            print(f"\nConfiguration Sources:")
            for source, count in summary['sources'].items():
                print(f"   - {source}: {count} entries")
            
            # Service generator status
            if self.service_generator:
                all_status = self.service_generator.get_all_service_status()
                print(f"\nRegistered Services ({len(all_status)}):")
                
                for service_name, status in all_status.items():
                    active_indicator = "🟢" if status['is_active'] else "🔴"
                    print(f"   {active_indicator} {service_name} ({status['type']})")
                    print(f"      - Dependencies: {len(status['dependencies'])}")
                    print(f"      - Required keys: {len(status['required_keys'])}")
                    print(f"      - Optional keys: {len(status['optional_keys'])}")
                    if status['last_update']:
                        last_update = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(status['last_update']))
                        print(f"      - Last update: {last_update}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to show status: {e}")
            logger.error(f"Status display failed: {e}")
            return False
    
    def manage_hot_reload(self, enable: bool) -> bool:
        """
        Enable or disable hot reloading
        
        Args:
            enable: Whether to enable hot reloading
            
        Returns:
            True if successful
        """
        try:
            if not self.config_manager:
                print("❌ Configuration not loaded. Run 'load' command first.")
                return False
            
            if enable:
                print("Enabling configuration hot reloading...")
                self.config_manager.enable_hot_reloading()
                print("✅ Hot reloading enabled")
                print("   Configuration files will be monitored for changes")
            else:
                print("Disabling configuration hot reloading...")
                self.config_manager.disable_hot_reloading()
                print("✅ Hot reloading disabled")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to manage hot reload: {e}")
            logger.error(f"Hot reload management failed: {e}")
            return False
    
    def list_services(self) -> bool:
        """
        List all registered services
        
        Returns:
            True if successful
        """
        try:
            print("Registered Services")
            print("=" * 50)
            
            if not self.service_generator:
                print("❌ Service generator not initialized")
                return False
            
            all_status = self.service_generator.get_all_service_status()
            
            if not all_status:
                print("No services registered")
                return True
            
            for service_name, status in all_status.items():
                active_indicator = "🟢" if status['is_active'] else "🔴"
                print(f"\n{active_indicator} {service_name}")
                print(f"   Type: {status['type']}")
                print(f"   Dependencies: {', '.join(status['dependencies']) if status['dependencies'] else 'None'}")
                print(f"   Required keys: {len(status['required_keys'])}")
                print(f"   Optional keys: {len(status['optional_keys'])}")
                
                if status['config_file_path']:
                    print(f"   Config file: {status['config_file_path']}")
                
                if status['health_check_url']:
                    print(f"   Health check: {status['health_check_url']}")
                
                if status['last_update']:
                    last_update = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(status['last_update']))
                    print(f"   Last update: {last_update}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to list services: {e}")
            logger.error(f"Service listing failed: {e}")
            return False
    
    def update_configuration(self, key: str, value: str) -> bool:
        """
        Update a configuration value
        
        Args:
            key: Configuration key
            value: New value
            
        Returns:
            True if successful
        """
        try:
            print(f"Updating configuration: {key}")
            
            if not self.config_manager:
                print("❌ Configuration not loaded. Run 'load' command first.")
                return False
            
            # Update configuration
            self.config_manager.update_configuration({key: value})
            
            print(f"✅ Configuration updated successfully")
            print(f"   - Key: {key}")
            print(f"   - Value: {'***' if 'SECRET' in key or 'PASSWORD' in key else value}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to update configuration: {e}")
            logger.error(f"Configuration update failed: {e}")
            return False


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Configuration Manager CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s load --environment development
  %(prog)s validate
  %(prog)s generate --service frontend --format env
  %(prog)s export --service backend --output backend.env
  %(prog)s status
  %(prog)s watch --enable
  %(prog)s services
  %(prog)s update --key JWT_SECRET --value new_secret_value
        """
    )
    
    parser.add_argument(
        '--project-path',
        type=str,
        help='Path to project root directory'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Load command
    load_parser = subparsers.add_parser('load', help='Load configuration')
    load_parser.add_argument(
        '--environment', '-e',
        default='development',
        choices=['development', 'staging', 'production'],
        help='Target environment'
    )
    load_parser.add_argument(
        '--hot-reload',
        action='store_true',
        help='Enable hot reloading'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate service configuration')
    generate_parser.add_argument(
        '--service', '-s',
        required=True,
        help='Service name'
    )
    generate_parser.add_argument(
        '--format', '-f',
        default='env',
        choices=['env', 'json', 'yaml'],
        help='Output format'
    )
    generate_parser.add_argument(
        '--no-deps',
        action='store_true',
        help='Exclude dependencies'
    )
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export service configuration to file')
    export_parser.add_argument(
        '--service', '-s',
        required=True,
        help='Service name'
    )
    export_parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output file path'
    )
    export_parser.add_argument(
        '--format', '-f',
        default='env',
        choices=['env', 'json', 'yaml'],
        help='Output format'
    )
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show configuration system status')
    
    # Watch command
    watch_parser = subparsers.add_parser('watch', help='Manage hot reloading')
    watch_group = watch_parser.add_mutually_exclusive_group(required=True)
    watch_group.add_argument('--enable', action='store_true', help='Enable hot reloading')
    watch_group.add_argument('--disable', action='store_true', help='Disable hot reloading')
    
    # Services command
    services_parser = subparsers.add_parser('services', help='List registered services')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update configuration value')
    update_parser.add_argument('--key', '-k', required=True, help='Configuration key')
    update_parser.add_argument('--value', '-v', required=True, help='New value')
    
    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create CLI instance
    cli = ConfigManagerCLI()
    
    # Setup managers
    cli.setup_managers(args.project_path)
    
    # Execute command
    success = False
    
    try:
        if args.command == 'load':
            success = cli.load_configuration(args.environment, args.hot_reload)
        
        elif args.command == 'validate':
            success = cli.validate_configuration()
        
        elif args.command == 'generate':
            success = cli.generate_service_config(
                args.service,
                args.format,
                not args.no_deps
            )
        
        elif args.command == 'export':
            success = cli.export_service_config(
                args.service,
                args.output,
                args.format
            )
        
        elif args.command == 'status':
            success = cli.show_status()
        
        elif args.command == 'watch':
            success = cli.manage_hot_reload(args.enable)
        
        elif args.command == 'services':
            success = cli.list_services()
        
        elif args.command == 'update':
            success = cli.update_configuration(args.key, args.value)
        
        else:
            parser.print_help()
            success = False
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        success = False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}")
        success = False
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()