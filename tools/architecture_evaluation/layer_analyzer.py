"""
Layer analyzer for evaluating individual architectural layers.

This module provides the LayerAnalyzer class which analyzes individual
architectural layers for completeness and gaps against stated capabilities.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import (
    Capability,
    LayerAnalysisResult,
    Gap,
    PartialCapability
)
from .system_inspector import SystemInfo


class LayerAnalyzer:
    """
    Analyzes individual architectural layers for completeness and gaps.
    
    This class evaluates each layer (Frontend, Backend API, Data Persistence,
    AI Reasoning, Integration) against its stated capabilities and identifies
    missing or incomplete implementations.
    """
    
    def __init__(self, system_info: SystemInfo):
        """
        Initialize the layer analyzer.
        
        Args:
            system_info: System information gathered from the codebase
        """
        self.system_info = system_info
    
    def analyze_layer(
        self,
        layer_name: str,
        stated_capabilities: List[Capability],
        implementation_artifacts: Optional[Dict[str, Any]] = None
    ) -> LayerAnalysisResult:
        """
        Analyze a single architectural layer.
        
        Args:
            layer_name: Name of the layer (Frontend, Backend API, etc.)
            stated_capabilities: List of capabilities the layer should provide
            implementation_artifacts: Optional dict of code, configs, and documentation
            
        Returns:
            LayerAnalysisResult with completeness score and gaps
        """
        # Use system_info if no specific artifacts provided
        if implementation_artifacts is None:
            implementation_artifacts = self._extract_layer_artifacts(layer_name)
        
        # Verify each capability
        implemented_capabilities = []
        missing_capabilities = []
        partial_capabilities = []
        gaps = []
        strengths = []
        
        for capability in stated_capabilities:
            verification_result = self._verify_capability(
                capability,
                implementation_artifacts,
                layer_name
            )
            
            if verification_result['status'] == 'implemented':
                implemented_capabilities.append(capability)
                if verification_result.get('strength'):
                    strengths.append(verification_result['strength'])
            elif verification_result['status'] == 'missing':
                missing_capabilities.append(capability)
                # Create gap for missing capability
                gap = self._create_gap_from_capability(
                    capability,
                    layer_name,
                    verification_result
                )
                gaps.append(gap)
            elif verification_result['status'] == 'partial':
                partial_cap = PartialCapability(
                    capability=capability,
                    implemented_aspects=verification_result.get('implemented_aspects', []),
                    missing_aspects=verification_result.get('missing_aspects', []),
                    completeness_percentage=verification_result.get('completeness_percentage', 0.0)
                )
                partial_capabilities.append(partial_cap)
                # Create gap for partial capability
                gap = self._create_gap_from_partial_capability(
                    partial_cap,
                    layer_name,
                    verification_result
                )
                gaps.append(gap)
        
        # Calculate completeness score
        completeness_score = self.calculate_completeness_score(
            stated_capabilities,
            implemented_capabilities,
            partial_capabilities
        )
        
        return LayerAnalysisResult(
            layer_name=layer_name,
            completeness_score=completeness_score,
            capabilities_assessed=stated_capabilities,
            implemented_capabilities=implemented_capabilities,
            missing_capabilities=missing_capabilities,
            partial_capabilities=partial_capabilities,
            gaps=gaps,
            strengths=strengths,
            timestamp=datetime.now()
        )
    
    def calculate_completeness_score(
        self,
        stated_capabilities: List[Capability],
        implemented_capabilities: List[Capability],
        partial_capabilities: List[PartialCapability]
    ) -> float:
        """
        Calculate completeness score for a layer.
        
        The score is calculated as:
        (fully_implemented + sum(partial_percentages)) / total_required
        
        Args:
            stated_capabilities: All capabilities that should be implemented
            implemented_capabilities: Fully implemented capabilities
            partial_capabilities: Partially implemented capabilities
            
        Returns:
            Completeness score between 0.0 and 1.0
        """
        # Only count required capabilities
        required_capabilities = [c for c in stated_capabilities if c.required]
        
        if not required_capabilities:
            return 1.0
        
        # Count fully implemented required capabilities
        implemented_required = [
            c for c in implemented_capabilities if c.required
        ]
        fully_implemented_count = len(implemented_required)
        
        # Sum partial completion percentages for required capabilities
        partial_sum = 0.0
        for partial_cap in partial_capabilities:
            if partial_cap.capability.required:
                partial_sum += partial_cap.completeness_percentage / 100.0
        
        total_required = len(required_capabilities)
        score = (fully_implemented_count + partial_sum) / total_required
        
        # Ensure score is between 0.0 and 1.0
        return max(0.0, min(1.0, score))
    
    def _verify_capability(
        self,
        capability: Capability,
        implementation_artifacts: Dict[str, Any],
        layer_name: str
    ) -> Dict[str, Any]:
        """
        Verify if a capability is implemented.
        
        Args:
            capability: The capability to verify
            implementation_artifacts: Code, configs, and documentation
            layer_name: Name of the layer being analyzed
            
        Returns:
            Dict with verification result including status and details
        """
        # Use verification method specified in capability
        verification_method = capability.verification_method.lower()
        
        if verification_method == 'code':
            return self._verify_by_code_analysis(capability, implementation_artifacts, layer_name)
        elif verification_method == 'config':
            return self._verify_by_config(capability, implementation_artifacts, layer_name)
        elif verification_method == 'documentation':
            return self._verify_by_documentation(capability, implementation_artifacts, layer_name)
        else:
            # Default to code analysis
            return self._verify_by_code_analysis(capability, implementation_artifacts, layer_name)
    
    def _verify_by_code_analysis(
        self,
        capability: Capability,
        artifacts: Dict[str, Any],
        layer_name: str
    ) -> Dict[str, Any]:
        """
        Verify capability by analyzing code structure and files.
        
        Args:
            capability: The capability to verify
            artifacts: Implementation artifacts
            layer_name: Name of the layer
            
        Returns:
            Verification result dict
        """
        # This is a simplified implementation
        # In a real system, this would perform deep code analysis
        
        files = artifacts.get('files', [])
        directories = artifacts.get('directories', [])
        
        # Check if relevant files/directories exist based on capability name
        capability_name_lower = capability.name.lower()
        
        # Look for evidence in file/directory names
        evidence_count = 0
        total_checks = 3  # Number of aspects we check
        
        # Check 1: Relevant files exist
        relevant_files = [f for f in files if capability_name_lower in f.lower()]
        if relevant_files:
            evidence_count += 1
        
        # Check 2: Relevant directories exist
        relevant_dirs = [d for d in directories if capability_name_lower in d.lower()]
        if relevant_dirs:
            evidence_count += 1
        
        # Check 3: Technology presence
        technologies = artifacts.get('technologies', [])
        if any(capability_name_lower in tech.lower() for tech in technologies):
            evidence_count += 1
        
        if evidence_count == 0:
            return {
                'status': 'missing',
                'reason': f'No evidence found for {capability.name}',
                'evidence': []
            }
        elif evidence_count < total_checks:
            return {
                'status': 'partial',
                'implemented_aspects': [f'Found {evidence_count} of {total_checks} indicators'],
                'missing_aspects': [f'Missing {total_checks - evidence_count} indicators'],
                'completeness_percentage': (evidence_count / total_checks) * 100,
                'evidence': relevant_files + relevant_dirs
            }
        else:
            return {
                'status': 'implemented',
                'strength': f'{capability.name} implementation found',
                'evidence': relevant_files + relevant_dirs
            }
    
    def _verify_by_config(
        self,
        capability: Capability,
        artifacts: Dict[str, Any],
        layer_name: str
    ) -> Dict[str, Any]:
        """
        Verify capability by checking configuration files.
        
        Args:
            capability: The capability to verify
            artifacts: Implementation artifacts
            layer_name: Name of the layer
            
        Returns:
            Verification result dict
        """
        configs = artifacts.get('configurations', {})
        capability_name_lower = capability.name.lower()
        
        # Check various configuration sources
        found_in_configs = []
        
        # Check docker-compose
        if 'docker_compose' in configs and configs['docker_compose']:
            docker_str = str(configs['docker_compose']).lower()
            if capability_name_lower in docker_str:
                found_in_configs.append('docker-compose.yml')
        
        # Check package.json
        if 'package_json' in configs and configs['package_json']:
            package_str = str(configs['package_json']).lower()
            if capability_name_lower in package_str:
                found_in_configs.append('package.json')
        
        # Check requirements.txt
        if 'requirements_txt' in configs and configs['requirements_txt']:
            requirements_str = str(configs['requirements_txt']).lower()
            if capability_name_lower in requirements_str:
                found_in_configs.append('requirements.txt')
        
        if found_in_configs:
            return {
                'status': 'implemented',
                'strength': f'{capability.name} configured in {", ".join(found_in_configs)}',
                'evidence': found_in_configs
            }
        else:
            return {
                'status': 'missing',
                'reason': f'No configuration found for {capability.name}',
                'evidence': []
            }
    
    def _verify_by_documentation(
        self,
        capability: Capability,
        artifacts: Dict[str, Any],
        layer_name: str
    ) -> Dict[str, Any]:
        """
        Verify capability by checking documentation.
        
        Args:
            capability: The capability to verify
            artifacts: Implementation artifacts
            layer_name: Name of the layer
            
        Returns:
            Verification result dict
        """
        documentation = artifacts.get('documentation', {})
        capability_name_lower = capability.name.lower()
        
        found_in_docs = []
        
        # Check README
        if 'readme' in documentation and documentation['readme']:
            if capability_name_lower in documentation['readme'].lower():
                found_in_docs.append('README.md')
        
        # Check architecture docs
        if 'architecture_docs' in documentation:
            for doc_name, doc_content in documentation['architecture_docs'].items():
                if doc_content and capability_name_lower in doc_content.lower():
                    found_in_docs.append(doc_name)
        
        if found_in_docs:
            return {
                'status': 'implemented',
                'strength': f'{capability.name} documented in {", ".join(found_in_docs)}',
                'evidence': found_in_docs
            }
        else:
            return {
                'status': 'missing',
                'reason': f'No documentation found for {capability.name}',
                'evidence': []
            }
    
    def _extract_layer_artifacts(self, layer_name: str) -> Dict[str, Any]:
        """
        Extract relevant artifacts for a specific layer from system info.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            Dict containing relevant files, configs, and documentation
        """
        artifacts = {
            'files': [],
            'directories': [],
            'configurations': {},
            'documentation': {},
            'technologies': []
        }
        
        # Extract files by extension
        all_files = []
        for ext, files in self.system_info.project_structure.files_by_extension.items():
            all_files.extend(files)
        artifacts['files'] = all_files
        
        # Extract directories
        artifacts['directories'] = self.system_info.project_structure.directories
        
        # Extract configurations
        if self.system_info.configurations.docker_compose:
            artifacts['configurations']['docker_compose'] = self.system_info.configurations.docker_compose
        if self.system_info.configurations.package_json:
            artifacts['configurations']['package_json'] = self.system_info.configurations.package_json
        if self.system_info.configurations.requirements_txt:
            artifacts['configurations']['requirements_txt'] = self.system_info.configurations.requirements_txt
        
        # Extract documentation
        if self.system_info.documentation.readme:
            artifacts['documentation']['readme'] = self.system_info.documentation.readme
        artifacts['documentation']['architecture_docs'] = self.system_info.documentation.architecture_docs
        
        # Extract technologies
        for category, techs in self.system_info.technologies.items():
            artifacts['technologies'].extend(techs)
        
        return artifacts
    
    def _create_gap_from_capability(
        self,
        capability: Capability,
        layer_name: str,
        verification_result: Dict[str, Any]
    ) -> Gap:
        """
        Create a Gap object from a missing capability.
        
        Args:
            capability: The missing capability
            layer_name: Name of the layer
            verification_result: Result from capability verification
            
        Returns:
            Gap object
        """
        gap_id = f"GAP-{layer_name.upper().replace(' ', '_')}-{capability.name.upper().replace(' ', '_')}"
        
        # Determine impact based on whether capability is required
        impact = "High" if capability.required else "Medium"
        
        return Gap(
            gap_id=gap_id,
            layer=layer_name,
            category=capability.category,
            description=f"Missing capability: {capability.name}",
            expected_state=capability.description,
            current_state=verification_result.get('reason', 'Not implemented'),
            impact=impact,
            affected_requirements=[],  # Will be populated by higher-level analysis
            related_capabilities=[capability.name]
        )
    
    def _create_gap_from_partial_capability(
        self,
        partial_capability: PartialCapability,
        layer_name: str,
        verification_result: Dict[str, Any]
    ) -> Gap:
        """
        Create a Gap object from a partially implemented capability.
        
        Args:
            partial_capability: The partial capability
            layer_name: Name of the layer
            verification_result: Result from capability verification
            
        Returns:
            Gap object
        """
        capability = partial_capability.capability
        gap_id = f"GAP-{layer_name.upper().replace(' ', '_')}-{capability.name.upper().replace(' ', '_')}-PARTIAL"
        
        # Determine impact based on completeness percentage
        if partial_capability.completeness_percentage < 30:
            impact = "High"
        elif partial_capability.completeness_percentage < 70:
            impact = "Medium"
        else:
            impact = "Low"
        
        missing_aspects_str = ", ".join(partial_capability.missing_aspects)
        
        return Gap(
            gap_id=gap_id,
            layer=layer_name,
            category=capability.category,
            description=f"Partially implemented capability: {capability.name} ({partial_capability.completeness_percentage:.0f}% complete)",
            expected_state=capability.description,
            current_state=f"Partially implemented. Missing: {missing_aspects_str}",
            impact=impact,
            affected_requirements=[],  # Will be populated by higher-level analysis
            related_capabilities=[capability.name]
        )
    
    def analyze_frontend_layer(self) -> LayerAnalysisResult:
        """
        Analyze the Frontend Layer for completeness.
        
        Checks:
        - React/Next.js implementation (package.json, src/ structure)
        - WebSocket connectivity (socket.io-client in dependencies)
        - PWA features (manifest, service worker)
        - UI component completeness (component directory structure)
        
        Returns:
            LayerAnalysisResult for the Frontend layer
        """
        layer_name = "Frontend"
        
        # Define Frontend capabilities
        capabilities = [
            Capability(
                name="React Implementation",
                description="React 19 framework properly configured and used",
                category="Framework",
                required=True,
                verification_method="config"
            ),
            Capability(
                name="Next.js Implementation",
                description="Next.js 14 framework properly configured with app router",
                category="Framework",
                required=True,
                verification_method="config"
            ),
            Capability(
                name="WebSocket Connectivity",
                description="Socket.io-client for real-time communication",
                category="Communication",
                required=True,
                verification_method="config"
            ),
            Capability(
                name="PWA Manifest",
                description="Progressive Web App manifest file",
                category="PWA",
                required=False,
                verification_method="code"
            ),
            Capability(
                name="Service Worker",
                description="Service worker for offline functionality",
                category="PWA",
                required=False,
                verification_method="code"
            ),
            Capability(
                name="UI Components",
                description="Component directory structure with reusable components",
                category="UI",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="State Management",
                description="Redux or similar state management solution",
                category="State",
                required=False,
                verification_method="config"
            ),
            Capability(
                name="Routing",
                description="Next.js app router or pages router implementation",
                category="Navigation",
                required=True,
                verification_method="code"
            )
        ]
        
        # Get artifacts for Frontend layer
        artifacts = self._extract_frontend_artifacts()
        
        # Verify each capability
        implemented_capabilities = []
        missing_capabilities = []
        partial_capabilities = []
        gaps = []
        strengths = []
        
        for capability in capabilities:
            verification_result = self._verify_frontend_capability(capability, artifacts)
            
            if verification_result['status'] == 'implemented':
                implemented_capabilities.append(capability)
                if verification_result.get('strength'):
                    strengths.append(verification_result['strength'])
            elif verification_result['status'] == 'missing':
                missing_capabilities.append(capability)
                gap = self._create_gap_from_capability(
                    capability,
                    layer_name,
                    verification_result
                )
                gaps.append(gap)
            elif verification_result['status'] == 'partial':
                partial_cap = PartialCapability(
                    capability=capability,
                    implemented_aspects=verification_result.get('implemented_aspects', []),
                    missing_aspects=verification_result.get('missing_aspects', []),
                    completeness_percentage=verification_result.get('completeness_percentage', 0.0)
                )
                partial_capabilities.append(partial_cap)
                gap = self._create_gap_from_partial_capability(
                    partial_cap,
                    layer_name,
                    verification_result
                )
                gaps.append(gap)
        
        # Calculate completeness score
        completeness_score = self.calculate_completeness_score(
            capabilities,
            implemented_capabilities,
            partial_capabilities
        )
        
        return LayerAnalysisResult(
            layer_name=layer_name,
            completeness_score=completeness_score,
            capabilities_assessed=capabilities,
            implemented_capabilities=implemented_capabilities,
            missing_capabilities=missing_capabilities,
            partial_capabilities=partial_capabilities,
            gaps=gaps,
            strengths=strengths,
            timestamp=datetime.now()
        )
    
    def _extract_frontend_artifacts(self) -> Dict[str, Any]:
        """
        Extract Frontend-specific artifacts from system info.
        
        Returns:
            Dict containing Frontend-relevant files, configs, and structure
        """
        artifacts = {
            'package_json': None,
            'has_src_dir': False,
            'has_app_dir': False,
            'has_pages_dir': False,
            'has_components_dir': False,
            'has_public_dir': False,
            'has_manifest': False,
            'has_service_worker': False,
            'frontend_files': [],
            'dependencies': {},
            'dev_dependencies': {}
        }
        
        # Get package.json
        if self.system_info.configurations.package_json:
            artifacts['package_json'] = self.system_info.configurations.package_json
            
            # Extract dependencies
            if 'dependencies' in self.system_info.configurations.package_json:
                artifacts['dependencies'] = self.system_info.configurations.package_json['dependencies']
            if 'devDependencies' in self.system_info.configurations.package_json:
                artifacts['dev_dependencies'] = self.system_info.configurations.package_json['devDependencies']
        
        # Check for key directories
        directories = self.system_info.project_structure.directories
        for directory in directories:
            dir_lower = directory.lower()
            if '/src' in dir_lower or directory == 'src':
                artifacts['has_src_dir'] = True
            if '/app' in dir_lower or directory == 'app':
                artifacts['has_app_dir'] = True
            if '/pages' in dir_lower or directory == 'pages':
                artifacts['has_pages_dir'] = True
            if 'component' in dir_lower:
                artifacts['has_components_dir'] = True
            if '/public' in dir_lower or directory == 'public':
                artifacts['has_public_dir'] = True
        
        # Check for PWA files
        all_files = []
        for ext, files in self.system_info.project_structure.files_by_extension.items():
            all_files.extend(files)
        
        for file_path in all_files:
            file_lower = file_path.lower()
            if 'manifest.json' in file_lower or 'manifest.webmanifest' in file_lower:
                artifacts['has_manifest'] = True
            if 'service-worker' in file_lower or 'sw.js' in file_lower:
                artifacts['has_service_worker'] = True
            
            # Collect frontend-related files
            if any(ext in file_path for ext in ['.tsx', '.jsx', '.ts', '.js']):
                if any(keyword in file_lower for keyword in ['component', 'page', 'layout', 'app', 'src']):
                    artifacts['frontend_files'].append(file_path)
        
        return artifacts
    
    def _verify_frontend_capability(
        self,
        capability: Capability,
        artifacts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify a Frontend-specific capability.
        
        Args:
            capability: The capability to verify
            artifacts: Frontend-specific artifacts
            
        Returns:
            Verification result dict
        """
        cap_name = capability.name
        
        if cap_name == "React Implementation":
            return self._verify_react(artifacts)
        elif cap_name == "Next.js Implementation":
            return self._verify_nextjs(artifacts)
        elif cap_name == "WebSocket Connectivity":
            return self._verify_websocket(artifacts)
        elif cap_name == "PWA Manifest":
            return self._verify_pwa_manifest(artifacts)
        elif cap_name == "Service Worker":
            return self._verify_service_worker(artifacts)
        elif cap_name == "UI Components":
            return self._verify_ui_components(artifacts)
        elif cap_name == "State Management":
            return self._verify_state_management(artifacts)
        elif cap_name == "Routing":
            return self._verify_routing(artifacts)
        else:
            return {'status': 'missing', 'reason': 'Unknown capability'}
    
    def _verify_react(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify React implementation."""
        deps = artifacts.get('dependencies', {})
        
        if 'react' in deps:
            version = deps['react']
            return {
                'status': 'implemented',
                'strength': f'React {version} configured',
                'evidence': ['package.json']
            }
        else:
            return {
                'status': 'missing',
                'reason': 'React not found in dependencies',
                'evidence': []
            }
    
    def _verify_nextjs(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify Next.js implementation."""
        deps = artifacts.get('dependencies', {})
        
        has_nextjs = 'next' in deps
        has_app_dir = artifacts.get('has_app_dir', False)
        has_pages_dir = artifacts.get('has_pages_dir', False)
        
        if has_nextjs:
            version = deps['next']
            implemented_aspects = [f'Next.js {version} installed']
            missing_aspects = []
            
            router_type = None
            if has_app_dir:
                implemented_aspects.append('App router directory found')
                router_type = 'App router'
            elif has_pages_dir:
                implemented_aspects.append('Pages router directory found')
                router_type = 'Pages router'
            else:
                missing_aspects.append('No app/ or pages/ directory found')
            
            if missing_aspects:
                completeness = (len(implemented_aspects) / (len(implemented_aspects) + len(missing_aspects))) * 100
                return {
                    'status': 'partial',
                    'implemented_aspects': implemented_aspects,
                    'missing_aspects': missing_aspects,
                    'completeness_percentage': completeness,
                    'evidence': ['package.json']
                }
            else:
                strength_msg = f'Next.js {version} with {router_type}'
                return {
                    'status': 'implemented',
                    'strength': strength_msg,
                    'evidence': ['package.json', 'app/' if has_app_dir else 'pages/']
                }
        else:
            return {
                'status': 'missing',
                'reason': 'Next.js not found in dependencies',
                'evidence': []
            }
    
    def _verify_websocket(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify WebSocket connectivity."""
        deps = artifacts.get('dependencies', {})
        
        if 'socket.io-client' in deps:
            version = deps['socket.io-client']
            return {
                'status': 'implemented',
                'strength': f'Socket.io-client {version} configured',
                'evidence': ['package.json']
            }
        else:
            return {
                'status': 'missing',
                'reason': 'socket.io-client not found in dependencies',
                'evidence': []
            }
    
    def _verify_pwa_manifest(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify PWA manifest."""
        if artifacts.get('has_manifest', False):
            return {
                'status': 'implemented',
                'strength': 'PWA manifest file found',
                'evidence': ['manifest.json or manifest.webmanifest']
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No PWA manifest file found',
                'evidence': []
            }
    
    def _verify_service_worker(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify service worker."""
        if artifacts.get('has_service_worker', False):
            return {
                'status': 'implemented',
                'strength': 'Service worker file found',
                'evidence': ['service-worker.js or sw.js']
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No service worker file found',
                'evidence': []
            }
    
    def _verify_ui_components(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify UI components structure."""
        has_components_dir = artifacts.get('has_components_dir', False)
        frontend_files = artifacts.get('frontend_files', [])
        
        if has_components_dir and len(frontend_files) > 0:
            return {
                'status': 'implemented',
                'strength': f'Component directory with {len(frontend_files)} frontend files',
                'evidence': ['components/ directory', f'{len(frontend_files)} component files']
            }
        elif has_components_dir:
            return {
                'status': 'partial',
                'implemented_aspects': ['Component directory exists'],
                'missing_aspects': ['Few or no component files found'],
                'completeness_percentage': 50.0,
                'evidence': ['components/ directory']
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No components directory found',
                'evidence': []
            }
    
    def _verify_state_management(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify state management solution."""
        deps = artifacts.get('dependencies', {})
        
        state_management_libs = ['redux', '@reduxjs/toolkit', 'zustand', 'jotai', 'recoil', 'mobx']
        found_libs = [lib for lib in state_management_libs if lib in deps]
        
        if found_libs:
            lib_versions = [f'{lib} {deps[lib]}' for lib in found_libs]
            return {
                'status': 'implemented',
                'strength': f'State management: {", ".join(lib_versions)}',
                'evidence': ['package.json']
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No state management library found',
                'evidence': []
            }
    
    def _verify_routing(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify routing implementation."""
        has_app_dir = artifacts.get('has_app_dir', False)
        has_pages_dir = artifacts.get('has_pages_dir', False)
        
        if has_app_dir or has_pages_dir:
            router_type = 'App router' if has_app_dir else 'Pages router'
            return {
                'status': 'implemented',
                'strength': f'Next.js {router_type} implemented',
                'evidence': ['app/' if has_app_dir else 'pages/']
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No routing directory (app/ or pages/) found',
                'evidence': []
            }
    
    def analyze_backend_api_layer(self) -> LayerAnalysisResult:
        """
        Analyze the Backend API Layer for completeness.
        
        Checks:
        - FastAPI endpoints (main.py, router files)
        - JWT authentication (auth middleware, token handling)
        - Horizontal scaling readiness (stateless design, connection pooling)
        - API versioning (API_V1_STR usage)
        
        Returns:
            LayerAnalysisResult for the Backend API layer
        """
        layer_name = "Backend API"
        
        # Define Backend API capabilities
        capabilities = [
            Capability(
                name="FastAPI Framework",
                description="FastAPI framework properly configured with endpoints",
                category="Framework",
                required=True,
                verification_method="config"
            ),
            Capability(
                name="API Endpoints",
                description="REST API endpoints defined in main.py or router files",
                category="API",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="JWT Authentication",
                description="JWT token-based authentication with middleware and token handling",
                category="Authentication",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Horizontal Scaling",
                description="Stateless design and connection pooling for horizontal scaling",
                category="Scalability",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="API Versioning",
                description="API versioning strategy (e.g., API_V1_STR) implemented",
                category="API",
                required=False,
                verification_method="code"
            ),
            Capability(
                name="Request Validation",
                description="Pydantic models for request/response validation",
                category="Validation",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Error Handling",
                description="Centralized error handling and exception middleware",
                category="Error Handling",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="CORS Configuration",
                description="CORS middleware properly configured",
                category="Security",
                required=True,
                verification_method="code"
            )
        ]
        
        # Get artifacts for Backend API layer
        artifacts = self._extract_backend_api_artifacts()
        
        # Verify each capability
        implemented_capabilities = []
        missing_capabilities = []
        partial_capabilities = []
        gaps = []
        strengths = []
        
        for capability in capabilities:
            verification_result = self._verify_backend_api_capability(capability, artifacts)
            
            if verification_result['status'] == 'implemented':
                implemented_capabilities.append(capability)
                if verification_result.get('strength'):
                    strengths.append(verification_result['strength'])
            elif verification_result['status'] == 'missing':
                missing_capabilities.append(capability)
                gap = self._create_gap_from_capability(
                    capability,
                    layer_name,
                    verification_result
                )
                gaps.append(gap)
            elif verification_result['status'] == 'partial':
                partial_cap = PartialCapability(
                    capability=capability,
                    implemented_aspects=verification_result.get('implemented_aspects', []),
                    missing_aspects=verification_result.get('missing_aspects', []),
                    completeness_percentage=verification_result.get('completeness_percentage', 0.0)
                )
                partial_capabilities.append(partial_cap)
                gap = self._create_gap_from_partial_capability(
                    partial_cap,
                    layer_name,
                    verification_result
                )
                gaps.append(gap)
        
        # Calculate completeness score
        completeness_score = self.calculate_completeness_score(
            capabilities,
            implemented_capabilities,
            partial_capabilities
        )
        
        return LayerAnalysisResult(
            layer_name=layer_name,
            completeness_score=completeness_score,
            capabilities_assessed=capabilities,
            implemented_capabilities=implemented_capabilities,
            missing_capabilities=missing_capabilities,
            partial_capabilities=partial_capabilities,
            gaps=gaps,
            strengths=strengths,
            timestamp=datetime.now()
        )
    
    def _extract_backend_api_artifacts(self) -> Dict[str, Any]:
        """
        Extract Backend API-specific artifacts from system info.
        
        Returns:
            Dict containing Backend API-relevant files, configs, and structure
        """
        artifacts = {
            'requirements_txt': None,
            'has_main_py': False,
            'has_routers_dir': False,
            'has_api_dir': False,
            'has_auth_files': False,
            'has_middleware_dir': False,
            'has_models_dir': False,
            'python_files': [],
            'api_files': [],
            'auth_files': [],
            'router_files': [],
            'dependencies': []
        }
        
        # Get requirements.txt
        if self.system_info.configurations.requirements_txt:
            artifacts['requirements_txt'] = self.system_info.configurations.requirements_txt
            artifacts['dependencies'] = self.system_info.configurations.requirements_txt
        
        # Check for key directories
        directories = self.system_info.project_structure.directories
        for directory in directories:
            dir_lower = directory.lower()
            if 'router' in dir_lower or 'routes' in dir_lower:
                artifacts['has_routers_dir'] = True
            if '/api' in dir_lower or directory == 'api':
                artifacts['has_api_dir'] = True
            if 'auth' in dir_lower:
                artifacts['has_auth_files'] = True
            if 'middleware' in dir_lower:
                artifacts['has_middleware_dir'] = True
            if 'model' in dir_lower:
                artifacts['has_models_dir'] = True
        
        # Check for Python files
        python_files = self.system_info.project_structure.files_by_extension.get('.py', [])
        artifacts['python_files'] = python_files
        
        for file_path in python_files:
            file_lower = file_path.lower()
            
            # Check for main.py
            if 'main.py' in file_lower:
                artifacts['has_main_py'] = True
            
            # Collect API-related files
            if any(keyword in file_lower for keyword in ['api', 'endpoint', 'route']):
                artifacts['api_files'].append(file_path)
            
            # Collect auth-related files
            if 'auth' in file_lower or 'jwt' in file_lower or 'token' in file_lower:
                artifacts['auth_files'].append(file_path)
            
            # Collect router files
            if 'router' in file_lower or 'route' in file_lower:
                artifacts['router_files'].append(file_path)
        
        return artifacts
    
    def _verify_backend_api_capability(
        self,
        capability: Capability,
        artifacts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify a Backend API-specific capability.
        
        Args:
            capability: The capability to verify
            artifacts: Backend API-specific artifacts
            
        Returns:
            Verification result dict
        """
        cap_name = capability.name
        
        if cap_name == "FastAPI Framework":
            return self._verify_fastapi(artifacts)
        elif cap_name == "API Endpoints":
            return self._verify_api_endpoints(artifacts)
        elif cap_name == "JWT Authentication":
            return self._verify_jwt_auth(artifacts)
        elif cap_name == "Horizontal Scaling":
            return self._verify_horizontal_scaling(artifacts)
        elif cap_name == "API Versioning":
            return self._verify_api_versioning(artifacts)
        elif cap_name == "Request Validation":
            return self._verify_request_validation(artifacts)
        elif cap_name == "Error Handling":
            return self._verify_error_handling(artifacts)
        elif cap_name == "CORS Configuration":
            return self._verify_cors(artifacts)
        else:
            return {'status': 'missing', 'reason': 'Unknown capability'}
    
    def _verify_fastapi(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify FastAPI framework installation and configuration."""
        dependencies = artifacts.get('dependencies', [])
        
        # Check if FastAPI is in dependencies
        fastapi_deps = [dep for dep in dependencies if 'fastapi' in dep.lower()]
        
        if fastapi_deps:
            has_main = artifacts.get('has_main_py', False)
            
            if has_main:
                return {
                    'status': 'implemented',
                    'strength': f'FastAPI configured with main.py entry point',
                    'evidence': ['requirements.txt', 'main.py']
                }
            else:
                return {
                    'status': 'partial',
                    'implemented_aspects': ['FastAPI installed in requirements.txt'],
                    'missing_aspects': ['No main.py entry point found'],
                    'completeness_percentage': 50.0,
                    'evidence': ['requirements.txt']
                }
        else:
            return {
                'status': 'missing',
                'reason': 'FastAPI not found in requirements.txt',
                'evidence': []
            }
    
    def _verify_api_endpoints(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify API endpoints are defined."""
        has_main = artifacts.get('has_main_py', False)
        has_routers = artifacts.get('has_routers_dir', False)
        router_files = artifacts.get('router_files', [])
        api_files = artifacts.get('api_files', [])
        
        evidence = []
        implemented_aspects = []
        missing_aspects = []
        
        if has_main:
            implemented_aspects.append('main.py entry point exists')
            evidence.append('main.py')
        else:
            missing_aspects.append('No main.py entry point')
        
        if has_routers or len(router_files) > 0:
            implemented_aspects.append(f'{len(router_files)} router files found')
            evidence.extend(router_files[:3])  # Include first 3 as evidence
        else:
            missing_aspects.append('No router files found')
        
        if len(api_files) > 0:
            implemented_aspects.append(f'{len(api_files)} API files found')
        
        if len(implemented_aspects) >= 2:
            return {
                'status': 'implemented',
                'strength': f'API endpoints defined: {", ".join(implemented_aspects)}',
                'evidence': evidence
            }
        elif len(implemented_aspects) > 0:
            completeness = (len(implemented_aspects) / 2) * 100
            return {
                'status': 'partial',
                'implemented_aspects': implemented_aspects,
                'missing_aspects': missing_aspects,
                'completeness_percentage': completeness,
                'evidence': evidence
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No API endpoints or router files found',
                'evidence': []
            }
    
    def _verify_jwt_auth(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify JWT authentication implementation."""
        dependencies = artifacts.get('dependencies', [])
        auth_files = artifacts.get('auth_files', [])
        
        # Check for JWT libraries
        jwt_libs = [dep for dep in dependencies if any(lib in dep.lower() for lib in ['pyjwt', 'python-jose', 'jwt'])]
        
        evidence = []
        implemented_aspects = []
        missing_aspects = []
        
        if jwt_libs:
            implemented_aspects.append(f'JWT library installed: {jwt_libs[0].split("==")[0]}')
            evidence.append('requirements.txt')
        else:
            missing_aspects.append('No JWT library found in dependencies')
        
        if len(auth_files) > 0:
            implemented_aspects.append(f'{len(auth_files)} auth-related files found')
            evidence.extend(auth_files[:2])  # Include first 2 as evidence
        else:
            missing_aspects.append('No auth-related files found')
        
        if len(implemented_aspects) >= 2:
            return {
                'status': 'implemented',
                'strength': f'JWT authentication: {", ".join(implemented_aspects)}',
                'evidence': evidence
            }
        elif len(implemented_aspects) > 0:
            completeness = (len(implemented_aspects) / 2) * 100
            return {
                'status': 'partial',
                'implemented_aspects': implemented_aspects,
                'missing_aspects': missing_aspects,
                'completeness_percentage': completeness,
                'evidence': evidence
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No JWT authentication implementation found',
                'evidence': []
            }
    
    def _verify_horizontal_scaling(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify horizontal scaling readiness (stateless design, connection pooling)."""
        dependencies = artifacts.get('dependencies', [])
        python_files = artifacts.get('python_files', [])
        
        evidence = []
        implemented_aspects = []
        missing_aspects = []
        
        # Check for connection pooling libraries
        pooling_libs = [dep for dep in dependencies if any(lib in dep.lower() for lib in ['sqlalchemy', 'psycopg2', 'asyncpg', 'redis'])]
        
        if pooling_libs:
            implemented_aspects.append(f'Connection pooling libraries: {len(pooling_libs)} found')
            evidence.append('requirements.txt')
        else:
            missing_aspects.append('No connection pooling libraries found')
        
        # Check for async support (indicator of scalability)
        async_libs = [dep for dep in dependencies if any(lib in dep.lower() for lib in ['asyncio', 'aiohttp', 'uvicorn', 'fastapi'])]
        
        if async_libs:
            implemented_aspects.append('Async support detected')
        
        # Check for stateless indicators (no session files, proper database usage)
        has_models = artifacts.get('has_models_dir', False)
        if has_models:
            implemented_aspects.append('Database models directory found')
        
        # Heuristic: if we have 2+ indicators, consider it implemented
        if len(implemented_aspects) >= 2:
            return {
                'status': 'implemented',
                'strength': f'Horizontal scaling ready: {", ".join(implemented_aspects)}',
                'evidence': evidence
            }
        elif len(implemented_aspects) > 0:
            completeness = (len(implemented_aspects) / 2) * 100
            return {
                'status': 'partial',
                'implemented_aspects': implemented_aspects,
                'missing_aspects': missing_aspects or ['Additional scaling features needed'],
                'completeness_percentage': completeness,
                'evidence': evidence
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No horizontal scaling indicators found',
                'evidence': []
            }
    
    def _verify_api_versioning(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify API versioning strategy."""
        api_files = artifacts.get('api_files', [])
        router_files = artifacts.get('router_files', [])
        python_files = artifacts.get('python_files', [])
        
        # Look for versioning patterns in file paths
        versioning_patterns = ['v1', 'v2', 'api_v1', 'api_v2', 'version']
        
        versioned_files = []
        for file_path in api_files + router_files:
            if any(pattern in file_path.lower() for pattern in versioning_patterns):
                versioned_files.append(file_path)
        
        if len(versioned_files) > 0:
            return {
                'status': 'implemented',
                'strength': f'API versioning detected in {len(versioned_files)} files',
                'evidence': versioned_files[:3]  # Show first 3 as evidence
            }
        else:
            # Check if there's at least an API structure that could support versioning
            if len(api_files) > 0 or artifacts.get('has_api_dir', False):
                return {
                    'status': 'partial',
                    'implemented_aspects': ['API structure exists'],
                    'missing_aspects': ['No explicit versioning pattern found'],
                    'completeness_percentage': 30.0,
                    'evidence': []
                }
            else:
                return {
                    'status': 'missing',
                    'reason': 'No API versioning strategy found',
                    'evidence': []
                }
    
    def _verify_request_validation(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify request validation with Pydantic models."""
        dependencies = artifacts.get('dependencies', [])
        has_models = artifacts.get('has_models_dir', False)
        
        # Check for Pydantic (comes with FastAPI)
        pydantic_deps = [dep for dep in dependencies if 'pydantic' in dep.lower()]
        fastapi_deps = [dep for dep in dependencies if 'fastapi' in dep.lower()]
        
        evidence = []
        implemented_aspects = []
        
        if pydantic_deps or fastapi_deps:
            implemented_aspects.append('Pydantic available (via FastAPI or direct)')
            evidence.append('requirements.txt')
        
        if has_models:
            implemented_aspects.append('Models directory found')
        
        if len(implemented_aspects) >= 1:
            return {
                'status': 'implemented',
                'strength': f'Request validation: {", ".join(implemented_aspects)}',
                'evidence': evidence
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No request validation framework found',
                'evidence': []
            }
    
    def _verify_error_handling(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify centralized error handling."""
        has_middleware = artifacts.get('has_middleware_dir', False)
        python_files = artifacts.get('python_files', [])
        
        # Look for error handling files
        error_files = [f for f in python_files if any(keyword in f.lower() for keyword in ['error', 'exception', 'handler'])]
        
        evidence = []
        implemented_aspects = []
        
        if has_middleware:
            implemented_aspects.append('Middleware directory found')
            evidence.append('middleware/')
        
        if len(error_files) > 0:
            implemented_aspects.append(f'{len(error_files)} error handling files found')
            evidence.extend(error_files[:2])
        
        if len(implemented_aspects) >= 1:
            return {
                'status': 'implemented',
                'strength': f'Error handling: {", ".join(implemented_aspects)}',
                'evidence': evidence
            }
        else:
            return {
                'status': 'partial',
                'implemented_aspects': ['FastAPI default error handling'],
                'missing_aspects': ['No custom error handling found'],
                'completeness_percentage': 40.0,
                'evidence': []
            }
    
    def _verify_cors(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify CORS configuration."""
        dependencies = artifacts.get('dependencies', [])
        has_main = artifacts.get('has_main_py', False)
        
        # FastAPI includes CORS middleware
        fastapi_deps = [dep for dep in dependencies if 'fastapi' in dep.lower()]
        
        if fastapi_deps and has_main:
            return {
                'status': 'implemented',
                'strength': 'CORS middleware available via FastAPI',
                'evidence': ['requirements.txt', 'main.py']
            }
        elif fastapi_deps:
            return {
                'status': 'partial',
                'implemented_aspects': ['FastAPI with CORS support installed'],
                'missing_aspects': ['CORS configuration in main.py not verified'],
                'completeness_percentage': 60.0,
                'evidence': ['requirements.txt']
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No CORS configuration found',
                'evidence': []
            }

    def analyze_data_persistence_layer(self) -> LayerAnalysisResult:
        """
        Analyze the Data Persistence Layer for completeness.
        
        Checks:
        - Neo4j graph operations (neo4j_db.py, graph queries)
        - PostgreSQL usage (models, migrations, queries)
        - Redis caching (redis_db.py, cache decorators)
        - Data consistency mechanisms (transactions, constraints)
        
        Returns:
            LayerAnalysisResult for the Data Persistence layer
        """
        layer_name = "Data Persistence"
        
        # Define Data Persistence capabilities
        capabilities = [
            Capability(
                name="Neo4j Graph Database",
                description="Neo4j graph database configured with connection and query operations",
                category="Graph Database",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="PostgreSQL Relational Database",
                description="PostgreSQL database with models, migrations, and query operations",
                category="Relational Database",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Redis Caching",
                description="Redis caching layer with cache decorators and operations",
                category="Caching",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Database Migrations",
                description="Database migration system (e.g., Alembic) for schema management",
                category="Schema Management",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Data Consistency",
                description="Transaction management and data consistency mechanisms",
                category="Data Integrity",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Connection Pooling",
                description="Database connection pooling for performance",
                category="Performance",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="ORM Models",
                description="ORM models for database entities (SQLAlchemy, etc.)",
                category="Data Modeling",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Query Optimization",
                description="Indexed queries and query optimization strategies",
                category="Performance",
                required=False,
                verification_method="code"
            )
        ]
        
        # Get artifacts for Data Persistence layer
        artifacts = self._extract_data_persistence_artifacts()
        
        # Verify each capability
        implemented_capabilities = []
        missing_capabilities = []
        partial_capabilities = []
        gaps = []
        strengths = []
        
        for capability in capabilities:
            verification_result = self._verify_data_persistence_capability(capability, artifacts)
            
            if verification_result['status'] == 'implemented':
                implemented_capabilities.append(capability)
                if verification_result.get('strength'):
                    strengths.append(verification_result['strength'])
            elif verification_result['status'] == 'missing':
                missing_capabilities.append(capability)
                gap = self._create_gap_from_capability(
                    capability,
                    layer_name,
                    verification_result
                )
                gaps.append(gap)
            elif verification_result['status'] == 'partial':
                partial_cap = PartialCapability(
                    capability=capability,
                    implemented_aspects=verification_result.get('implemented_aspects', []),
                    missing_aspects=verification_result.get('missing_aspects', []),
                    completeness_percentage=verification_result.get('completeness_percentage', 0.0)
                )
                partial_capabilities.append(partial_cap)
                gap = self._create_gap_from_partial_capability(
                    partial_cap,
                    layer_name,
                    verification_result
                )
                gaps.append(gap)
        
        # Calculate completeness score
        completeness_score = self.calculate_completeness_score(
            capabilities,
            implemented_capabilities,
            partial_capabilities
        )
        
        return LayerAnalysisResult(
            layer_name=layer_name,
            completeness_score=completeness_score,
            capabilities_assessed=capabilities,
            implemented_capabilities=implemented_capabilities,
            missing_capabilities=missing_capabilities,
            partial_capabilities=partial_capabilities,
            gaps=gaps,
            strengths=strengths,
            timestamp=datetime.now()
        )
    
    def _extract_data_persistence_artifacts(self) -> Dict[str, Any]:
        """
        Extract Data Persistence-specific artifacts from system info.
        
        Returns:
            Dict containing Data Persistence-relevant files, configs, and structure
        """
        artifacts = {
            'requirements_txt': None,
            'docker_compose': None,
            'has_neo4j_files': False,
            'has_postgres_files': False,
            'has_redis_files': False,
            'has_models_dir': False,
            'has_migrations_dir': False,
            'has_db_dir': False,
            'python_files': [],
            'neo4j_files': [],
            'postgres_files': [],
            'redis_files': [],
            'model_files': [],
            'migration_files': [],
            'dependencies': []
        }
        
        # Get requirements.txt
        if self.system_info.configurations.requirements_txt:
            artifacts['requirements_txt'] = self.system_info.configurations.requirements_txt
            artifacts['dependencies'] = self.system_info.configurations.requirements_txt
        
        # Get docker-compose.yml
        if self.system_info.configurations.docker_compose:
            artifacts['docker_compose'] = self.system_info.configurations.docker_compose
        
        # Check for key directories
        directories = self.system_info.project_structure.directories
        for directory in directories:
            dir_lower = directory.lower()
            if 'model' in dir_lower:
                artifacts['has_models_dir'] = True
            if 'migration' in dir_lower or 'alembic' in dir_lower:
                artifacts['has_migrations_dir'] = True
            if '/db' in dir_lower or directory == 'db' or 'database' in dir_lower:
                artifacts['has_db_dir'] = True
        
        # Check for Python files
        python_files = self.system_info.project_structure.files_by_extension.get('.py', [])
        artifacts['python_files'] = python_files
        
        for file_path in python_files:
            file_lower = file_path.lower()
            
            # Collect Neo4j-related files
            if 'neo4j' in file_lower or 'graph' in file_lower:
                artifacts['neo4j_files'].append(file_path)
                artifacts['has_neo4j_files'] = True
            
            # Collect PostgreSQL-related files
            if any(keyword in file_lower for keyword in ['postgres', 'postgresql', 'psycopg', 'sqlalchemy']):
                artifacts['postgres_files'].append(file_path)
                artifacts['has_postgres_files'] = True
            
            # Collect Redis-related files
            if 'redis' in file_lower or 'cache' in file_lower:
                artifacts['redis_files'].append(file_path)
                artifacts['has_redis_files'] = True
            
            # Collect model files
            if 'model' in file_lower and not 'test' in file_lower:
                artifacts['model_files'].append(file_path)
            
            # Collect migration files
            if 'migration' in file_lower or 'alembic' in file_lower:
                artifacts['migration_files'].append(file_path)
        
        return artifacts
    
    def _verify_data_persistence_capability(
        self,
        capability: Capability,
        artifacts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify a specific Data Persistence capability.
        
        Args:
            capability: The capability to verify
            artifacts: Data Persistence artifacts
            
        Returns:
            Dict with verification result
        """
        capability_verifiers = {
            "Neo4j Graph Database": self._verify_neo4j,
            "PostgreSQL Relational Database": self._verify_postgresql,
            "Redis Caching": self._verify_redis,
            "Database Migrations": self._verify_migrations,
            "Data Consistency": self._verify_data_consistency,
            "Connection Pooling": self._verify_connection_pooling,
            "ORM Models": self._verify_orm_models,
            "Query Optimization": self._verify_query_optimization
        }
        
        verifier = capability_verifiers.get(capability.name)
        if verifier:
            return verifier(artifacts)
        
        # Default verification
        return {
            'status': 'missing',
            'reason': f'No verification method for {capability.name}',
            'evidence': []
        }
    
    def _verify_neo4j(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify Neo4j graph database implementation."""
        dependencies = artifacts.get('dependencies', [])
        neo4j_files = artifacts.get('neo4j_files', [])
        docker_compose = artifacts.get('docker_compose')
        
        # Check for Neo4j dependencies
        neo4j_deps = [dep for dep in dependencies if 'neo4j' in dep.lower()]
        
        # Check for Neo4j in docker-compose
        has_neo4j_service = False
        if docker_compose and isinstance(docker_compose, dict):
            if 'services' in docker_compose:
                for service_name in docker_compose['services'].keys():
                    if 'neo4j' in service_name.lower():
                        has_neo4j_service = True
                        break
        elif docker_compose and isinstance(docker_compose, str):
            # Handle string representation
            if 'neo4j' in docker_compose.lower():
                has_neo4j_service = True
        
        implemented_aspects = []
        missing_aspects = []
        evidence = []
        
        if neo4j_deps:
            implemented_aspects.append('Neo4j Python driver installed')
            evidence.append('requirements.txt')
        else:
            missing_aspects.append('Neo4j Python driver not found')
        
        if has_neo4j_service:
            implemented_aspects.append('Neo4j service in docker-compose')
            evidence.append('docker-compose.yml')
        else:
            missing_aspects.append('Neo4j service not configured')
        
        if neo4j_files:
            implemented_aspects.append(f'Neo4j connection files: {len(neo4j_files)}')
            evidence.extend(neo4j_files[:3])  # Add up to 3 files as evidence
        else:
            missing_aspects.append('No Neo4j connection or query files found')
        
        if len(implemented_aspects) >= 2:
            return {
                'status': 'implemented',
                'strength': f'Neo4j: {", ".join(implemented_aspects)}',
                'evidence': evidence
            }
        elif implemented_aspects:
            completeness = (len(implemented_aspects) / 3.0) * 100
            return {
                'status': 'partial',
                'implemented_aspects': implemented_aspects,
                'missing_aspects': missing_aspects,
                'completeness_percentage': completeness,
                'evidence': evidence
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No Neo4j implementation found',
                'evidence': []
            }
    
    def _verify_postgresql(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify PostgreSQL database implementation."""
        dependencies = artifacts.get('dependencies', [])
        postgres_files = artifacts.get('postgres_files', [])
        model_files = artifacts.get('model_files', [])
        docker_compose = artifacts.get('docker_compose')
        
        # Check for PostgreSQL dependencies
        postgres_deps = [dep for dep in dependencies if any(
            keyword in dep.lower() for keyword in ['psycopg', 'sqlalchemy', 'postgres']
        )]
        
        # Check for PostgreSQL in docker-compose
        has_postgres_service = False
        if docker_compose and isinstance(docker_compose, dict):
            if 'services' in docker_compose:
                for service_name in docker_compose['services'].keys():
                    if any(keyword in service_name.lower() for keyword in ['postgres', 'postgresql']):
                        has_postgres_service = True
                        break
        elif docker_compose and isinstance(docker_compose, str):
            # Handle string representation
            if any(keyword in docker_compose.lower() for keyword in ['postgres', 'postgresql']):
                has_postgres_service = True
        
        implemented_aspects = []
        missing_aspects = []
        evidence = []
        
        if postgres_deps:
            implemented_aspects.append('PostgreSQL drivers installed')
            evidence.append('requirements.txt')
        else:
            missing_aspects.append('PostgreSQL drivers not found')
        
        if has_postgres_service:
            implemented_aspects.append('PostgreSQL service in docker-compose')
            evidence.append('docker-compose.yml')
        else:
            missing_aspects.append('PostgreSQL service not configured')
        
        if model_files:
            implemented_aspects.append(f'Database models: {len(model_files)}')
            evidence.extend(model_files[:3])
        else:
            missing_aspects.append('No database model files found')
        
        if len(implemented_aspects) >= 2:
            return {
                'status': 'implemented',
                'strength': f'PostgreSQL: {", ".join(implemented_aspects)}',
                'evidence': evidence
            }
        elif implemented_aspects:
            completeness = (len(implemented_aspects) / 3.0) * 100
            return {
                'status': 'partial',
                'implemented_aspects': implemented_aspects,
                'missing_aspects': missing_aspects,
                'completeness_percentage': completeness,
                'evidence': evidence
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No PostgreSQL implementation found',
                'evidence': []
            }
    
    def _verify_redis(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify Redis caching implementation."""
        dependencies = artifacts.get('dependencies', [])
        redis_files = artifacts.get('redis_files', [])
        docker_compose = artifacts.get('docker_compose')
        
        # Check for Redis dependencies
        redis_deps = [dep for dep in dependencies if 'redis' in dep.lower()]
        
        # Check for Redis in docker-compose
        has_redis_service = False
        if docker_compose and isinstance(docker_compose, dict):
            if 'services' in docker_compose:
                for service_name in docker_compose['services'].keys():
                    if 'redis' in service_name.lower():
                        has_redis_service = True
                        break
        elif docker_compose and isinstance(docker_compose, str):
            # Handle string representation
            if 'redis' in docker_compose.lower():
                has_redis_service = True
        
        implemented_aspects = []
        missing_aspects = []
        evidence = []
        
        if redis_deps:
            implemented_aspects.append('Redis Python client installed')
            evidence.append('requirements.txt')
        else:
            missing_aspects.append('Redis Python client not found')
        
        if has_redis_service:
            implemented_aspects.append('Redis service in docker-compose')
            evidence.append('docker-compose.yml')
        else:
            missing_aspects.append('Redis service not configured')
        
        if redis_files:
            implemented_aspects.append(f'Redis connection/cache files: {len(redis_files)}')
            evidence.extend(redis_files[:3])
        else:
            missing_aspects.append('No Redis connection or cache files found')
        
        if len(implemented_aspects) >= 2:
            return {
                'status': 'implemented',
                'strength': f'Redis: {", ".join(implemented_aspects)}',
                'evidence': evidence
            }
        elif implemented_aspects:
            completeness = (len(implemented_aspects) / 3.0) * 100
            return {
                'status': 'partial',
                'implemented_aspects': implemented_aspects,
                'missing_aspects': missing_aspects,
                'completeness_percentage': completeness,
                'evidence': evidence
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No Redis implementation found',
                'evidence': []
            }
    
    def _verify_migrations(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify database migration system."""
        dependencies = artifacts.get('dependencies', [])
        has_migrations_dir = artifacts.get('has_migrations_dir', False)
        migration_files = artifacts.get('migration_files', [])
        
        # Check for migration tool dependencies
        migration_deps = [dep for dep in dependencies if any(
            keyword in dep.lower() for keyword in ['alembic', 'migrate', 'flyway']
        )]
        
        implemented_aspects = []
        missing_aspects = []
        evidence = []
        
        if migration_deps:
            implemented_aspects.append('Migration tool installed')
            evidence.append('requirements.txt')
        else:
            missing_aspects.append('No migration tool found')
        
        if has_migrations_dir:
            implemented_aspects.append('Migrations directory exists')
            evidence.append('migrations/ or alembic/')
        else:
            missing_aspects.append('No migrations directory found')
        
        if migration_files:
            implemented_aspects.append(f'Migration files: {len(migration_files)}')
            evidence.extend(migration_files[:2])
        
        if len(implemented_aspects) >= 2:
            return {
                'status': 'implemented',
                'strength': f'Migrations: {", ".join(implemented_aspects)}',
                'evidence': evidence
            }
        elif implemented_aspects:
            completeness = (len(implemented_aspects) / 3.0) * 100
            return {
                'status': 'partial',
                'implemented_aspects': implemented_aspects,
                'missing_aspects': missing_aspects,
                'completeness_percentage': completeness,
                'evidence': evidence
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No migration system found',
                'evidence': []
            }
    
    def _verify_data_consistency(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify data consistency mechanisms."""
        dependencies = artifacts.get('dependencies', [])
        python_files = artifacts.get('python_files', [])
        
        # Check for SQLAlchemy (supports transactions)
        sqlalchemy_deps = [dep for dep in dependencies if 'sqlalchemy' in dep.lower()]
        
        # Look for transaction-related code patterns
        has_transaction_code = False
        transaction_files = []
        
        # This is a simplified check - in a real implementation, we'd parse the files
        for file_path in python_files:
            file_lower = file_path.lower()
            if any(keyword in file_lower for keyword in ['transaction', 'session', 'commit']):
                has_transaction_code = True
                transaction_files.append(file_path)
        
        implemented_aspects = []
        missing_aspects = []
        evidence = []
        
        if sqlalchemy_deps:
            implemented_aspects.append('SQLAlchemy with transaction support')
            evidence.append('requirements.txt')
        
        if has_transaction_code:
            implemented_aspects.append('Transaction management code found')
            evidence.extend(transaction_files[:2])
        
        if len(implemented_aspects) >= 1:
            return {
                'status': 'implemented',
                'strength': f'Data consistency: {", ".join(implemented_aspects)}',
                'evidence': evidence
            }
        else:
            return {
                'status': 'partial',
                'implemented_aspects': ['Database drivers support transactions'],
                'missing_aspects': ['No explicit transaction management found'],
                'completeness_percentage': 40.0,
                'evidence': []
            }
    
    def _verify_connection_pooling(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify database connection pooling."""
        dependencies = artifacts.get('dependencies', [])
        
        # Check for connection pooling support
        pooling_deps = [dep for dep in dependencies if any(
            keyword in dep.lower() for keyword in ['sqlalchemy', 'psycopg2', 'redis']
        )]
        
        if pooling_deps:
            return {
                'status': 'implemented',
                'strength': 'Database drivers with connection pooling support',
                'evidence': ['requirements.txt']
            }
        else:
            return {
                'status': 'partial',
                'implemented_aspects': ['Database connections available'],
                'missing_aspects': ['Connection pooling not explicitly configured'],
                'completeness_percentage': 50.0,
                'evidence': []
            }
    
    def _verify_orm_models(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify ORM models implementation."""
        dependencies = artifacts.get('dependencies', [])
        model_files = artifacts.get('model_files', [])
        has_models_dir = artifacts.get('has_models_dir', False)
        
        # Check for ORM dependencies
        orm_deps = [dep for dep in dependencies if any(
            keyword in dep.lower() for keyword in ['sqlalchemy', 'django', 'peewee']
        )]
        
        implemented_aspects = []
        missing_aspects = []
        evidence = []
        
        if orm_deps:
            implemented_aspects.append('ORM framework installed')
            evidence.append('requirements.txt')
        else:
            missing_aspects.append('No ORM framework found')
        
        if has_models_dir:
            implemented_aspects.append('Models directory exists')
            evidence.append('models/')
        
        if model_files:
            implemented_aspects.append(f'Model files: {len(model_files)}')
            evidence.extend(model_files[:3])
        else:
            missing_aspects.append('No model files found')
        
        if len(implemented_aspects) >= 2:
            return {
                'status': 'implemented',
                'strength': f'ORM Models: {", ".join(implemented_aspects)}',
                'evidence': evidence
            }
        elif implemented_aspects:
            completeness = (len(implemented_aspects) / 3.0) * 100
            return {
                'status': 'partial',
                'implemented_aspects': implemented_aspects,
                'missing_aspects': missing_aspects,
                'completeness_percentage': completeness,
                'evidence': evidence
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No ORM models found',
                'evidence': []
            }
    
    def _verify_query_optimization(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify query optimization strategies."""
        model_files = artifacts.get('model_files', [])
        
        # This is a simplified check - in a real implementation, we'd parse files
        # looking for indexes, query optimization patterns, etc.
        
        if model_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['Database models exist for optimization'],
                'missing_aspects': ['Index definitions not verified', 'Query patterns not analyzed'],
                'completeness_percentage': 30.0,
                'evidence': model_files[:2]
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No model files to analyze for query optimization',
                'evidence': []
            }

    def analyze_ai_reasoning_layer(self) -> LayerAnalysisResult:
        """
        Analyze the AI Reasoning Layer.
        
        Checks:
        - Multi-LLM integration (OpenAI, Anthropic, Ollama configs)
        - Fallback mechanisms (circuit breaker, retry logic)
        - Prompt engineering (prompt templates, context management)
        - Response processing (parsing, validation)
        
        Returns:
            LayerAnalysisResult for AI Reasoning Layer
        """
        layer_name = "AI Reasoning"
        
        # Define capabilities for AI Reasoning Layer
        capabilities = [
            Capability(
                name="Multi-LLM Integration",
                description="Support for multiple LLM providers (OpenAI, Anthropic, Ollama)",
                category="LLM Integration",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="OpenAI Integration",
                description="Integration with OpenAI API",
                category="LLM Integration",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Anthropic Integration",
                description="Integration with Anthropic API",
                category="LLM Integration",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Ollama Integration",
                description="Integration with Ollama for local LLM",
                category="LLM Integration",
                required=False,
                verification_method="code"
            ),
            Capability(
                name="Fallback Mechanisms",
                description="Circuit breaker and retry logic for LLM failures",
                category="Reliability",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Circuit Breaker",
                description="Circuit breaker pattern for LLM service failures",
                category="Reliability",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Retry Logic",
                description="Retry logic with exponential backoff for transient failures",
                category="Reliability",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Prompt Engineering",
                description="Prompt templates and context management",
                category="Prompt Management",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Prompt Templates",
                description="Reusable prompt templates for different tasks",
                category="Prompt Management",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Context Management",
                description="Managing conversation context and token limits",
                category="Prompt Management",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Response Processing",
                description="Parsing and validation of LLM responses",
                category="Response Handling",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Response Parsing",
                description="Parsing structured data from LLM responses",
                category="Response Handling",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Response Validation",
                description="Validating LLM responses for correctness and safety",
                category="Response Handling",
                required=True,
                verification_method="code"
            ),
        ]
        
        # Extract AI Reasoning Layer artifacts
        artifacts = self._extract_ai_reasoning_artifacts()
        
        # Verify each capability
        implemented_capabilities = []
        missing_capabilities = []
        partial_capabilities = []
        gaps = []
        strengths = []
        
        for capability in capabilities:
            verification_result = self._verify_ai_reasoning_capability(capability, artifacts)
            
            if verification_result['status'] == 'implemented':
                implemented_capabilities.append(capability)
                strengths.append(f"{capability.name}: {verification_result.get('evidence', 'Implemented')}")
            elif verification_result['status'] == 'partial':
                partial_cap = PartialCapability(
                    capability=capability,
                    implemented_aspects=verification_result.get('implemented_aspects', []),
                    missing_aspects=verification_result.get('missing_aspects', []),
                    completeness_percentage=verification_result.get('completeness_percentage', 50.0)
                )
                partial_capabilities.append(partial_cap)
                
                # Create gap for partial capability
                gap = self._create_gap_from_partial_capability(partial_cap, layer_name, verification_result)
                gaps.append(gap)
            else:  # missing
                missing_capabilities.append(capability)
                
                # Create gap for missing capability
                gap = self._create_gap_from_capability(capability, layer_name, verification_result)
                gaps.append(gap)
        
        # Calculate completeness score
        completeness_score = self.calculate_completeness_score(
            capabilities, implemented_capabilities, partial_capabilities
        )
        
        return LayerAnalysisResult(
            layer_name=layer_name,
            completeness_score=completeness_score,
            capabilities_assessed=capabilities,
            implemented_capabilities=implemented_capabilities,
            missing_capabilities=missing_capabilities,
            partial_capabilities=partial_capabilities,
            gaps=gaps,
            strengths=strengths,
            timestamp=datetime.now()
        )
    
    def _extract_ai_reasoning_artifacts(self) -> Dict[str, Any]:
        """Extract artifacts relevant to AI Reasoning Layer."""
        artifacts = {}
        
        # Get Python files from project structure
        python_files = self.system_info.project_structure.files_by_extension.get('.py', [])
        
        # Look for LLM service files - include all files in llm directories
        llm_service_patterns = [
            'llm_service', 'llm-service', 'ai_service', 'ai-service',
            'openai', 'anthropic', 'ollama', 'llm_client', 'llm_provider',
            'llm/', 'llm\\', 'ai/', 'ai\\'  # Include all files in llm/ai directories
        ]
        
        llm_files = []
        for pattern in llm_service_patterns:
            for py_file in python_files:
                if pattern in py_file.lower():
                    llm_files.append(py_file)
        
        artifacts['llm_files'] = list(set(llm_files))
        
        # Look for prompt template files
        prompt_patterns = ['prompt', 'template']
        prompt_files = []
        for pattern in prompt_patterns:
            for py_file in python_files:
                if pattern in py_file.lower():
                    prompt_files.append(py_file)
        
        artifacts['prompt_files'] = list(set(prompt_files))
        
        # Look for configuration files with LLM settings
        env_files = [f for f in self.system_info.project_structure.files_by_extension.get('.env', []) 
                     if '.env' in f]
        artifacts['env_files'] = env_files
        
        # Check for LLM-related dependencies
        requirements = self.system_info.configurations.requirements_txt or []
        artifacts['openai_installed'] = any('openai' in req.lower() for req in requirements)
        artifacts['anthropic_installed'] = any('anthropic' in req.lower() for req in requirements)
        
        # Look for services directory
        artifacts['services'] = self.system_info.services
        
        return artifacts
    
    def _verify_ai_reasoning_capability(
        self, capability: Capability, artifacts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify a specific AI Reasoning Layer capability."""
        
        if capability.name == "Multi-LLM Integration":
            return self._verify_multi_llm(artifacts)
        elif capability.name == "OpenAI Integration":
            return self._verify_openai(artifacts)
        elif capability.name == "Anthropic Integration":
            return self._verify_anthropic(artifacts)
        elif capability.name == "Ollama Integration":
            return self._verify_ollama(artifacts)
        elif capability.name == "Fallback Mechanisms":
            return self._verify_fallback_mechanisms(artifacts)
        elif capability.name == "Circuit Breaker":
            return self._verify_circuit_breaker(artifacts)
        elif capability.name == "Retry Logic":
            return self._verify_retry_logic(artifacts)
        elif capability.name == "Prompt Engineering":
            return self._verify_prompt_engineering(artifacts)
        elif capability.name == "Prompt Templates":
            return self._verify_prompt_templates(artifacts)
        elif capability.name == "Context Management":
            return self._verify_context_management(artifacts)
        elif capability.name == "Response Processing":
            return self._verify_response_processing(artifacts)
        elif capability.name == "Response Parsing":
            return self._verify_response_parsing(artifacts)
        elif capability.name == "Response Validation":
            return self._verify_response_validation(artifacts)
        else:
            return {'status': 'missing', 'reason': 'Unknown capability'}
    
    def _verify_multi_llm(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify multi-LLM integration support."""
        llm_files = artifacts.get('llm_files', [])
        
        if not llm_files:
            return {
                'status': 'missing',
                'reason': 'No LLM service files found',
                'evidence': []
            }
        
        # Check if multiple LLM providers are supported
        providers_found = []
        if artifacts.get('openai_installed'):
            providers_found.append('OpenAI')
        if artifacts.get('anthropic_installed'):
            providers_found.append('Anthropic')
        
        # Check for Ollama in files
        for file in llm_files:
            if 'ollama' in file.lower():
                providers_found.append('Ollama')
                break
        
        if len(providers_found) >= 2:
            return {
                'status': 'implemented',
                'evidence': f"Multiple LLM providers found: {', '.join(providers_found)}",
                'providers': providers_found
            }
        elif len(providers_found) == 1:
            return {
                'status': 'partial',
                'implemented_aspects': [f'{providers_found[0]} integration'],
                'missing_aspects': ['Additional LLM provider support'],
                'completeness_percentage': 40.0,
                'evidence': llm_files[:2]
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No LLM provider integrations found',
                'evidence': []
            }
    
    def _verify_openai(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify OpenAI integration."""
        if artifacts.get('openai_installed'):
            llm_files = artifacts.get('llm_files', [])
            return {
                'status': 'implemented',
                'evidence': f"OpenAI package installed, LLM files: {len(llm_files)}"
            }
        else:
            return {
                'status': 'missing',
                'reason': 'OpenAI package not found in dependencies',
                'evidence': []
            }
    
    def _verify_anthropic(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify Anthropic integration."""
        if artifacts.get('anthropic_installed'):
            llm_files = artifacts.get('llm_files', [])
            return {
                'status': 'implemented',
                'evidence': f"Anthropic package installed, LLM files: {len(llm_files)}"
            }
        else:
            return {
                'status': 'missing',
                'reason': 'Anthropic package not found in dependencies',
                'evidence': []
            }
    
    def _verify_ollama(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify Ollama integration."""
        llm_files = artifacts.get('llm_files', [])
        
        # Check for Ollama-specific files
        ollama_files = [f for f in llm_files if 'ollama' in f.lower()]
        
        if ollama_files:
            return {
                'status': 'implemented',
                'evidence': f"Ollama integration files found: {ollama_files}"
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No Ollama integration files found',
                'evidence': []
            }
    
    def _verify_fallback_mechanisms(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify fallback mechanisms (circuit breaker, retry logic)."""
        llm_files = artifacts.get('llm_files', [])
        
        if not llm_files:
            return {
                'status': 'missing',
                'reason': 'No LLM service files to analyze for fallback mechanisms',
                'evidence': []
            }
        
        # This is a simplified check - in a real implementation, we'd parse files
        # looking for circuit breaker patterns, retry decorators, etc.
        
        # Check for common fallback/retry patterns in file names
        fallback_indicators = ['retry', 'fallback', 'circuit', 'breaker', 'resilience']
        has_fallback_files = any(
            indicator in file.lower() 
            for file in llm_files 
            for indicator in fallback_indicators
        )
        
        if has_fallback_files:
            return {
                'status': 'implemented',
                'evidence': 'Fallback mechanism files found'
            }
        else:
            return {
                'status': 'partial',
                'implemented_aspects': ['LLM service exists'],
                'missing_aspects': ['Circuit breaker pattern', 'Retry logic not verified'],
                'completeness_percentage': 30.0,
                'evidence': llm_files[:2]
            }
    
    def _verify_circuit_breaker(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify circuit breaker pattern implementation."""
        llm_files = artifacts.get('llm_files', [])
        
        # Check for circuit breaker patterns
        circuit_breaker_files = [
            f for f in llm_files 
            if 'circuit' in f.lower() or 'breaker' in f.lower()
        ]
        
        if circuit_breaker_files:
            return {
                'status': 'implemented',
                'evidence': f"Circuit breaker files found: {circuit_breaker_files}"
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No circuit breaker implementation found',
                'evidence': []
            }
    
    def _verify_retry_logic(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify retry logic with exponential backoff."""
        llm_files = artifacts.get('llm_files', [])
        
        # Check for retry patterns
        retry_files = [
            f for f in llm_files 
            if 'retry' in f.lower() or 'backoff' in f.lower()
        ]
        
        if retry_files:
            return {
                'status': 'implemented',
                'evidence': f"Retry logic files found: {retry_files}"
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No retry logic implementation found',
                'evidence': []
            }
    
    def _verify_prompt_engineering(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify prompt engineering capabilities."""
        prompt_files = artifacts.get('prompt_files', [])
        
        if not prompt_files:
            return {
                'status': 'missing',
                'reason': 'No prompt template files found',
                'evidence': []
            }
        
        # Check if we have both templates and context management
        has_templates = len(prompt_files) > 0
        
        if has_templates:
            return {
                'status': 'partial',
                'implemented_aspects': ['Prompt files exist'],
                'missing_aspects': ['Template structure not verified', 'Context management not verified'],
                'completeness_percentage': 50.0,
                'evidence': prompt_files[:3]
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No prompt engineering implementation found',
                'evidence': []
            }
    
    def _verify_prompt_templates(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify prompt template implementation."""
        prompt_files = artifacts.get('prompt_files', [])
        
        if prompt_files:
            return {
                'status': 'implemented',
                'evidence': f"Prompt template files found: {len(prompt_files)} files"
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No prompt template files found',
                'evidence': []
            }
    
    def _verify_context_management(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify context management for conversation and token limits."""
        llm_files = artifacts.get('llm_files', [])
        
        # Check for context management patterns
        context_files = [
            f for f in llm_files 
            if 'context' in f.lower() or 'conversation' in f.lower() or 'token' in f.lower()
        ]
        
        if context_files:
            return {
                'status': 'implemented',
                'evidence': f"Context management files found: {context_files}"
            }
        else:
            return {
                'status': 'partial',
                'implemented_aspects': ['LLM service exists'],
                'missing_aspects': ['Context management not verified', 'Token limit handling not verified'],
                'completeness_percentage': 30.0,
                'evidence': llm_files[:2]
            }
    
    def _verify_response_processing(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify response processing capabilities."""
        llm_files = artifacts.get('llm_files', [])
        
        if not llm_files:
            return {
                'status': 'missing',
                'reason': 'No LLM service files to analyze for response processing',
                'evidence': []
            }
        
        # This is a simplified check
        return {
            'status': 'partial',
            'implemented_aspects': ['LLM service exists for response processing'],
            'missing_aspects': ['Response parsing not verified', 'Response validation not verified'],
            'completeness_percentage': 40.0,
            'evidence': llm_files[:2]
        }
    
    def _verify_response_parsing(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify response parsing implementation."""
        llm_files = artifacts.get('llm_files', [])
        
        # Check for parsing-related files
        parsing_files = [
            f for f in llm_files 
            if 'parse' in f.lower() or 'parser' in f.lower()
        ]
        
        if parsing_files:
            return {
                'status': 'implemented',
                'evidence': f"Response parsing files found: {parsing_files}"
            }
        elif llm_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['LLM service exists'],
                'missing_aspects': ['Dedicated parsing logic not verified'],
                'completeness_percentage': 40.0,
                'evidence': llm_files[:2]
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No response parsing implementation found',
                'evidence': []
            }
    
    def _verify_response_validation(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify response validation implementation."""
        llm_files = artifacts.get('llm_files', [])
        
        # Check for validation-related files
        validation_files = [
            f for f in llm_files 
            if 'validat' in f.lower() or 'sanitiz' in f.lower() or 'verify' in f.lower()
        ]
        
        if validation_files:
            return {
                'status': 'implemented',
                'evidence': f"Response validation files found: {validation_files}"
            }
        elif llm_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['LLM service exists'],
                'missing_aspects': ['Response validation logic not verified', 'Safety checks not verified'],
                'completeness_percentage': 30.0,
                'evidence': llm_files[:2]
            }
        else:
            return {
                'status': 'missing',
                'reason': 'No response validation implementation found',
                'evidence': []
            }

    def analyze_integration_layer(self) -> LayerAnalysisResult:
        """
        Analyze the Integration Layer.
        
        Checks:
        - GitHub webhook handling (webhook endpoints, signature verification)
        - OAuth 2.0 implementation (NextAuth, OAuth flows)
        - External API integrations (GitHub API, LLM APIs)
        
        Returns:
            LayerAnalysisResult for Integration Layer
        """
        layer_name = "Integration"
        
        # Define capabilities for Integration Layer
        capabilities = [
            Capability(
                name="GitHub Webhook Handling",
                description="Endpoints for receiving and processing GitHub webhooks",
                category="Webhooks",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Webhook Signature Verification",
                description="Verification of GitHub webhook signatures for security",
                category="Webhooks",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Webhook Event Processing",
                description="Processing of different GitHub webhook events (PR, push, etc.)",
                category="Webhooks",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="OAuth 2.0 Implementation",
                description="OAuth 2.0 authentication flow implementation",
                category="Authentication",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="NextAuth Integration",
                description="NextAuth.js for OAuth authentication",
                category="Authentication",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="OAuth Provider Configuration",
                description="Configuration for OAuth providers (GitHub, etc.)",
                category="Authentication",
                required=True,
                verification_method="config"
            ),
            Capability(
                name="GitHub API Integration",
                description="Integration with GitHub REST/GraphQL API",
                category="External APIs",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="GitHub API Authentication",
                description="Authentication with GitHub API using tokens",
                category="External APIs",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="GitHub API Rate Limiting",
                description="Handling of GitHub API rate limits",
                category="External APIs",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="External API Error Handling",
                description="Error handling for external API calls",
                category="External APIs",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="API Retry Logic",
                description="Retry logic for failed external API calls",
                category="External APIs",
                required=True,
                verification_method="code"
            ),
            Capability(
                name="Secure Credential Storage",
                description="Secure storage of API keys and tokens",
                category="Security",
                required=True,
                verification_method="config"
            ),
        ]
        
        # Extract Integration Layer artifacts
        artifacts = self._extract_integration_artifacts()
        
        # Verify each capability
        implemented_capabilities = []
        missing_capabilities = []
        partial_capabilities = []
        gaps = []
        strengths = []
        
        for capability in capabilities:
            verification_result = self._verify_integration_capability(capability, artifacts)
            
            if verification_result['status'] == 'implemented':
                implemented_capabilities.append(capability)
                strengths.append(f"{capability.name}: {verification_result.get('evidence', 'Implemented')}")
            elif verification_result['status'] == 'partial':
                partial_cap = PartialCapability(
                    capability=capability,
                    implemented_aspects=verification_result.get('implemented_aspects', []),
                    missing_aspects=verification_result.get('missing_aspects', []),
                    completeness_percentage=verification_result.get('completeness_percentage', 50.0)
                )
                partial_capabilities.append(partial_cap)
                
                # Create gap for partial capability
                gap = self._create_gap_from_partial_capability(partial_cap, layer_name, verification_result)
                gaps.append(gap)
            else:  # missing
                missing_capabilities.append(capability)
                
                # Create gap for missing capability
                gap = self._create_gap_from_capability(capability, layer_name, verification_result)
                gaps.append(gap)
        
        # Calculate completeness score
        completeness_score = self.calculate_completeness_score(
            capabilities, implemented_capabilities, partial_capabilities
        )
        
        return LayerAnalysisResult(
            layer_name=layer_name,
            completeness_score=completeness_score,
            capabilities_assessed=capabilities,
            implemented_capabilities=implemented_capabilities,
            missing_capabilities=missing_capabilities,
            partial_capabilities=partial_capabilities,
            gaps=gaps,
            strengths=strengths,
            timestamp=datetime.now()
        )
    
    def _extract_integration_artifacts(self) -> Dict[str, Any]:
        """Extract artifacts relevant to Integration Layer."""
        artifacts = {}
        
        # Get Python files from project structure
        python_files = self.system_info.project_structure.files_by_extension.get('.py', [])
        
        # Look for webhook-related files
        webhook_patterns = ['webhook', 'github_webhook', 'gh_webhook']
        webhook_files = []
        for pattern in webhook_patterns:
            for py_file in python_files:
                if pattern in py_file.lower():
                    webhook_files.append(py_file)
        
        artifacts['webhook_files'] = list(set(webhook_files))
        
        # Look for OAuth/auth-related files
        oauth_patterns = ['oauth', 'nextauth', 'auth', 'authentication']
        oauth_files = []
        for pattern in oauth_patterns:
            for py_file in python_files:
                if pattern in py_file.lower():
                    oauth_files.append(py_file)
        
        # Also check TypeScript/JavaScript files for NextAuth
        ts_files = self.system_info.project_structure.files_by_extension.get('.ts', [])
        js_files = self.system_info.project_structure.files_by_extension.get('.js', [])
        
        for pattern in oauth_patterns:
            for ts_file in ts_files:
                if pattern in ts_file.lower():
                    oauth_files.append(ts_file)
            for js_file in js_files:
                if pattern in js_file.lower():
                    oauth_files.append(js_file)
        
        artifacts['oauth_files'] = list(set(oauth_files))
        
        # Look for GitHub API integration files
        github_api_patterns = ['github', 'gh_api', 'github_client', 'github_service']
        github_api_files = []
        for pattern in github_api_patterns:
            for py_file in python_files:
                if pattern in py_file.lower() and 'webhook' not in py_file.lower():
                    github_api_files.append(py_file)
        
        artifacts['github_api_files'] = list(set(github_api_files))
        
        # Check for GitHub-related dependencies
        requirements = self.system_info.configurations.requirements_txt or []
        artifacts['pygithub_installed'] = any('pygithub' in req.lower() or 'github' in req.lower() for req in requirements)
        
        # Check for NextAuth in package.json
        package_json = self.system_info.configurations.package_json or {}
        dependencies = package_json.get('dependencies', {})
        dev_dependencies = package_json.get('devDependencies', {})
        
        artifacts['nextauth_installed'] = 'next-auth' in dependencies or 'next-auth' in dev_dependencies
        
        # Look for environment variables related to OAuth and GitHub
        env_files = [f for f in self.system_info.project_structure.files_by_extension.get('.env', []) 
                     if '.env' in f]
        artifacts['env_files'] = env_files
        
        # Check for services
        artifacts['services'] = self.system_info.services
        
        return artifacts
    
    def _verify_integration_capability(
        self, capability: Capability, artifacts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify a specific Integration Layer capability."""
        capability_verifiers = {
            "GitHub Webhook Handling": self._verify_github_webhooks,
            "Webhook Signature Verification": self._verify_webhook_signature,
            "Webhook Event Processing": self._verify_webhook_events,
            "OAuth 2.0 Implementation": self._verify_oauth,
            "NextAuth Integration": self._verify_nextauth,
            "OAuth Provider Configuration": self._verify_oauth_config,
            "GitHub API Integration": self._verify_github_api,
            "GitHub API Authentication": self._verify_github_api_auth,
            "GitHub API Rate Limiting": self._verify_github_rate_limiting,
            "External API Error Handling": self._verify_external_api_error_handling,
            "API Retry Logic": self._verify_api_retry_logic,
            "Secure Credential Storage": self._verify_secure_credentials,
        }
        
        verifier = capability_verifiers.get(capability.name)
        if verifier:
            return verifier(artifacts)
        
        # Default verification
        return self._verify_capability(capability, artifacts)
    
    def _verify_github_webhooks(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify GitHub webhook handling implementation."""
        webhook_files = artifacts.get('webhook_files', [])
        
        if webhook_files:
            return {
                'status': 'implemented',
                'evidence': f"Webhook files found: {webhook_files}"
            }
        
        # Check if there are any API files that might handle webhooks
        services = artifacts.get('services', [])
        webhook_services = [s for s in services if 'webhook' in s.lower() or 'github' in s.lower()]
        
        if webhook_services:
            return {
                'status': 'partial',
                'implemented_aspects': ['Webhook service exists'],
                'missing_aspects': ['Webhook endpoint implementation not verified'],
                'completeness_percentage': 50.0,
                'evidence': webhook_services
            }
        
        return {
            'status': 'missing',
            'reason': 'No webhook handling implementation found',
            'evidence': []
        }
    
    def _verify_webhook_signature(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify webhook signature verification implementation."""
        webhook_files = artifacts.get('webhook_files', [])
        
        # Look for signature verification patterns
        if webhook_files:
            # If webhook files exist, assume partial implementation
            return {
                'status': 'partial',
                'implemented_aspects': ['Webhook endpoints exist'],
                'missing_aspects': ['Signature verification not verified in code'],
                'completeness_percentage': 40.0,
                'evidence': webhook_files
            }
        
        return {
            'status': 'missing',
            'reason': 'No webhook signature verification found',
            'evidence': []
        }
    
    def _verify_webhook_events(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify webhook event processing implementation."""
        webhook_files = artifacts.get('webhook_files', [])
        
        if webhook_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['Webhook infrastructure exists'],
                'missing_aspects': ['Event processing logic not verified'],
                'completeness_percentage': 50.0,
                'evidence': webhook_files
            }
        
        return {
            'status': 'missing',
            'reason': 'No webhook event processing found',
            'evidence': []
        }
    
    def _verify_oauth(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify OAuth 2.0 implementation."""
        oauth_files = artifacts.get('oauth_files', [])
        nextauth_installed = artifacts.get('nextauth_installed', False)
        
        if nextauth_installed and oauth_files:
            return {
                'status': 'implemented',
                'evidence': f"NextAuth installed and OAuth files found: {oauth_files[:3]}"
            }
        elif nextauth_installed:
            return {
                'status': 'partial',
                'implemented_aspects': ['NextAuth library installed'],
                'missing_aspects': ['OAuth configuration files not found'],
                'completeness_percentage': 60.0,
                'evidence': ['next-auth in package.json']
            }
        elif oauth_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['OAuth-related files exist'],
                'missing_aspects': ['NextAuth not installed'],
                'completeness_percentage': 40.0,
                'evidence': oauth_files[:3]
            }
        
        return {
            'status': 'missing',
            'reason': 'No OAuth 2.0 implementation found',
            'evidence': []
        }
    
    def _verify_nextauth(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify NextAuth integration."""
        nextauth_installed = artifacts.get('nextauth_installed', False)
        oauth_files = artifacts.get('oauth_files', [])
        
        # Look for NextAuth configuration files
        nextauth_config_files = [f for f in oauth_files if 'nextauth' in f.lower() or '[...nextauth]' in f.lower()]
        
        if nextauth_installed and nextauth_config_files:
            return {
                'status': 'implemented',
                'evidence': f"NextAuth installed with config: {nextauth_config_files}"
            }
        elif nextauth_installed:
            return {
                'status': 'partial',
                'implemented_aspects': ['NextAuth library installed'],
                'missing_aspects': ['NextAuth configuration not found'],
                'completeness_percentage': 50.0,
                'evidence': ['next-auth in package.json']
            }
        
        return {
            'status': 'missing',
            'reason': 'NextAuth not installed',
            'evidence': []
        }
    
    def _verify_oauth_config(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify OAuth provider configuration."""
        env_files = artifacts.get('env_files', [])
        oauth_files = artifacts.get('oauth_files', [])
        
        if env_files and oauth_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['Environment files exist', 'OAuth files exist'],
                'missing_aspects': ['OAuth provider configuration not verified in env files'],
                'completeness_percentage': 60.0,
                'evidence': env_files + oauth_files[:2]
            }
        elif env_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['Environment files exist'],
                'missing_aspects': ['OAuth configuration not verified'],
                'completeness_percentage': 30.0,
                'evidence': env_files
            }
        
        return {
            'status': 'missing',
            'reason': 'No OAuth provider configuration found',
            'evidence': []
        }
    
    def _verify_github_api(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify GitHub API integration."""
        github_api_files = artifacts.get('github_api_files', [])
        pygithub_installed = artifacts.get('pygithub_installed', False)
        
        if github_api_files and pygithub_installed:
            return {
                'status': 'implemented',
                'evidence': f"GitHub API files found with PyGithub: {github_api_files[:3]}"
            }
        elif github_api_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['GitHub API integration files exist'],
                'missing_aspects': ['PyGithub library not verified'],
                'completeness_percentage': 70.0,
                'evidence': github_api_files[:3]
            }
        elif pygithub_installed:
            return {
                'status': 'partial',
                'implemented_aspects': ['PyGithub library installed'],
                'missing_aspects': ['GitHub API integration files not found'],
                'completeness_percentage': 40.0,
                'evidence': ['PyGithub in requirements']
            }
        
        return {
            'status': 'missing',
            'reason': 'No GitHub API integration found',
            'evidence': []
        }
    
    def _verify_github_api_auth(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify GitHub API authentication."""
        github_api_files = artifacts.get('github_api_files', [])
        env_files = artifacts.get('env_files', [])
        
        if github_api_files and env_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['GitHub API files exist', 'Environment files exist'],
                'missing_aspects': ['GitHub token authentication not verified in code'],
                'completeness_percentage': 60.0,
                'evidence': github_api_files[:2] + env_files
            }
        elif github_api_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['GitHub API files exist'],
                'missing_aspects': ['Authentication configuration not found'],
                'completeness_percentage': 40.0,
                'evidence': github_api_files[:2]
            }
        
        return {
            'status': 'missing',
            'reason': 'No GitHub API authentication found',
            'evidence': []
        }
    
    def _verify_github_rate_limiting(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify GitHub API rate limiting handling."""
        github_api_files = artifacts.get('github_api_files', [])
        
        if github_api_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['GitHub API integration exists'],
                'missing_aspects': ['Rate limiting handling not verified'],
                'completeness_percentage': 30.0,
                'evidence': github_api_files[:2]
            }
        
        return {
            'status': 'missing',
            'reason': 'No GitHub API rate limiting handling found',
            'evidence': []
        }
    
    def _verify_external_api_error_handling(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify external API error handling."""
        github_api_files = artifacts.get('github_api_files', [])
        webhook_files = artifacts.get('webhook_files', [])
        
        integration_files = github_api_files + webhook_files
        
        if integration_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['External API integration exists'],
                'missing_aspects': ['Error handling logic not verified'],
                'completeness_percentage': 40.0,
                'evidence': integration_files[:3]
            }
        
        return {
            'status': 'missing',
            'reason': 'No external API error handling found',
            'evidence': []
        }
    
    def _verify_api_retry_logic(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify API retry logic implementation."""
        github_api_files = artifacts.get('github_api_files', [])
        
        if github_api_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['API integration exists'],
                'missing_aspects': ['Retry logic not verified'],
                'completeness_percentage': 30.0,
                'evidence': github_api_files[:2]
            }
        
        return {
            'status': 'missing',
            'reason': 'No API retry logic found',
            'evidence': []
        }
    
    def _verify_secure_credentials(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify secure credential storage."""
        env_files = artifacts.get('env_files', [])
        
        if env_files:
            return {
                'status': 'partial',
                'implemented_aspects': ['Environment files exist for credentials'],
                'missing_aspects': ['Secure storage mechanism not verified (e.g., secrets manager)'],
                'completeness_percentage': 50.0,
                'evidence': env_files
            }
        
        return {
            'status': 'missing',
            'reason': 'No secure credential storage found',
            'evidence': []
        }
