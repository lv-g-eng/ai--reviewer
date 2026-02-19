"""
Unit tests for LayerAnalyzer.

Tests the layer analysis functionality including completeness score calculation
and capability verification logic.
"""

import pytest
from datetime import datetime
from pathlib import Path

from tools.architecture_evaluation.layer_analyzer import LayerAnalyzer
from tools.architecture_evaluation.models import (
    Capability,
    LayerAnalysisResult,
    Gap,
    PartialCapability
)
from tools.architecture_evaluation.system_inspector import (
    SystemInfo,
    ProjectStructure,
    ConfigurationFiles,
    Documentation
)


@pytest.fixture
def sample_system_info():
    """Create a sample SystemInfo for testing."""
    project_structure = ProjectStructure(
        root_path=Path("/test/project"),
        directories=["src", "tests", "frontend", "backend"],
        files_by_extension={
            ".py": ["src/main.py", "src/auth.py", "tests/test_main.py"],
            ".ts": ["frontend/app.ts", "frontend/auth.ts"],
            ".json": ["package.json", "tsconfig.json"]
        },
        total_files=6,
        total_directories=4
    )
    
    configurations = ConfigurationFiles(
        docker_compose={"services": {"api": {}, "db": {}}},
        package_json={"dependencies": {"react": "^18.0.0", "next": "^14.0.0"}},
        requirements_txt=["fastapi==0.104.0", "pytest==7.4.0"]
    )
    
    documentation = Documentation(
        readme="# Test Project\nThis is a test project with React and FastAPI.",
        architecture_docs={"docs/architecture.md": "Architecture documentation"},
        other_docs={}
    )
    
    return SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation=documentation,
        services=["api", "db"],
        technologies={
            "frontend": ["React", "Next.js"],
            "backend": ["FastAPI"],
            "database": [],
            "infrastructure": ["Docker Compose"],
            "testing": ["pytest"]
        }
    )


@pytest.fixture
def layer_analyzer(sample_system_info):
    """Create a LayerAnalyzer instance for testing."""
    return LayerAnalyzer(sample_system_info)


def test_calculate_completeness_score_all_implemented(layer_analyzer):
    """Test completeness score calculation when all capabilities are implemented."""
    capabilities = [
        Capability("Auth", "Authentication", "Security", True, "Code"),
        Capability("Cache", "Caching", "Performance", True, "Config"),
    ]
    implemented = capabilities.copy()
    partial = []
    
    score = layer_analyzer.calculate_completeness_score(capabilities, implemented, partial)
    
    assert score == 1.0


def test_calculate_completeness_score_none_implemented(layer_analyzer):
    """Test completeness score calculation when no capabilities are implemented."""
    capabilities = [
        Capability("Auth", "Authentication", "Security", True, "Code"),
        Capability("Cache", "Caching", "Performance", True, "Config"),
    ]
    implemented = []
    partial = []
    
    score = layer_analyzer.calculate_completeness_score(capabilities, implemented, partial)
    
    assert score == 0.0


def test_calculate_completeness_score_half_implemented(layer_analyzer):
    """Test completeness score calculation when half are implemented."""
    capabilities = [
        Capability("Auth", "Authentication", "Security", True, "Code"),
        Capability("Cache", "Caching", "Performance", True, "Config"),
    ]
    implemented = [capabilities[0]]
    partial = []
    
    score = layer_analyzer.calculate_completeness_score(capabilities, implemented, partial)
    
    assert score == 0.5


def test_calculate_completeness_score_with_partial(layer_analyzer):
    """Test completeness score calculation with partial implementations."""
    capabilities = [
        Capability("Auth", "Authentication", "Security", True, "Code"),
        Capability("Cache", "Caching", "Performance", True, "Config"),
    ]
    implemented = []
    partial = [
        PartialCapability(
            capability=capabilities[0],
            implemented_aspects=["Basic auth"],
            missing_aspects=["OAuth"],
            completeness_percentage=50.0
        ),
        PartialCapability(
            capability=capabilities[1],
            implemented_aspects=["Redis"],
            missing_aspects=["Memcached"],
            completeness_percentage=75.0
        )
    ]
    
    score = layer_analyzer.calculate_completeness_score(capabilities, implemented, partial)
    
    # (0 + 0.5 + 0.75) / 2 = 0.625
    assert abs(score - 0.625) < 0.001


def test_calculate_completeness_score_only_required(layer_analyzer):
    """Test that only required capabilities are counted in score."""
    capabilities = [
        Capability("Auth", "Authentication", "Security", True, "Code"),
        Capability("Cache", "Caching", "Performance", False, "Config"),  # Not required
    ]
    implemented = [capabilities[0]]
    partial = []
    
    score = layer_analyzer.calculate_completeness_score(capabilities, implemented, partial)
    
    # Only 1 required capability, and it's implemented
    assert score == 1.0


def test_calculate_completeness_score_no_required(layer_analyzer):
    """Test completeness score when no capabilities are required."""
    capabilities = [
        Capability("Feature1", "Optional feature 1", "Feature", False, "Code"),
        Capability("Feature2", "Optional feature 2", "Feature", False, "Code"),
    ]
    implemented = []
    partial = []
    
    score = layer_analyzer.calculate_completeness_score(capabilities, implemented, partial)
    
    # No required capabilities, so score should be 1.0
    assert score == 1.0


def test_analyze_layer_basic(layer_analyzer):
    """Test basic layer analysis."""
    capabilities = [
        Capability("React", "React framework", "Frontend", True, "Code"),
        Capability("FastAPI", "FastAPI framework", "Backend", True, "Code"),
    ]
    
    result = layer_analyzer.analyze_layer("Frontend", capabilities)
    
    assert isinstance(result, LayerAnalysisResult)
    assert result.layer_name == "Frontend"
    assert 0.0 <= result.completeness_score <= 1.0
    assert len(result.capabilities_assessed) == 2
    assert isinstance(result.timestamp, datetime)


def test_analyze_layer_with_artifacts(layer_analyzer):
    """Test layer analysis with custom artifacts."""
    capabilities = [
        Capability("Auth", "Authentication", "Security", True, "Code"),
    ]
    
    artifacts = {
        'files': ['src/auth.py', 'src/auth_middleware.py'],
        'directories': ['src/auth'],
        'configurations': {},
        'documentation': {},
        'technologies': ['JWT', 'OAuth']
    }
    
    result = layer_analyzer.analyze_layer("Backend API", capabilities, artifacts)
    
    assert result.layer_name == "Backend API"
    assert len(result.capabilities_assessed) == 1


def test_verify_capability_by_code_implemented(layer_analyzer):
    """Test capability verification by code when implemented."""
    capability = Capability("Auth", "Authentication", "Security", True, "Code")
    artifacts = {
        'files': ['src/auth.py', 'src/auth_middleware.py'],
        'directories': ['src/auth'],
        'technologies': ['JWT', 'Authentication']
    }
    
    result = layer_analyzer._verify_by_code_analysis(capability, artifacts, "Backend")
    
    assert result['status'] == 'implemented'
    assert 'strength' in result


def test_verify_capability_by_code_missing(layer_analyzer):
    """Test capability verification by code when missing."""
    capability = Capability("GraphQL", "GraphQL API", "Backend", True, "Code")
    artifacts = {
        'files': ['src/main.py'],
        'directories': ['src'],
        'technologies': ['REST']
    }
    
    result = layer_analyzer._verify_by_code_analysis(capability, artifacts, "Backend")
    
    assert result['status'] == 'missing'
    assert 'reason' in result


def test_verify_capability_by_config_implemented(layer_analyzer):
    """Test capability verification by config when implemented."""
    capability = Capability("Redis", "Redis caching", "Data", True, "Config")
    artifacts = {
        'configurations': {
            'docker_compose': {'services': {'redis': {'image': 'redis:7.2'}}}
        }
    }
    
    result = layer_analyzer._verify_by_config(capability, artifacts, "Data Persistence")
    
    assert result['status'] == 'implemented'


def test_verify_capability_by_config_missing(layer_analyzer):
    """Test capability verification by config when missing."""
    capability = Capability("MongoDB", "MongoDB database", "Data", True, "Config")
    artifacts = {
        'configurations': {
            'docker_compose': {'services': {'postgres': {'image': 'postgres:16'}}}
        }
    }
    
    result = layer_analyzer._verify_by_config(capability, artifacts, "Data Persistence")
    
    assert result['status'] == 'missing'


def test_verify_capability_by_documentation_implemented(layer_analyzer):
    """Test capability verification by documentation when implemented."""
    capability = Capability("WebSocket", "WebSocket support", "Integration", True, "Documentation")
    artifacts = {
        'documentation': {
            'readme': 'This project uses WebSocket for real-time communication.',
            'architecture_docs': {}
        }
    }
    
    result = layer_analyzer._verify_by_documentation(capability, artifacts, "Integration")
    
    assert result['status'] == 'implemented'


def test_verify_capability_by_documentation_missing(layer_analyzer):
    """Test capability verification by documentation when missing."""
    capability = Capability("gRPC", "gRPC support", "Integration", True, "Documentation")
    artifacts = {
        'documentation': {
            'readme': 'This project uses REST APIs.',
            'architecture_docs': {}
        }
    }
    
    result = layer_analyzer._verify_by_documentation(capability, artifacts, "Integration")
    
    assert result['status'] == 'missing'


