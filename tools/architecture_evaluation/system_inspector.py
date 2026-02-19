"""
System inspector for gathering codebase information.

This module provides functionality to traverse the project structure,
parse configuration files, and extract documentation for architecture evaluation.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ProjectStructure:
    """Represents the project directory structure."""
    root_path: Path
    directories: List[str] = field(default_factory=list)
    files_by_extension: Dict[str, List[str]] = field(default_factory=dict)
    total_files: int = 0
    total_directories: int = 0


@dataclass
class ConfigurationFiles:
    """Represents parsed configuration files."""
    docker_compose: Optional[Dict[str, Any]] = None
    package_json: Optional[Dict[str, Any]] = None
    requirements_txt: Optional[List[str]] = None
    other_configs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Documentation:
    """Represents parsed documentation files."""
    readme: Optional[str] = None
    architecture_docs: Dict[str, str] = field(default_factory=dict)
    other_docs: Dict[str, str] = field(default_factory=dict)


@dataclass
class SystemInfo:
    """Complete system information gathered from codebase."""
    project_structure: ProjectStructure
    configurations: ConfigurationFiles
    documentation: Documentation
    services: List[str] = field(default_factory=list)
    technologies: Dict[str, List[str]] = field(default_factory=dict)


class SystemInspector:
    """
    Gathers comprehensive information about a codebase for architecture evaluation.
    
    This class provides methods to:
    - Traverse file system and analyze project structure
    - Parse configuration files (docker-compose.yml, package.json, requirements.txt)
    - Extract and parse documentation (README.md, architecture docs)
    """
    
    def __init__(self, project_root: str):
        """
        Initialize the system inspector.
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = Path(project_root).resolve()
        self.ignore_patterns = {
            '__pycache__', 'node_modules', '.git', '.pytest_cache',
            'venv', 'env', '.venv', 'dist', 'build', '.next',
            'coverage', '.coverage', 'htmlcov'
        }
    
    def gather_system_info(self) -> SystemInfo:
        """
        Gather complete system information from the codebase.
        
        Returns:
            SystemInfo object containing all gathered information
        """
        project_structure = self.traverse_project_structure()
        configurations = self.parse_configuration_files()
        documentation = self.parse_documentation()
        services = self.identify_services(configurations)
        technologies = self.identify_technologies(configurations, project_structure)
        
        return SystemInfo(
            project_structure=project_structure,
            configurations=configurations,
            documentation=documentation,
            services=services,
            technologies=technologies
        )
    
    def traverse_project_structure(self) -> ProjectStructure:
        """
        Traverse the project directory structure and categorize files.
        
        Returns:
            ProjectStructure object with directory and file information
        """
        structure = ProjectStructure(root_path=self.project_root)
        
        for root, dirs, files in os.walk(self.project_root):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
            
            rel_root = os.path.relpath(root, self.project_root)
            if rel_root != '.':
                structure.directories.append(rel_root)
                structure.total_directories += 1
            
            for file in files:
                structure.total_files += 1
                ext = Path(file).suffix.lower()
                if ext:
                    if ext not in structure.files_by_extension:
                        structure.files_by_extension[ext] = []
                    rel_path = os.path.join(rel_root, file)
                    structure.files_by_extension[ext].append(rel_path)
        
        return structure
    
    def parse_configuration_files(self) -> ConfigurationFiles:
        """
        Parse common configuration files from the project.
        
        Returns:
            ConfigurationFiles object with parsed configuration data
        """
        configs = ConfigurationFiles()
        
        # Parse docker-compose.yml
        docker_compose_path = self.project_root / 'docker-compose.yml'
        if docker_compose_path.exists():
            configs.docker_compose = self._parse_yaml(docker_compose_path)
        
        # Parse package.json (frontend or Node.js projects)
        package_json_path = self.project_root / 'package.json'
        if package_json_path.exists():
            configs.package_json = self._parse_json(package_json_path)
        
        # Check for package.json in common frontend directories
        for frontend_dir in ['frontend', 'client', 'web']:
            frontend_package = self.project_root / frontend_dir / 'package.json'
            if frontend_package.exists():
                configs.package_json = self._parse_json(frontend_package)
                break
        
        # Parse requirements.txt (Python projects)
        requirements_path = self.project_root / 'requirements.txt'
        if requirements_path.exists():
            configs.requirements_txt = self._parse_requirements(requirements_path)
        
        # Look for other common config files
        config_files = {
            'pyproject.toml': self._parse_toml,
            'setup.py': self._read_text,
            'tsconfig.json': self._parse_json,
            'next.config.js': self._read_text,
            '.env.example': self._read_text,
        }
        
        for config_name, parser in config_files.items():
            config_path = self.project_root / config_name
            if config_path.exists():
                try:
                    configs.other_configs[config_name] = parser(config_path)
                except Exception:
                    # If parsing fails, just skip this config
                    pass
        
        return configs
    
    def parse_documentation(self) -> Documentation:
        """
        Parse documentation files from the project.
        
        Returns:
            Documentation object with parsed documentation content
        """
        docs = Documentation()
        
        # Parse README.md
        readme_path = self.project_root / 'README.md'
        if readme_path.exists():
            docs.readme = self._read_text(readme_path)
        
        # Look for architecture documentation
        arch_doc_patterns = [
            'docs/architecture',
            'docs/ARCHITECTURE.md',
            'ARCHITECTURE.md',
            'docs/design',
        ]
        
        for pattern in arch_doc_patterns:
            path = self.project_root / pattern
            if path.is_file():
                docs.architecture_docs[pattern] = self._read_text(path)
            elif path.is_dir():
                # Read all markdown files in architecture directory
                for md_file in path.glob('*.md'):
                    rel_path = str(md_file.relative_to(self.project_root))
                    docs.architecture_docs[rel_path] = self._read_text(md_file)
        
        # Look for other documentation
        docs_dir = self.project_root / 'docs'
        if docs_dir.exists() and docs_dir.is_dir():
            for md_file in docs_dir.rglob('*.md'):
                rel_path = str(md_file.relative_to(self.project_root))
                # Skip if already in architecture_docs
                if rel_path not in docs.architecture_docs:
                    docs.other_docs[rel_path] = self._read_text(md_file)
        
        return docs
    
    def identify_services(self, configs: ConfigurationFiles) -> List[str]:
        """
        Identify microservices from docker-compose configuration.
        
        Args:
            configs: Parsed configuration files
            
        Returns:
            List of service names
        """
        services = []
        
        if configs.docker_compose and 'services' in configs.docker_compose:
            services = list(configs.docker_compose['services'].keys())
        
        return services
    
    def identify_technologies(
        self,
        configs: ConfigurationFiles,
        structure: ProjectStructure
    ) -> Dict[str, List[str]]:
        """
        Identify technologies used in the project.
        
        Args:
            configs: Parsed configuration files
            structure: Project structure information
            
        Returns:
            Dictionary mapping technology categories to lists of technologies
        """
        technologies = {
            'frontend': [],
            'backend': [],
            'database': [],
            'infrastructure': [],
            'testing': [],
        }
        
        # Identify frontend technologies from package.json
        if configs.package_json and 'dependencies' in configs.package_json:
            deps = configs.package_json['dependencies']
            if 'react' in deps:
                technologies['frontend'].append(f"React {deps.get('react', '')}")
            if 'next' in deps:
                technologies['frontend'].append(f"Next.js {deps.get('next', '')}")
            if 'socket.io-client' in deps:
                technologies['frontend'].append('Socket.io')
            if 'redux' in deps or '@reduxjs/toolkit' in deps:
                technologies['frontend'].append('Redux')
        
        # Identify backend technologies from requirements.txt
        if configs.requirements_txt:
            for req in configs.requirements_txt:
                req_lower = req.lower()
                if 'fastapi' in req_lower:
                    technologies['backend'].append('FastAPI')
                elif 'django' in req_lower:
                    technologies['backend'].append('Django')
                elif 'flask' in req_lower:
                    technologies['backend'].append('Flask')
                elif 'celery' in req_lower:
                    technologies['backend'].append('Celery')
        
        # Identify databases from docker-compose
        if configs.docker_compose and 'services' in configs.docker_compose:
            for service_name, service_config in configs.docker_compose['services'].items():
                if 'image' in service_config:
                    image = service_config['image'].lower()
                    if 'postgres' in image:
                        technologies['database'].append('PostgreSQL')
                    elif 'neo4j' in image:
                        technologies['database'].append('Neo4j')
                    elif 'redis' in image:
                        technologies['database'].append('Redis')
                    elif 'mongo' in image:
                        technologies['database'].append('MongoDB')
        
        # Identify infrastructure technologies
        if configs.docker_compose:
            technologies['infrastructure'].append('Docker Compose')
        
        # Identify testing frameworks from file extensions
        if '.py' in structure.files_by_extension:
            # Check for pytest
            if any('pytest' in f for f in structure.files_by_extension.get('.py', [])):
                technologies['testing'].append('pytest')
            if any('test_' in f for f in structure.files_by_extension.get('.py', [])):
                technologies['testing'].append('Python unit tests')
        
        if '.ts' in structure.files_by_extension or '.tsx' in structure.files_by_extension:
            if configs.package_json and 'devDependencies' in configs.package_json:
                dev_deps = configs.package_json['devDependencies']
                if 'jest' in dev_deps:
                    technologies['testing'].append('Jest')
                if 'vitest' in dev_deps:
                    technologies['testing'].append('Vitest')
        
        # Remove duplicates
        for category in technologies:
            technologies[category] = list(set(technologies[category]))
        
        return technologies
    
    def _parse_yaml(self, path: Path) -> Optional[Dict[str, Any]]:
        """Parse a YAML file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return None
    
    def _parse_json(self, path: Path) -> Optional[Dict[str, Any]]:
        """Parse a JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _parse_requirements(self, path: Path) -> Optional[List[str]]:
        """Parse a requirements.txt file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Filter out comments and empty lines
                requirements = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        requirements.append(line)
                return requirements
        except Exception:
            return None
    
    def _parse_toml(self, path: Path) -> Optional[Dict[str, Any]]:
        """Parse a TOML file."""
        try:
            import tomli
            with open(path, 'rb') as f:
                return tomli.load(f)
        except ImportError:
            # tomli not available, try tomllib (Python 3.11+)
            try:
                import tomllib
                with open(path, 'rb') as f:
                    return tomllib.load(f)
            except Exception:
                return None
        except Exception:
            return None
    
    def _read_text(self, path: Path) -> Optional[str]:
        """Read a text file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