def test_create_gap_from_capability(layer_analyzer):
    """Test gap creation from missing capability."""
    capability = Capability("OAuth", "OAuth 2.0", "Security", True, "Code")
    verification_result = {
        'status': 'missing',
        'reason': 'No OAuth implementation found'
    }
    
    gap = layer_analyzer._create_gap_from_capability(
        capability,
        "Backend API",
        verification_result
    )
    
    assert isinstance(gap, Gap)
    assert gap.layer == "Backend API"
    assert gap.category == "Security"
    assert "OAuth" in gap.description
    assert gap.impact == "High"  # Required capability


def test_create_gap_from_partial_capability(layer_analyzer):
    """Test gap creation from partial capability."""
    capability = Capability("Auth", "Authentication", "Security", True, "Code")
    partial_cap = PartialCapability(
        capability=capability,
        implemented_aspects=["Basic auth"],
        missing_aspects=["OAuth", "2FA"],
        completeness_percentage=40.0
    )
    verification_result = {
        'status': 'partial',
        'completeness_percentage': 40.0
    }
    
    gap = layer_analyzer._create_gap_from_partial_capability(
        partial_cap,
        "Backend API",
        verification_result
    )
    
    assert isinstance(gap, Gap)
    assert gap.layer == "Backend API"
    assert "40%" in gap.description
    assert gap.impact == "Medium"  # 30-70% complete


def test_analyze_layer_creates_gaps_for_missing(layer_analyzer):
    """Test that analyze_layer creates gaps for missing capabilities."""
    capabilities = [
        Capability("NonExistent", "Does not exist", "Test", True, "Code"),
    ]
    
    result = layer_analyzer.analyze_layer("Test Layer", capabilities)
    
    assert len(result.missing_capabilities) > 0
    assert len(result.gaps) > 0
    assert result.completeness_score < 1.0


def test_completeness_score_range(layer_analyzer):
    """Test that completeness score is always between 0.0 and 1.0."""
    capabilities = [
        Capability("Cap1", "Capability 1", "Test", True, "Code"),
        Capability("Cap2", "Capability 2", "Test", True, "Code"),
        Capability("Cap3", "Capability 3", "Test", True, "Code"),
    ]
    
    # Test with various combinations
    for impl_count in range(len(capabilities) + 1):
        implemented = capabilities[:impl_count]
        score = layer_analyzer.calculate_completeness_score(
            capabilities,
            implemented,
            []
        )
        assert 0.0 <= score <= 1.0
        assert score == impl_count / len(capabilities)


# Frontend Layer Analysis Tests

@pytest.fixture
def frontend_system_info():
    """Create a SystemInfo with Frontend-specific data."""
    project_structure = ProjectStructure(
        root_path=Path("/test/frontend-project"),
        directories=[
            "src",
            "src/app",
            "src/components",
            "public",
            "tests"
        ],
        files_by_extension={
            ".tsx": [
                "src/app/page.tsx",
                "src/app/layout.tsx",
                "src/components/Button.tsx",
                "src/components/Header.tsx"
            ],
            ".ts": ["src/lib/utils.ts"],
            ".json": ["package.json", "tsconfig.json", "public/manifest.json"],
            ".js": ["public/service-worker.js"]
        },
        total_files=8,
        total_directories=5
    )
    
    configurations = ConfigurationFiles(
        docker_compose=None,
        package_json={
            "dependencies": {
                "react": "^19.0.0",
                "next": "^14.0.0",
                "socket.io-client": "^4.5.0",
                "@reduxjs/toolkit": "^1.9.0"
            },
            "devDependencies": {
                "typescript": "^5.0.0"
            }
        },
        requirements_txt=None
    )
    
    documentation = Documentation(
        readme="# Frontend Project\nBuilt with React 19 and Next.js 14.",
        architecture_docs={},
        other_docs={}
    )
    
    return SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation=documentation,
        services=[],
        technologies={
            "frontend": ["React", "Next.js", "Socket.io"],
            "backend": [],
            "database": [],
            "infrastructure": [],
            "testing": []
        }
    )


@pytest.fixture
def frontend_analyzer(frontend_system_info):
    """Create a LayerAnalyzer for Frontend testing."""
    return LayerAnalyzer(frontend_system_info)


def test_analyze_frontend_layer_complete(frontend_analyzer):
    """Test Frontend layer analysis with complete implementation."""
    result = frontend_analyzer.analyze_frontend_layer()
    
    assert isinstance(result, LayerAnalysisResult)
    assert result.layer_name == "Frontend"
    assert 0.0 <= result.completeness_score <= 1.0
    assert len(result.capabilities_assessed) == 8  # All Frontend capabilities
    assert isinstance(result.timestamp, datetime)


def test_analyze_frontend_layer_has_react(frontend_analyzer):
    """Test that Frontend analysis detects React."""
    result = frontend_analyzer.analyze_frontend_layer()
    
    # Check if React capability is implemented
    react_caps = [cap for cap in result.implemented_capabilities if cap.name == "React Implementation"]
    assert len(react_caps) > 0


def test_analyze_frontend_layer_has_nextjs(frontend_analyzer):
    """Test that Frontend analysis detects Next.js."""
    result = frontend_analyzer.analyze_frontend_layer()
    
    # Check if Next.js capability is implemented
    nextjs_caps = [cap for cap in result.implemented_capabilities if cap.name == "Next.js Implementation"]
    assert len(nextjs_caps) > 0


def test_analyze_frontend_layer_has_websocket(frontend_analyzer):
    """Test that Frontend analysis detects WebSocket."""
    result = frontend_analyzer.analyze_frontend_layer()
    
    # Check if WebSocket capability is implemented
    ws_caps = [cap for cap in result.implemented_capabilities if cap.name == "WebSocket Connectivity"]
    assert len(ws_caps) > 0


def test_analyze_frontend_layer_has_pwa_manifest(frontend_analyzer):
    """Test that Frontend analysis detects PWA manifest."""
    result = frontend_analyzer.analyze_frontend_layer()
    
    # Check if PWA Manifest capability is implemented
    manifest_caps = [cap for cap in result.implemented_capabilities if cap.name == "PWA Manifest"]
    assert len(manifest_caps) > 0


def test_analyze_frontend_layer_has_service_worker(frontend_analyzer):
    """Test that Frontend analysis detects service worker."""
    result = frontend_analyzer.analyze_frontend_layer()
    
    # Check if Service Worker capability is implemented
    sw_caps = [cap for cap in result.implemented_capabilities if cap.name == "Service Worker"]
    assert len(sw_caps) > 0


def test_analyze_frontend_layer_has_components(frontend_analyzer):
    """Test that Frontend analysis detects UI components."""
    result = frontend_analyzer.analyze_frontend_layer()
    
    # Check if UI Components capability is implemented
    comp_caps = [cap for cap in result.implemented_capabilities if cap.name == "UI Components"]
    assert len(comp_caps) > 0


def test_analyze_frontend_layer_has_state_management(frontend_analyzer):
    """Test that Frontend analysis detects state management."""
    result = frontend_analyzer.analyze_frontend_layer()
    
    # Check if State Management capability is implemented
    state_caps = [cap for cap in result.implemented_capabilities if cap.name == "State Management"]
    assert len(state_caps) > 0


def test_analyze_frontend_layer_has_routing(frontend_analyzer):
    """Test that Frontend analysis detects routing."""
    result = frontend_analyzer.analyze_frontend_layer()
    
    # Check if Routing capability is implemented
    routing_caps = [cap for cap in result.implemented_capabilities if cap.name == "Routing"]
    assert len(routing_caps) > 0


def test_analyze_frontend_layer_missing_features():
    """Test Frontend layer analysis with missing features."""
    # Create minimal system info without PWA features
    project_structure = ProjectStructure(
        root_path=Path("/test/minimal-frontend"),
        directories=["src", "src/app"],
        files_by_extension={
            ".tsx": ["src/app/page.tsx"],
            ".json": ["package.json"]
        },
        total_files=2,
        total_directories=2
    )
    
    configurations = ConfigurationFiles(
        docker_compose=None,
        package_json={
            "dependencies": {
                "react": "^19.0.0",
                "next": "^14.0.0"
            }
        },
        requirements_txt=None
    )
    
    documentation = Documentation(
        readme="# Minimal Frontend",
        architecture_docs={},
        other_docs={}
    )
    
    system_info = SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation=documentation,
        services=[],
        technologies={"frontend": ["React", "Next.js"]}
    )
    
    analyzer = LayerAnalyzer(system_info)
    result = analyzer.analyze_frontend_layer()
    
    # Should have missing capabilities
    assert len(result.missing_capabilities) > 0
    
    # WebSocket should be missing
    ws_missing = [cap for cap in result.missing_capabilities if cap.name == "WebSocket Connectivity"]
    assert len(ws_missing) > 0
    
    # PWA features should be missing
    pwa_missing = [cap for cap in result.missing_capabilities if "PWA" in cap.name or "Service Worker" in cap.name]
    assert len(pwa_missing) > 0


def test_extract_frontend_artifacts(frontend_analyzer):
    """Test extraction of Frontend-specific artifacts."""
    artifacts = frontend_analyzer._extract_frontend_artifacts()
    
    assert 'package_json' in artifacts
    assert 'dependencies' in artifacts
    assert 'has_app_dir' in artifacts
    assert 'has_components_dir' in artifacts
    assert 'has_manifest' in artifacts
    assert 'has_service_worker' in artifacts
    
    # Check specific values
    assert artifacts['has_app_dir'] is True
    assert artifacts['has_components_dir'] is True
    assert artifacts['has_manifest'] is True
    assert artifacts['has_service_worker'] is True
    assert 'react' in artifacts['dependencies']
    assert 'next' in artifacts['dependencies']


def test_verify_react_present(frontend_analyzer):
    """Test React verification when present."""
    artifacts = {
        'dependencies': {'react': '^19.0.0'}
    }
    
    result = frontend_analyzer._verify_react(artifacts)
    
    assert result['status'] == 'implemented'
    assert 'React' in result['strength']


def test_verify_react_missing(frontend_analyzer):
    """Test React verification when missing."""
    artifacts = {
        'dependencies': {}
    }
    
    result = frontend_analyzer._verify_react(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_nextjs_with_app_router(frontend_analyzer):
    """Test Next.js verification with app router."""
    artifacts = {
        'dependencies': {'next': '^14.0.0'},
        'has_app_dir': True,
        'has_pages_dir': False
    }
    
    result = frontend_analyzer._verify_nextjs(artifacts)
    
    assert result['status'] == 'implemented'
    assert 'App router' in result['strength']


def test_verify_nextjs_with_pages_router(frontend_analyzer):
    """Test Next.js verification with pages router."""
    artifacts = {
        'dependencies': {'next': '^14.0.0'},
        'has_app_dir': False,
        'has_pages_dir': True
    }
    
    result = frontend_analyzer._verify_nextjs(artifacts)
    
    assert result['status'] == 'implemented'
    assert 'Pages router' in result['strength']


def test_verify_nextjs_partial(frontend_analyzer):
    """Test Next.js verification when partially implemented."""
    artifacts = {
        'dependencies': {'next': '^14.0.0'},
        'has_app_dir': False,
        'has_pages_dir': False
    }
    
    result = frontend_analyzer._verify_nextjs(artifacts)
    
    assert result['status'] == 'partial'
    assert len(result['missing_aspects']) > 0


def test_verify_websocket_present(frontend_analyzer):
    """Test WebSocket verification when present."""
    artifacts = {
        'dependencies': {'socket.io-client': '^4.5.0'}
    }
    
    result = frontend_analyzer._verify_websocket(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_websocket_missing(frontend_analyzer):
    """Test WebSocket verification when missing."""
    artifacts = {
        'dependencies': {}
    }
    
    result = frontend_analyzer._verify_websocket(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_ui_components_complete(frontend_analyzer):
    """Test UI components verification when complete."""
    artifacts = {
        'has_components_dir': True,
        'frontend_files': ['Button.tsx', 'Header.tsx', 'Footer.tsx']
    }
    
    result = frontend_analyzer._verify_ui_components(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_ui_components_partial(frontend_analyzer):
    """Test UI components verification when partial."""
    artifacts = {
        'has_components_dir': True,
        'frontend_files': []
    }
    
    result = frontend_analyzer._verify_ui_components(artifacts)
    
    assert result['status'] == 'partial'


def test_verify_state_management_redux(frontend_analyzer):
    """Test state management verification with Redux."""
    artifacts = {
        'dependencies': {'@reduxjs/toolkit': '^1.9.0'}
    }
    
    result = frontend_analyzer._verify_state_management(artifacts)
    
    assert result['status'] == 'implemented'
    assert 'reduxjs' in result['strength'].lower()


def test_verify_state_management_missing(frontend_analyzer):
    """Test state management verification when missing."""
    artifacts = {
        'dependencies': {}
    }
    
    result = frontend_analyzer._verify_state_management(artifacts)
    
    assert result['status'] == 'missing'


# Backend API Layer Analysis Tests

@pytest.fixture
def backend_system_info():
    """Create a SystemInfo with Backend API-specific data."""
    project_structure = ProjectStructure(
        root_path=Path("/test/backend-project"),
        directories=[
            "src",
            "src/api",
            "src/api/v1",
            "src/api/v1/routers",
            "src/auth",
            "src/middleware",
            "src/models",
            "tests"
        ],
        files_by_extension={
            ".py": [
                "src/main.py",
                "src/api/v1/routers/users.py",
                "src/api/v1/routers/items.py",
                "src/auth/jwt_handler.py",
                "src/auth/auth_middleware.py",
                "src/middleware/error_handler.py",
                "src/models/user.py",
                "tests/test_main.py"
            ]
        },
        total_files=8,
        total_directories=8
    )
    
    configurations = ConfigurationFiles(
        docker_compose={
            "services": {
                "api": {"image": "python:3.11"},
                "postgres": {"image": "postgres:16"},
                "redis": {"image": "redis:7.2"}
            }
        },
        package_json=None,
        requirements_txt=[
            "fastapi==0.104.0",
            "uvicorn==0.24.0",
            "pyjwt==2.8.0",
            "sqlalchemy==2.0.23",
            "asyncpg==0.29.0",
            "redis==5.0.1",
            "pydantic==2.5.0"
        ]
    )
    
    documentation = Documentation(
        readme="# Backend API\nBuilt with FastAPI and PostgreSQL.",
        architecture_docs={},
        other_docs={}
    )
    
    return SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation=documentation,
        services=["api", "postgres", "redis"],
        technologies={
            "frontend": [],
            "backend": ["FastAPI"],
            "database": ["PostgreSQL", "Redis"],
            "infrastructure": ["Docker Compose"],
            "testing": ["pytest"]
        }
    )


@pytest.fixture
def backend_analyzer(backend_system_info):
    """Create a LayerAnalyzer for Backend API testing."""
    return LayerAnalyzer(backend_system_info)


def test_analyze_backend_api_layer_complete(backend_analyzer):
    """Test Backend API layer analysis with complete implementation."""
    result = backend_analyzer.analyze_backend_api_layer()
    
    assert isinstance(result, LayerAnalysisResult)
    assert result.layer_name == "Backend API"
    assert 0.0 <= result.completeness_score <= 1.0
    assert len(result.capabilities_assessed) == 8  # All Backend API capabilities
    assert isinstance(result.timestamp, datetime)


def test_analyze_backend_api_layer_has_fastapi(backend_analyzer):
    """Test that Backend API analysis detects FastAPI."""
    result = backend_analyzer.analyze_backend_api_layer()
    
    # Check if FastAPI capability is implemented
    fastapi_caps = [cap for cap in result.implemented_capabilities if cap.name == "FastAPI Framework"]
    assert len(fastapi_caps) > 0


def test_analyze_backend_api_layer_has_endpoints(backend_analyzer):
    """Test that Backend API analysis detects API endpoints."""
    result = backend_analyzer.analyze_backend_api_layer()
    
    # Check if API Endpoints capability is implemented
    endpoint_caps = [cap for cap in result.implemented_capabilities if cap.name == "API Endpoints"]
    assert len(endpoint_caps) > 0


def test_analyze_backend_api_layer_has_jwt(backend_analyzer):
    """Test that Backend API analysis detects JWT authentication."""
    result = backend_analyzer.analyze_backend_api_layer()
    
    # Check if JWT Authentication capability is implemented
    jwt_caps = [cap for cap in result.implemented_capabilities if cap.name == "JWT Authentication"]
    assert len(jwt_caps) > 0


def test_analyze_backend_api_layer_has_scaling(backend_analyzer):
    """Test that Backend API analysis detects horizontal scaling readiness."""
    result = backend_analyzer.analyze_backend_api_layer()
    
    # Check if Horizontal Scaling capability is implemented
    scaling_caps = [cap for cap in result.implemented_capabilities if cap.name == "Horizontal Scaling"]
    assert len(scaling_caps) > 0


def test_analyze_backend_api_layer_has_versioning(backend_analyzer):
    """Test that Backend API analysis detects API versioning."""
    result = backend_analyzer.analyze_backend_api_layer()
    
    # Check if API Versioning capability is implemented or partial
    versioning_caps = [cap for cap in result.implemented_capabilities if cap.name == "API Versioning"]
    versioning_partial = [cap for cap in result.partial_capabilities if cap.capability.name == "API Versioning"]
    assert len(versioning_caps) > 0 or len(versioning_partial) > 0


def test_analyze_backend_api_layer_has_validation(backend_analyzer):
    """Test that Backend API analysis detects request validation."""
    result = backend_analyzer.analyze_backend_api_layer()
    
    # Check if Request Validation capability is implemented
    validation_caps = [cap for cap in result.implemented_capabilities if cap.name == "Request Validation"]
    assert len(validation_caps) > 0


def test_analyze_backend_api_layer_has_error_handling(backend_analyzer):
    """Test that Backend API analysis detects error handling."""
    result = backend_analyzer.analyze_backend_api_layer()
    
    # Check if Error Handling capability is implemented or partial
    error_caps = [cap for cap in result.implemented_capabilities if cap.name == "Error Handling"]
    error_partial = [cap for cap in result.partial_capabilities if cap.capability.name == "Error Handling"]
    assert len(error_caps) > 0 or len(error_partial) > 0


def test_analyze_backend_api_layer_has_cors(backend_analyzer):
    """Test that Backend API analysis detects CORS configuration."""
    result = backend_analyzer.analyze_backend_api_layer()
    
    # Check if CORS Configuration capability is implemented
    cors_caps = [cap for cap in result.implemented_capabilities if cap.name == "CORS Configuration"]
    assert len(cors_caps) > 0


def test_analyze_backend_api_layer_missing_features():
    """Test Backend API layer analysis with missing features."""
    # Create minimal system info without JWT and versioning
    project_structure = ProjectStructure(
        root_path=Path("/test/minimal-backend"),
        directories=["src"],
        files_by_extension={
            ".py": ["src/main.py"]
        },
        total_files=1,
        total_directories=1
    )
    
    configurations = ConfigurationFiles(
        docker_compose=None,
        package_json=None,
        requirements_txt=["fastapi==0.104.0"]
    )
    
    documentation = Documentation(
        readme="# Minimal Backend",
        architecture_docs={},
        other_docs={}
    )
    
    system_info = SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation=documentation,
        services=[],
        technologies={"backend": ["FastAPI"]}
    )
    
    analyzer = LayerAnalyzer(system_info)
    result = analyzer.analyze_backend_api_layer()
    
    # Should have missing capabilities
    assert len(result.missing_capabilities) > 0
    
    # JWT should be missing
    jwt_missing = [cap for cap in result.missing_capabilities if cap.name == "JWT Authentication"]
    assert len(jwt_missing) > 0


def test_extract_backend_api_artifacts(backend_analyzer):
    """Test extraction of Backend API-specific artifacts."""
    artifacts = backend_analyzer._extract_backend_api_artifacts()
    
    assert 'requirements_txt' in artifacts
    assert 'dependencies' in artifacts
    assert 'has_main_py' in artifacts
    assert 'has_routers_dir' in artifacts
    assert 'has_auth_files' in artifacts
    assert 'python_files' in artifacts
    
    # Check specific values
    assert artifacts['has_main_py'] is True
    assert artifacts['has_routers_dir'] is True
    assert artifacts['has_auth_files'] is True
    assert len(artifacts['auth_files']) > 0
    assert len(artifacts['router_files']) > 0


def test_verify_fastapi_present(backend_analyzer):
    """Test FastAPI verification when present."""
    artifacts = {
        'dependencies': ['fastapi==0.104.0'],
        'has_main_py': True
    }
    
    result = backend_analyzer._verify_fastapi(artifacts)
    
    assert result['status'] == 'implemented'
    assert 'FastAPI' in result['strength']


def test_verify_fastapi_partial(backend_analyzer):
    """Test FastAPI verification when partially implemented."""
    artifacts = {
        'dependencies': ['fastapi==0.104.0'],
        'has_main_py': False
    }
    
    result = backend_analyzer._verify_fastapi(artifacts)
    
    assert result['status'] == 'partial'


def test_verify_fastapi_missing(backend_analyzer):
    """Test FastAPI verification when missing."""
    artifacts = {
        'dependencies': [],
        'has_main_py': False
    }
    
    result = backend_analyzer._verify_fastapi(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_api_endpoints_complete(backend_analyzer):
    """Test API endpoints verification when complete."""
    artifacts = {
        'has_main_py': True,
        'has_routers_dir': True,
        'router_files': ['routers/users.py', 'routers/items.py'],
        'api_files': ['api/v1/endpoints.py']
    }
    
    result = backend_analyzer._verify_api_endpoints(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_api_endpoints_partial(backend_analyzer):
    """Test API endpoints verification when partial."""
    artifacts = {
        'has_main_py': True,
        'has_routers_dir': False,
        'router_files': [],
        'api_files': []
    }
    
    result = backend_analyzer._verify_api_endpoints(artifacts)
    
    assert result['status'] == 'partial'


def test_verify_api_endpoints_missing(backend_analyzer):
    """Test API endpoints verification when missing."""
    artifacts = {
        'has_main_py': False,
        'has_routers_dir': False,
        'router_files': [],
        'api_files': []
    }
    
    result = backend_analyzer._verify_api_endpoints(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_jwt_auth_complete(backend_analyzer):
    """Test JWT authentication verification when complete."""
    artifacts = {
        'dependencies': ['pyjwt==2.8.0', 'python-jose==3.3.0'],
        'auth_files': ['auth/jwt_handler.py', 'auth/middleware.py']
    }
    
    result = backend_analyzer._verify_jwt_auth(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_jwt_auth_partial(backend_analyzer):
    """Test JWT authentication verification when partial."""
    artifacts = {
        'dependencies': ['pyjwt==2.8.0'],
        'auth_files': []
    }
    
    result = backend_analyzer._verify_jwt_auth(artifacts)
    
    assert result['status'] == 'partial'


def test_verify_jwt_auth_missing(backend_analyzer):
    """Test JWT authentication verification when missing."""
    artifacts = {
        'dependencies': [],
        'auth_files': []
    }
    
    result = backend_analyzer._verify_jwt_auth(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_horizontal_scaling_complete(backend_analyzer):
    """Test horizontal scaling verification when complete."""
    artifacts = {
        'dependencies': ['sqlalchemy==2.0.23', 'asyncpg==0.29.0', 'redis==5.0.1'],
        'python_files': ['models/user.py'],
        'has_models_dir': True
    }
    
    result = backend_analyzer._verify_horizontal_scaling(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_horizontal_scaling_partial(backend_analyzer):
    """Test horizontal scaling verification when partial."""
    artifacts = {
        'dependencies': ['fastapi==0.104.0'],
        'python_files': [],
        'has_models_dir': False
    }
    
    result = backend_analyzer._verify_horizontal_scaling(artifacts)
    
    assert result['status'] == 'partial'


def test_verify_horizontal_scaling_missing(backend_analyzer):
    """Test horizontal scaling verification when missing."""
    artifacts = {
        'dependencies': [],
        'python_files': [],
        'has_models_dir': False
    }
    
    result = backend_analyzer._verify_horizontal_scaling(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_api_versioning_complete(backend_analyzer):
    """Test API versioning verification when complete."""
    artifacts = {
        'api_files': ['api/v1/endpoints.py', 'api/v1/routers/users.py'],
        'router_files': ['api/v1/routers/items.py'],
        'python_files': ['api/v1/main.py'],
        'has_api_dir': True
    }
    
    result = backend_analyzer._verify_api_versioning(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_api_versioning_partial(backend_analyzer):
    """Test API versioning verification when partial."""
    artifacts = {
        'api_files': ['api/endpoints.py'],
        'router_files': [],
        'python_files': [],
        'has_api_dir': True
    }
    
    result = backend_analyzer._verify_api_versioning(artifacts)
    
    assert result['status'] == 'partial'


def test_verify_api_versioning_missing(backend_analyzer):
    """Test API versioning verification when missing."""
    artifacts = {
        'api_files': [],
        'router_files': [],
        'python_files': [],
        'has_api_dir': False
    }
    
    result = backend_analyzer._verify_api_versioning(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_request_validation_complete(backend_analyzer):
    """Test request validation verification when complete."""
    artifacts = {
        'dependencies': ['pydantic==2.5.0', 'fastapi==0.104.0'],
        'has_models_dir': True
    }
    
    result = backend_analyzer._verify_request_validation(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_request_validation_missing(backend_analyzer):
    """Test request validation verification when missing."""
    artifacts = {
        'dependencies': [],
        'has_models_dir': False
    }
    
    result = backend_analyzer._verify_request_validation(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_error_handling_complete(backend_analyzer):
    """Test error handling verification when complete."""
    artifacts = {
        'has_middleware_dir': True,
        'python_files': ['middleware/error_handler.py', 'middleware/exception_handler.py']
    }
    
    result = backend_analyzer._verify_error_handling(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_error_handling_partial(backend_analyzer):
    """Test error handling verification when partial."""
    artifacts = {
        'has_middleware_dir': False,
        'python_files': []
    }
    
    result = backend_analyzer._verify_error_handling(artifacts)
    
    assert result['status'] == 'partial'


def test_verify_cors_complete(backend_analyzer):
    """Test CORS verification when complete."""
    artifacts = {
        'dependencies': ['fastapi==0.104.0'],
        'has_main_py': True
    }
    
    result = backend_analyzer._verify_cors(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_cors_partial(backend_analyzer):
    """Test CORS verification when partial."""
    artifacts = {
        'dependencies': ['fastapi==0.104.0'],
        'has_main_py': False
    }
    
    result = backend_analyzer._verify_cors(artifacts)
    
    assert result['status'] == 'partial'


def test_verify_cors_missing(backend_analyzer):
    """Test CORS verification when missing."""
    artifacts = {
        'dependencies': [],
        'has_main_py': False
    }
    
    result = backend_analyzer._verify_cors(artifacts)
    
    assert result['status'] == 'missing'



# Data Persistence Layer Tests

@pytest.fixture
def data_persistence_system_info():
    """Create a sample SystemInfo for Data Persistence layer testing."""
    from ..system_inspector import SystemInfo, ProjectStructure, ConfigurationFiles
    
    project_structure = ProjectStructure(
        root_path=Path("/test/project"),
        directories=[
            "backend/db",
            "backend/models",
            "backend/migrations",
            "backend/alembic"
        ],
        files_by_extension={
            '.py': [
                'backend/db/neo4j_db.py',
                'backend/db/postgres_db.py',
                'backend/db/redis_db.py',
                'backend/models/user.py',
                'backend/models/project.py',
                'backend/migrations/env.py',
                'backend/alembic/versions/001_initial.py'
            ]
        },
        total_files=7,
        total_directories=4
    )
    
    configurations = ConfigurationFiles(
        package_json=None,
        requirements_txt=[
            'neo4j==5.15.0',
            'psycopg2-binary==2.9.9',
            'sqlalchemy==2.0.23',
            'redis==5.0.1',
            'alembic==1.13.0'
        ],
        docker_compose={
            'version': '3.8',
            'services': {
                'neo4j': {
                    'image': 'neo4j:5.15',
                    'ports': ['7474:7474', '7687:7687']
                },
                'postgres': {
                    'image': 'postgres:16',
                    'ports': ['5432:5432']
                },
                'redis': {
                    'image': 'redis:7.2',
                    'ports': ['6379:6379']
                }
            }
        }
    )
    
    return SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation={}
    )


@pytest.fixture
def data_persistence_analyzer(data_persistence_system_info):
    """Create a LayerAnalyzer for Data Persistence testing."""
    return LayerAnalyzer(data_persistence_system_info)


def test_analyze_data_persistence_layer_complete(data_persistence_analyzer):
    """Test analyzing a complete Data Persistence layer."""
    result = data_persistence_analyzer.analyze_data_persistence_layer()
    
    assert result.layer_name == "Data Persistence"
    assert result.completeness_score > 0.5
    assert len(result.capabilities_assessed) == 8


def test_analyze_data_persistence_layer_has_neo4j(data_persistence_analyzer):
    """Test that Neo4j capability is detected."""
    result = data_persistence_analyzer.analyze_data_persistence_layer()
    
    neo4j_caps = [cap for cap in result.implemented_capabilities if 'Neo4j' in cap.name]
    assert len(neo4j_caps) > 0


def test_analyze_data_persistence_layer_has_postgresql(data_persistence_analyzer):
    """Test that PostgreSQL capability is detected."""
    result = data_persistence_analyzer.analyze_data_persistence_layer()
    
    postgres_caps = [cap for cap in result.implemented_capabilities if 'PostgreSQL' in cap.name]
    assert len(postgres_caps) > 0


def test_analyze_data_persistence_layer_has_redis(data_persistence_analyzer):
    """Test that Redis capability is detected."""
    result = data_persistence_analyzer.analyze_data_persistence_layer()
    
    redis_caps = [cap for cap in result.implemented_capabilities if 'Redis' in cap.name]
    assert len(redis_caps) > 0


def test_analyze_data_persistence_layer_has_migrations(data_persistence_analyzer):
    """Test that database migrations capability is detected."""
    result = data_persistence_analyzer.analyze_data_persistence_layer()
    
    migration_caps = [cap for cap in result.implemented_capabilities if 'Migration' in cap.name]
    assert len(migration_caps) > 0


def test_analyze_data_persistence_layer_has_orm_models(data_persistence_analyzer):
    """Test that ORM models capability is detected."""
    result = data_persistence_analyzer.analyze_data_persistence_layer()
    
    orm_caps = [cap for cap in result.implemented_capabilities if 'ORM' in cap.name]
    assert len(orm_caps) > 0


def test_analyze_data_persistence_layer_missing_features():
    """Test analyzing a Data Persistence layer with missing features."""
    from ..system_inspector import SystemInfo, ProjectStructure, ConfigurationFiles
    
    # Create minimal system info with no data persistence features
    project_structure = ProjectStructure(
        root_path=Path("/test/project"),
        directories=["backend"],
        files_by_extension={'.py': ['backend/main.py']},
        total_files=1,
        total_directories=1
    )
    
    configurations = ConfigurationFiles(
        package_json=None,
        requirements_txt=['fastapi==0.104.1'],
        docker_compose=None
    )
    
    system_info = SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation={}
    )
    
    analyzer = LayerAnalyzer(system_info)
    result = analyzer.analyze_data_persistence_layer()
    
    assert result.layer_name == "Data Persistence"
    assert result.completeness_score < 0.5
    assert len(result.missing_capabilities) > 0 or len(result.partial_capabilities) > 0
    assert len(result.gaps) > 0


def test_extract_data_persistence_artifacts(data_persistence_analyzer):
    """Test extracting Data Persistence artifacts."""
    artifacts = data_persistence_analyzer._extract_data_persistence_artifacts()
    
    assert artifacts['has_neo4j_files'] is True
    assert artifacts['has_postgres_files'] is True
    assert artifacts['has_redis_files'] is True
    assert artifacts['has_models_dir'] is True
    assert artifacts['has_migrations_dir'] is True
    assert len(artifacts['neo4j_files']) > 0
    assert len(artifacts['postgres_files']) > 0
    assert len(artifacts['redis_files']) > 0
    assert len(artifacts['model_files']) > 0
    assert len(artifacts['migration_files']) > 0


def test_verify_neo4j_complete(data_persistence_analyzer):
    """Test verifying complete Neo4j implementation."""
    artifacts = data_persistence_analyzer._extract_data_persistence_artifacts()
    result = data_persistence_analyzer._verify_neo4j(artifacts)
    
    assert result['status'] == 'implemented'
    assert 'strength' in result
    assert len(result['evidence']) > 0


def test_verify_neo4j_missing(data_persistence_analyzer):
    """Test verifying missing Neo4j implementation."""
    artifacts = {
        'dependencies': [],
        'neo4j_files': [],
        'docker_compose': None
    }
    result = data_persistence_analyzer._verify_neo4j(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_postgresql_complete(data_persistence_analyzer):
    """Test verifying complete PostgreSQL implementation."""
    artifacts = data_persistence_analyzer._extract_data_persistence_artifacts()
    result = data_persistence_analyzer._verify_postgresql(artifacts)
    
    assert result['status'] == 'implemented'
    assert 'strength' in result
    assert len(result['evidence']) > 0


def test_verify_postgresql_partial(data_persistence_analyzer):
    """Test verifying partial PostgreSQL implementation."""
    artifacts = {
        'dependencies': ['psycopg2-binary==2.9.9'],
        'postgres_files': [],
        'model_files': [],
        'docker_compose': None
    }
    result = data_persistence_analyzer._verify_postgresql(artifacts)
    
    assert result['status'] == 'partial'
    assert 'implemented_aspects' in result
    assert 'missing_aspects' in result


def test_verify_postgresql_missing(data_persistence_analyzer):
    """Test verifying missing PostgreSQL implementation."""
    artifacts = {
        'dependencies': [],
        'postgres_files': [],
        'model_files': [],
        'docker_compose': None
    }
    result = data_persistence_analyzer._verify_postgresql(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_redis_complete(data_persistence_analyzer):
    """Test verifying complete Redis implementation."""
    artifacts = data_persistence_analyzer._extract_data_persistence_artifacts()
    result = data_persistence_analyzer._verify_redis(artifacts)
    
    assert result['status'] == 'implemented'
    assert 'strength' in result
    assert len(result['evidence']) > 0


def test_verify_redis_partial(data_persistence_analyzer):
    """Test verifying partial Redis implementation."""
    artifacts = {
        'dependencies': ['redis==5.0.1'],
        'redis_files': [],
        'docker_compose': None
    }
    result = data_persistence_analyzer._verify_redis(artifacts)
    
    assert result['status'] == 'partial'
    assert 'implemented_aspects' in result
    assert 'missing_aspects' in result


def test_verify_redis_missing(data_persistence_analyzer):
    """Test verifying missing Redis implementation."""
    artifacts = {
        'dependencies': [],
        'redis_files': [],
        'docker_compose': None
    }
    result = data_persistence_analyzer._verify_redis(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_migrations_complete(data_persistence_analyzer):
    """Test verifying complete migration system."""
    artifacts = data_persistence_analyzer._extract_data_persistence_artifacts()
    result = data_persistence_analyzer._verify_migrations(artifacts)
    
    assert result['status'] == 'implemented'
    assert 'strength' in result
    assert len(result['evidence']) > 0


def test_verify_migrations_partial(data_persistence_analyzer):
    """Test verifying partial migration system."""
    artifacts = {
        'dependencies': ['alembic==1.13.0'],
        'has_migrations_dir': False,
        'migration_files': []
    }
    result = data_persistence_analyzer._verify_migrations(artifacts)
    
    assert result['status'] == 'partial'
    assert 'implemented_aspects' in result
    assert 'missing_aspects' in result


def test_verify_migrations_missing(data_persistence_analyzer):
    """Test verifying missing migration system."""
    artifacts = {
        'dependencies': [],
        'has_migrations_dir': False,
        'migration_files': []
    }
    result = data_persistence_analyzer._verify_migrations(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_data_consistency_complete(data_persistence_analyzer):
    """Test verifying data consistency mechanisms."""
    artifacts = data_persistence_analyzer._extract_data_persistence_artifacts()
    result = data_persistence_analyzer._verify_data_consistency(artifacts)
    
    assert result['status'] in ['implemented', 'partial']
    assert len(result['evidence']) >= 0


def test_verify_connection_pooling_complete(data_persistence_analyzer):
    """Test verifying connection pooling."""
    artifacts = data_persistence_analyzer._extract_data_persistence_artifacts()
    result = data_persistence_analyzer._verify_connection_pooling(artifacts)
    
    assert result['status'] in ['implemented', 'partial']


def test_verify_orm_models_complete(data_persistence_analyzer):
    """Test verifying complete ORM models."""
    artifacts = data_persistence_analyzer._extract_data_persistence_artifacts()
    result = data_persistence_analyzer._verify_orm_models(artifacts)
    
    assert result['status'] == 'implemented'
    assert 'strength' in result
    assert len(result['evidence']) > 0


def test_verify_orm_models_partial(data_persistence_analyzer):
    """Test verifying partial ORM models."""
    artifacts = {
        'dependencies': ['sqlalchemy==2.0.23'],
        'model_files': [],
        'has_models_dir': False
    }
    result = data_persistence_analyzer._verify_orm_models(artifacts)
    
    assert result['status'] == 'partial'
    assert 'implemented_aspects' in result
    assert 'missing_aspects' in result


def test_verify_orm_models_missing(data_persistence_analyzer):
    """Test verifying missing ORM models."""
    artifacts = {
        'dependencies': [],
        'model_files': [],
        'has_models_dir': False
    }
    result = data_persistence_analyzer._verify_orm_models(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_query_optimization_partial(data_persistence_analyzer):
    """Test verifying query optimization (always partial without deep analysis)."""
    artifacts = data_persistence_analyzer._extract_data_persistence_artifacts()
    result = data_persistence_analyzer._verify_query_optimization(artifacts)
    
    assert result['status'] in ['partial', 'missing']


# AI Reasoning Layer Analysis Tests

@pytest.fixture
def ai_reasoning_system_info():
    """Create a SystemInfo with AI Reasoning Layer-specific data."""
    project_structure = ProjectStructure(
        root_path=Path("/test/ai-project"),
        directories=[
            "src",
            "src/llm",
            "src/llm/providers",
            "src/prompts",
            "tests"
        ],
        files_by_extension={
            ".py": [
                "src/llm/llm_service.py",
                "src/llm/providers/openai_provider.py",
                "src/llm/providers/anthropic_provider.py",
                "src/llm/providers/ollama_provider.py",
                "src/llm/retry_handler.py",
                "src/llm/circuit_breaker.py",
                "src/prompts/prompt_templates.py",
                "src/prompts/context_manager.py",
                "src/llm/response_parser.py",
                "src/llm/response_validator.py",
                "tests/test_llm.py"
            ]
        },
        total_files=11,
        total_directories=5
    )
    
    configurations = ConfigurationFiles(
        docker_compose={
            "services": {
                "llm-service": {"image": "python:3.11"}
            }
        },
        package_json=None,
        requirements_txt=[
            "openai==1.3.0",
            "anthropic==0.7.0",
            "tenacity==8.2.3",
            "pydantic==2.5.0"
        ]
    )
    
    documentation = Documentation(
        readme="# AI Reasoning Service\nMulti-LLM integration with OpenAI, Anthropic, and Ollama.",
        architecture_docs={},
        other_docs={}
    )
    
    return SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation=documentation,
        services=["llm-service"],
        technologies={
            "frontend": [],
            "backend": ["OpenAI", "Anthropic"],
            "database": [],
            "infrastructure": ["Docker Compose"],
            "testing": ["pytest"]
        }
    )


@pytest.fixture
def ai_reasoning_analyzer(ai_reasoning_system_info):
    """Create a LayerAnalyzer for AI Reasoning testing."""
    return LayerAnalyzer(ai_reasoning_system_info)


def test_analyze_ai_reasoning_layer_complete(ai_reasoning_analyzer):
    """Test AI Reasoning layer analysis with complete implementation."""
    result = ai_reasoning_analyzer.analyze_ai_reasoning_layer()
    
    assert isinstance(result, LayerAnalysisResult)
    assert result.layer_name == "AI Reasoning"
    assert 0.0 <= result.completeness_score <= 1.0
    assert len(result.capabilities_assessed) == 13  # All AI Reasoning capabilities
    assert isinstance(result.timestamp, datetime)


def test_analyze_ai_reasoning_layer_has_multi_llm(ai_reasoning_analyzer):
    """Test that AI Reasoning analysis detects multi-LLM integration."""
    result = ai_reasoning_analyzer.analyze_ai_reasoning_layer()
    
    # Check if Multi-LLM Integration capability is implemented
    multi_llm_caps = [cap for cap in result.implemented_capabilities if cap.name == "Multi-LLM Integration"]
    assert len(multi_llm_caps) > 0


def test_analyze_ai_reasoning_layer_has_openai(ai_reasoning_analyzer):
    """Test that AI Reasoning analysis detects OpenAI integration."""
    result = ai_reasoning_analyzer.analyze_ai_reasoning_layer()
    
    # Check if OpenAI Integration capability is implemented
    openai_caps = [cap for cap in result.implemented_capabilities if cap.name == "OpenAI Integration"]
    assert len(openai_caps) > 0


def test_analyze_ai_reasoning_layer_has_anthropic(ai_reasoning_analyzer):
    """Test that AI Reasoning analysis detects Anthropic integration."""
    result = ai_reasoning_analyzer.analyze_ai_reasoning_layer()
    
    # Check if Anthropic Integration capability is implemented
    anthropic_caps = [cap for cap in result.implemented_capabilities if cap.name == "Anthropic Integration"]
    assert len(anthropic_caps) > 0


def test_analyze_ai_reasoning_layer_has_ollama(ai_reasoning_analyzer):
    """Test that AI Reasoning analysis detects Ollama integration."""
    result = ai_reasoning_analyzer.analyze_ai_reasoning_layer()
    
    # Check if Ollama Integration capability is implemented
    ollama_caps = [cap for cap in result.implemented_capabilities if cap.name == "Ollama Integration"]
    assert len(ollama_caps) > 0


def test_analyze_ai_reasoning_layer_has_circuit_breaker(ai_reasoning_analyzer):
    """Test that AI Reasoning analysis detects circuit breaker."""
    result = ai_reasoning_analyzer.analyze_ai_reasoning_layer()
    
    # Check if Circuit Breaker capability is implemented
    cb_caps = [cap for cap in result.implemented_capabilities if cap.name == "Circuit Breaker"]
    # Also check partial capabilities in case it's detected but not fully verified
    cb_partial = [cap for cap in result.partial_capabilities if cap.capability.name == "Circuit Breaker"]
    assert len(cb_caps) > 0 or len(cb_partial) > 0


def test_analyze_ai_reasoning_layer_has_retry_logic(ai_reasoning_analyzer):
    """Test that AI Reasoning analysis detects retry logic."""
    result = ai_reasoning_analyzer.analyze_ai_reasoning_layer()
    
    # Check if Retry Logic capability is implemented
    retry_caps = [cap for cap in result.implemented_capabilities if cap.name == "Retry Logic"]
    # Also check partial capabilities in case it's detected but not fully verified
    retry_partial = [cap for cap in result.partial_capabilities if cap.capability.name == "Retry Logic"]
    assert len(retry_caps) > 0 or len(retry_partial) > 0


def test_analyze_ai_reasoning_layer_has_prompt_templates(ai_reasoning_analyzer):
    """Test that AI Reasoning analysis detects prompt templates."""
    result = ai_reasoning_analyzer.analyze_ai_reasoning_layer()
    
    # Check if Prompt Templates capability is implemented
    template_caps = [cap for cap in result.implemented_capabilities if cap.name == "Prompt Templates"]
    assert len(template_caps) > 0


def test_analyze_ai_reasoning_layer_has_context_management(ai_reasoning_analyzer):
    """Test that AI Reasoning analysis detects context management."""
    result = ai_reasoning_analyzer.analyze_ai_reasoning_layer()
    
    # Check if Context Management capability is implemented or partial
    context_caps = [cap for cap in result.implemented_capabilities if cap.name == "Context Management"]
    context_partial = [cap for cap in result.partial_capabilities if cap.capability.name == "Context Management"]
    assert len(context_caps) > 0 or len(context_partial) > 0


def test_analyze_ai_reasoning_layer_has_response_parsing(ai_reasoning_analyzer):
    """Test that AI Reasoning analysis detects response parsing."""
    result = ai_reasoning_analyzer.analyze_ai_reasoning_layer()
    
    # Check if Response Parsing capability is implemented or partial
    parsing_caps = [cap for cap in result.implemented_capabilities if cap.name == "Response Parsing"]
    parsing_partial = [cap for cap in result.partial_capabilities if cap.capability.name == "Response Parsing"]
    assert len(parsing_caps) > 0 or len(parsing_partial) > 0


def test_analyze_ai_reasoning_layer_has_response_validation(ai_reasoning_analyzer):
    """Test that AI Reasoning analysis detects response validation."""
    result = ai_reasoning_analyzer.analyze_ai_reasoning_layer()
    
    # Check if Response Validation capability is implemented or partial
    validation_caps = [cap for cap in result.implemented_capabilities if cap.name == "Response Validation"]
    validation_partial = [cap for cap in result.partial_capabilities if cap.capability.name == "Response Validation"]
    assert len(validation_caps) > 0 or len(validation_partial) > 0


def test_analyze_ai_reasoning_layer_missing_features():
    """Test AI Reasoning layer analysis with missing features."""
    # Create minimal system info without fallback mechanisms
    project_structure = ProjectStructure(
        root_path=Path("/test/minimal-ai"),
        directories=["src"],
        files_by_extension={
            ".py": ["src/llm_service.py"]
        },
        total_files=1,
        total_directories=1
    )
    
    configurations = ConfigurationFiles(
        docker_compose=None,
        package_json=None,
        requirements_txt=["openai==1.3.0"]
    )
    
    documentation = Documentation(
        readme="# Minimal AI Service",
        architecture_docs={},
        other_docs={}
    )
    
    system_info = SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation=documentation,
        services=[],
        technologies={"backend": ["OpenAI"]}
    )
    
    analyzer = LayerAnalyzer(system_info)
    result = analyzer.analyze_ai_reasoning_layer()
    
    # Should have missing capabilities
    assert len(result.missing_capabilities) > 0
    
    # Anthropic should be missing
    anthropic_missing = [cap for cap in result.missing_capabilities if cap.name == "Anthropic Integration"]
    assert len(anthropic_missing) > 0
    
    # Circuit breaker should be missing
    cb_missing = [cap for cap in result.missing_capabilities if cap.name == "Circuit Breaker"]
    assert len(cb_missing) > 0


def test_extract_ai_reasoning_artifacts(ai_reasoning_analyzer):
    """Test extraction of AI Reasoning-specific artifacts."""
    artifacts = ai_reasoning_analyzer._extract_ai_reasoning_artifacts()
    
    assert 'llm_files' in artifacts
    assert 'prompt_files' in artifacts
    assert 'env_files' in artifacts
    assert 'openai_installed' in artifacts
    assert 'anthropic_installed' in artifacts
    assert 'services' in artifacts
    
    # Check specific values
    assert len(artifacts['llm_files']) > 0
    assert len(artifacts['prompt_files']) > 0
    assert artifacts['openai_installed'] is True
    assert artifacts['anthropic_installed'] is True


def test_verify_multi_llm_complete(ai_reasoning_analyzer):
    """Test multi-LLM verification when complete."""
    artifacts = {
        'llm_files': ['llm_service.py', 'openai_provider.py', 'anthropic_provider.py'],
        'openai_installed': True,
        'anthropic_installed': True
    }
    
    result = ai_reasoning_analyzer._verify_multi_llm(artifacts)
    
    assert result['status'] == 'implemented'
    assert len(result['providers']) >= 2


def test_verify_multi_llm_partial(ai_reasoning_analyzer):
    """Test multi-LLM verification when partial."""
    artifacts = {
        'llm_files': ['llm_service.py'],
        'openai_installed': True,
        'anthropic_installed': False
    }
    
    result = ai_reasoning_analyzer._verify_multi_llm(artifacts)
    
    assert result['status'] == 'partial'


def test_verify_multi_llm_missing(ai_reasoning_analyzer):
    """Test multi-LLM verification when missing."""
    artifacts = {
        'llm_files': [],
        'openai_installed': False,
        'anthropic_installed': False
    }
    
    result = ai_reasoning_analyzer._verify_multi_llm(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_openai_present(ai_reasoning_analyzer):
    """Test OpenAI verification when present."""
    artifacts = {
        'openai_installed': True,
        'llm_files': ['openai_provider.py']
    }
    
    result = ai_reasoning_analyzer._verify_openai(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_openai_missing(ai_reasoning_analyzer):
    """Test OpenAI verification when missing."""
    artifacts = {
        'openai_installed': False,
        'llm_files': []
    }
    
    result = ai_reasoning_analyzer._verify_openai(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_anthropic_present(ai_reasoning_analyzer):
    """Test Anthropic verification when present."""
    artifacts = {
        'anthropic_installed': True,
        'llm_files': ['anthropic_provider.py']
    }
    
    result = ai_reasoning_analyzer._verify_anthropic(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_anthropic_missing(ai_reasoning_analyzer):
    """Test Anthropic verification when missing."""
    artifacts = {
        'anthropic_installed': False,
        'llm_files': []
    }
    
    result = ai_reasoning_analyzer._verify_anthropic(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_ollama_present(ai_reasoning_analyzer):
    """Test Ollama verification when present."""
    artifacts = {
        'llm_files': ['ollama_provider.py', 'llm_service.py']
    }
    
    result = ai_reasoning_analyzer._verify_ollama(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_ollama_missing(ai_reasoning_analyzer):
    """Test Ollama verification when missing."""
    artifacts = {
        'llm_files': ['openai_provider.py']
    }
    
    result = ai_reasoning_analyzer._verify_ollama(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_circuit_breaker_present(ai_reasoning_analyzer):
    """Test circuit breaker verification when present."""
    artifacts = {
        'llm_files': ['circuit_breaker.py', 'llm_service.py']
    }
    
    result = ai_reasoning_analyzer._verify_circuit_breaker(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_circuit_breaker_missing(ai_reasoning_analyzer):
    """Test circuit breaker verification when missing."""
    artifacts = {
        'llm_files': ['llm_service.py']
    }
    
    result = ai_reasoning_analyzer._verify_circuit_breaker(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_retry_logic_present(ai_reasoning_analyzer):
    """Test retry logic verification when present."""
    artifacts = {
        'llm_files': ['retry_handler.py', 'llm_service.py']
    }
    
    result = ai_reasoning_analyzer._verify_retry_logic(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_retry_logic_missing(ai_reasoning_analyzer):
    """Test retry logic verification when missing."""
    artifacts = {
        'llm_files': ['llm_service.py']
    }
    
    result = ai_reasoning_analyzer._verify_retry_logic(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_prompt_templates_present(ai_reasoning_analyzer):
    """Test prompt templates verification when present."""
    artifacts = {
        'prompt_files': ['prompt_templates.py', 'prompts.py']
    }
    
    result = ai_reasoning_analyzer._verify_prompt_templates(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_prompt_templates_missing(ai_reasoning_analyzer):
    """Test prompt templates verification when missing."""
    artifacts = {
        'prompt_files': []
    }
    
    result = ai_reasoning_analyzer._verify_prompt_templates(artifacts)
    
    assert result['status'] == 'missing'


def test_verify_context_management_present(ai_reasoning_analyzer):
    """Test context management verification when present."""
    artifacts = {
        'llm_files': ['context_manager.py', 'llm_service.py']
    }
    
    result = ai_reasoning_analyzer._verify_context_management(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_context_management_partial(ai_reasoning_analyzer):
    """Test context management verification when partial."""
    artifacts = {
        'llm_files': ['llm_service.py']
    }
    
    result = ai_reasoning_analyzer._verify_context_management(artifacts)
    
    assert result['status'] == 'partial'


def test_verify_response_parsing_present(ai_reasoning_analyzer):
    """Test response parsing verification when present."""
    artifacts = {
        'llm_files': ['response_parser.py', 'llm_service.py']
    }
    
    result = ai_reasoning_analyzer._verify_response_parsing(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_response_parsing_partial(ai_reasoning_analyzer):
    """Test response parsing verification when partial."""
    artifacts = {
        'llm_files': ['llm_service.py']
    }
    
    result = ai_reasoning_analyzer._verify_response_parsing(artifacts)
    
    assert result['status'] == 'partial'


def test_verify_response_validation_present(ai_reasoning_analyzer):
    """Test response validation verification when present."""
    artifacts = {
        'llm_files': ['response_validator.py', 'llm_service.py']
    }
    
    result = ai_reasoning_analyzer._verify_response_validation(artifacts)
    
    assert result['status'] == 'implemented'


def test_verify_response_validation_partial(ai_reasoning_analyzer):
    """Test response validation verification when partial."""
    artifacts = {
        'llm_files': ['llm_service.py']
    }
    
    result = ai_reasoning_analyzer._verify_response_validation(artifacts)
    
    assert result['status'] == 'partial'


# ============================================================================
# Integration Layer Tests
# ============================================================================

def test_analyze_integration_layer_complete():
    """Test Integration Layer analysis with complete implementation."""
    project_structure = ProjectStructure(
        root_path=Path("/test/project"),
        directories=["src", "webhooks", "auth", "github"],
        files_by_extension={
            ".py": [
                "src/webhooks/github_webhook.py",
                "src/webhooks/webhook_handler.py",
                "src/github/github_client.py",
                "src/github/github_api.py",
                "src/auth/oauth.py"
            ],
            ".ts": [
                "frontend/pages/api/auth/[...nextauth].ts",
                "frontend/lib/auth.ts"
            ],
            ".env": [".env", ".env.example"]
        },
        total_files=8,
        total_directories=4
    )
    
    configurations = ConfigurationFiles(
        docker_compose=None,
        package_json={
            "dependencies": {
                "next-auth": "^4.24.0",
                "react": "^18.0.0"
            }
        },
        requirements_txt=["PyGithub==2.1.0", "fastapi==0.104.0"]
    )
    
    documentation = Documentation(
        readme="# Project with GitHub integration",
        architecture_docs={},
        other_docs={}
    )
    
    system_info = SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation=documentation,
        services=["api", "webhook-service"],
        technologies={}
    )
    
    analyzer = LayerAnalyzer(system_info)
    result = analyzer.analyze_integration_layer()
    
    assert result.layer_name == "Integration"
    assert result.completeness_score > 0.0
    assert len(result.capabilities_assessed) > 0
    assert len(result.implemented_capabilities) > 0


def test_analyze_integration_layer_has_github_webhooks():
    """Test that Integration Layer detects GitHub webhook implementation."""
    project_structure = ProjectStructure(
        root_path=Path("/test/project"),
        directories=["src", "webhooks"],
        files_by_extension={
            ".py": [
                "src/webhooks/github_webhook.py",
                "src/webhooks/webhook_handler.py"
            ]
        },
        total_files=2,
        total_directories=2
    )
    
    system_info = SystemInfo(
        project_structure=project_structure,
        configurations=ConfigurationFiles(None, {}, []),
        documentation=Documentation("", {}, {}),
        services=["webhook-service"],
        technologies={}
    )
    
    analyzer = LayerAnalyzer(system_info)
    result = analyzer.analyze_integration_layer()
    
    # Should detect webhook files
    webhook_capability = next(
        (cap for cap in result.implemented_capabilities 
         if "Webhook" in cap.name),
        None
    )
    assert webhook_capability is not None or len(result.partial_capabilities) > 0


def test_analyze_integration_layer_has_oauth():
    """Test that Integration Layer detects OAuth implementation."""
    project_structure = ProjectStructure(
        root_path=Path("/test/project"),
        directories=["frontend", "pages", "api", "auth"],
        files_by_extension={
            ".ts": [
                "frontend/pages/api/auth/[...nextauth].ts",
                "frontend/lib/oauth.ts"
            ]
        },
        total_files=2,
        total_directories=4
    )
    
    configurations = ConfigurationFiles(
        docker_compose=None,
        package_json={
            "dependencies": {
                "next-auth": "^4.24.0"
            }
        },
        requirements_txt=[]
    )
    
    system_info = SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation=Documentation("", {}, {}),
        services=[],
        technologies={}
    )
    
    analyzer = LayerAnalyzer(system_info)
    result = analyzer.analyze_integration_layer()
    
    # Should detect NextAuth
    oauth_capability = next(
        (cap for cap in result.implemented_capabilities 
         if "OAuth" in cap.name or "NextAuth" in cap.name),
        None
    )
    assert oauth_capability is not None or len(result.partial_capabilities) > 0


def test_analyze_integration_layer_has_github_api():
    """Test that Integration Layer detects GitHub API integration."""
    project_structure = ProjectStructure(
        root_path=Path("/test/project"),
        directories=["src", "github"],
        files_by_extension={
            ".py": [
                "src/github/github_client.py",
                "src/github/github_api.py"
            ]
        },
        total_files=2,
        total_directories=2
    )
    
    configurations = ConfigurationFiles(
        docker_compose=None,
        package_json={},
        requirements_txt=["PyGithub==2.1.0"]
    )
    
    system_info = SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation=Documentation("", {}, {}),
        services=[],
        technologies={}
    )
    
    analyzer = LayerAnalyzer(system_info)
    result = analyzer.analyze_integration_layer()
    
    # Should detect GitHub API integration
    github_capability = next(
        (cap for cap in result.implemented_capabilities 
         if "GitHub API" in cap.name),
        None
    )
    assert github_capability is not None or len(result.partial_capabilities) > 0


def test_analyze_integration_layer_missing_features():
    """Test Integration Layer analysis with missing features."""
    project_structure = ProjectStructure(
        root_path=Path("/test/project"),
        directories=["src"],
        files_by_extension={
            ".py": ["src/main.py"]
        },
        total_files=1,
        total_directories=1
    )
    
    system_info = SystemInfo(
        project_structure=project_structure,
        configurations=ConfigurationFiles(None, {}, []),
        documentation=Documentation("", {}, {}),
        services=[],
        technologies={}
    )
    
    analyzer = LayerAnalyzer(system_info)
    result = analyzer.analyze_integration_layer()
    
    assert result.layer_name == "Integration"
    assert result.completeness_score < 1.0
    assert len(result.missing_capabilities) > 0
    assert len(result.gaps) > 0


def test_extract_integration_artifacts():
    """Test extraction of Integration Layer artifacts."""
    project_structure = ProjectStructure(
        root_path=Path("/test/project"),
        directories=["src", "webhooks", "github"],
        files_by_extension={
            ".py": [
                "src/webhooks/github_webhook.py",
                "src/github/github_client.py",
                "src/auth/oauth.py"
            ],
            ".ts": [
                "frontend/pages/api/auth/[...nextauth].ts"
            ],
            ".env": [".env"]
        },
        total_files=5,
        total_directories=3
    )
    
    configurations = ConfigurationFiles(
        docker_compose=None,
        package_json={
            "dependencies": {
                "next-auth": "^4.24.0"
            }
        },
        requirements_txt=["PyGithub==2.1.0"]
    )
    
    system_info = SystemInfo(
        project_structure=project_structure,
        configurations=configurations,
        documentation=Documentation("", {}, {}),
        services=["webhook-service"],
        technologies={}
    )
    
    analyzer = LayerAnalyzer(system_info)
    artifacts = analyzer._extract_integration_artifacts()
    
    assert "webhook_files" in artifacts
    assert "oauth_files" in artifacts
    assert "github_api_files" in artifacts
    assert "nextauth_installed" in artifacts
    assert "pygithub_installed" in artifacts
    assert artifacts["nextauth_installed"] is True
    assert artifacts["pygithub_installed"] is True
    assert len(artifacts["webhook_files"]) > 0
    assert len(artifacts["github_api_files"]) > 0


def test_verify_github_webhooks_present():
    """Test verification of GitHub webhook presence."""
    artifacts = {
        "webhook_files": ["src/webhooks/github_webhook.py"],
        "services": ["webhook-service"]
    }
    
    analyzer = LayerAnalyzer(SystemInfo(
        ProjectStructure(Path("/test"), [], {}, 0, 0),
        ConfigurationFiles(None, {}, []),
        Documentation("", {}, {}),
        [],
        {}
    ))
    
    result = analyzer._verify_github_webhooks(artifacts)
    
    assert result["status"] == "implemented"


def test_verify_github_webhooks_missing():
    """Test verification when GitHub webhooks are missing."""
    artifacts = {
        "webhook_files": [],
        "services": []
    }
    
    analyzer = LayerAnalyzer(SystemInfo(
        ProjectStructure(Path("/test"), [], {}, 0, 0),
        ConfigurationFiles(None, {}, []),
        Documentation("", {}, {}),
        [],
        {}
    ))
    
    result = analyzer._verify_github_webhooks(artifacts)
    
    assert result["status"] == "missing"


def test_verify_oauth_complete():
    """Test verification of complete OAuth implementation."""
    artifacts = {
        "nextauth_installed": True,
        "oauth_files": ["frontend/pages/api/auth/[...nextauth].ts"]
    }
    
    analyzer = LayerAnalyzer(SystemInfo(
        ProjectStructure(Path("/test"), [], {}, 0, 0),
        ConfigurationFiles(None, {}, []),
        Documentation("", {}, {}),
        [],
        {}
    ))
    
    result = analyzer._verify_oauth(artifacts)
    
    assert result["status"] == "implemented"


def test_verify_oauth_partial():
    """Test verification of partial OAuth implementation."""
    artifacts = {
        "nextauth_installed": True,
        "oauth_files": []
    }
    
    analyzer = LayerAnalyzer(SystemInfo(
        ProjectStructure(Path("/test"), [], {}, 0, 0),
        ConfigurationFiles(None, {}, []),
        Documentation("", {}, {}),
        [],
        {}
    ))
    
    result = analyzer._verify_oauth(artifacts)
    
    assert result["status"] == "partial"


def test_verify_oauth_missing():
    """Test verification when OAuth is missing."""
    artifacts = {
        "nextauth_installed": False,
        "oauth_files": []
    }
    
    analyzer = LayerAnalyzer(SystemInfo(
        ProjectStructure(Path("/test"), [], {}, 0, 0),
        ConfigurationFiles(None, {}, []),
        Documentation("", {}, {}),
        [],
        {}
    ))
    
    result = analyzer._verify_oauth(artifacts)
    
    assert result["status"] == "missing"


def test_verify_github_api_complete():
    """Test verification of complete GitHub API integration."""
    artifacts = {
        "github_api_files": ["src/github/github_client.py"],
        "pygithub_installed": True
    }
    
    analyzer = LayerAnalyzer(SystemInfo(
        ProjectStructure(Path("/test"), [], {}, 0, 0),
        ConfigurationFiles(None, {}, []),
        Documentation("", {}, {}),
        [],
        {}
    ))
    
    result = analyzer._verify_github_api(artifacts)
    
    assert result["status"] == "implemented"


def test_verify_github_api_partial():
    """Test verification of partial GitHub API integration."""
    artifacts = {
        "github_api_files": ["src/github/github_client.py"],
        "pygithub_installed": False
    }
    
    analyzer = LayerAnalyzer(SystemInfo(
        ProjectStructure(Path("/test"), [], {}, 0, 0),
        ConfigurationFiles(None, {}, []),
        Documentation("", {}, {}),
        [],
        {}
    ))
    
    result = analyzer._verify_github_api(artifacts)
    
    assert result["status"] == "partial"


def test_verify_github_api_missing():
    """Test verification when GitHub API integration is missing."""
    artifacts = {
        "github_api_files": [],
        "pygithub_installed": False
    }
    
    analyzer = LayerAnalyzer(SystemInfo(
        ProjectStructure(Path("/test"), [], {}, 0, 0),
        ConfigurationFiles(None, {}, []),
        Documentation("", {}, {}),
        [],
        {}
    ))
    
    result = analyzer._verify_github_api(artifacts)
    
    assert result["status"] == "missing"


def test_verify_nextauth_present():
    """Test verification of NextAuth presence."""
    artifacts = {
        "nextauth_installed": True,
        "oauth_files": ["frontend/pages/api/auth/[...nextauth].ts"]
    }
    
    analyzer = LayerAnalyzer(SystemInfo(
        ProjectStructure(Path("/test"), [], {}, 0, 0),
        ConfigurationFiles(None, {}, []),
        Documentation("", {}, {}),
        [],
        {}
    ))
    
    result = analyzer._verify_nextauth(artifacts)
    
    assert result["status"] == "implemented"


def test_verify_nextauth_missing():
    """Test verification when NextAuth is missing."""
    artifacts = {
        "nextauth_installed": False,
        "oauth_files": []
    }
    
    analyzer = LayerAnalyzer(SystemInfo(
        ProjectStructure(Path("/test"), [], {}, 0, 0),
        ConfigurationFiles(None, {}, []),
        Documentation("", {}, {}),
        [],
        {}
    ))
    
    result = analyzer._verify_nextauth(artifacts)
    
    assert result["status"] == "missing"


def test_verify_secure_credentials_partial():
    """Test verification of secure credential storage."""
    artifacts = {
        "env_files": [".env", ".env.example"]
    }
    
    analyzer = LayerAnalyzer(SystemInfo(
        ProjectStructure(Path("/test"), [], {}, 0, 0),
        ConfigurationFiles(None, {}, []),
        Documentation("", {}, {}),
        [],
        {}
    ))
    
    result = analyzer._verify_secure_credentials(artifacts)
    
    assert result["status"] == "partial"


def test_verify_secure_credentials_missing():
    """Test verification when secure credential storage is missing."""
    artifacts = {
        "env_files": []
    }
    
    analyzer = LayerAnalyzer(SystemInfo(
        ProjectStructure(Path("/test"), [], {}, 0, 0),
        ConfigurationFiles(None, {}, []),
        Documentation("", {}, {}),
        [],
        {}
    ))
    
    result = analyzer._verify_secure_credentials(artifacts)
    
    assert result["status"] == "missing"
