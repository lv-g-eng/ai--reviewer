"""
Unit tests for Service Merger component
"""

import asyncio
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from app.services.service_merger import (
    ServiceMerger,
    MergeOperation,
    FunctionalityValidation,
    ReferenceUpdate
)
from app.services.service_consolidator import (
    ConsolidationPlan,
    ConsolidationStrategy,
    ServiceFunction,
    MergeResult
)


class TestServiceMerger:
    """Test cases for ServiceMerger"""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create services directory structure
            services_dir = project_root / "services"
            services_dir.mkdir()
            
            # Create source service
            source_service_dir = services_dir / "source-service"
            source_service_dir.mkdir()
            (source_service_dir / "src").mkdir()
            
            # Create package.json
            package_json = {
                "name": "@ai-code-review/source-service",
                "dependencies": {"express": "^4.18.2", "axios": "^1.6.2"}
            }
            with open(source_service_dir / "package.json", "w") as f:
                json.dump(package_json, f)
            
            # Create source TypeScript file
            source_ts = """
import express from 'express';
import axios from 'axios';

const router = express.Router();

export function sourceFunction() {
    return 'source functionality';
}

router.get('/source', (req, res) => {
    res.json({ message: sourceFunction() });
});

export default router;
"""
            with open(source_service_dir / "src" / "index.ts", "w") as f:
                f.write(source_ts)
            
            # Create target service
            target_service_dir = services_dir / "target-service"
            target_service_dir.mkdir()
            (target_service_dir / "src").mkdir()
            
            # Create target package.json
            target_package_json = {
                "name": "@ai-code-review/target-service",
                "dependencies": {"express": "^4.18.2", "winston": "^3.11.0"}
            }
            with open(target_service_dir / "package.json", "w") as f:
                json.dump(target_package_json, f)
            
            # Create target TypeScript file
            target_ts = """
import express from 'express';
import winston from 'winston';

const router = express.Router();

export function targetFunction() {
    return 'target functionality';
}

router.get('/target', (req, res) => {
    res.json({ message: targetFunction() });
});

export default router;
"""
            with open(target_service_dir / "src" / "index.ts", "w") as f:
                f.write(target_ts)
            
            # Create backend directory
            backend_dir = project_root / "backend"
            backend_dir.mkdir()
            (backend_dir / "app").mkdir()
            (backend_dir / "app" / "services").mkdir()
            
            # Create frontend directory with references
            frontend_dir = project_root / "frontend"
            frontend_dir.mkdir()
            (frontend_dir / "src").mkdir()
            
            # Create frontend file with service references
            frontend_api = """
const API_ENDPOINTS = {
    sourceService: 'http://source-service:3001',
    targetService: 'http://target-service:3002'
};

export async function callSourceService() {
    const response = await fetch(`${API_ENDPOINTS.sourceService}/source`);
    return response.json();
}
"""
            with open(frontend_dir / "src" / "api.ts", "w") as f:
                f.write(frontend_api)
            
            # Create configuration files
            docker_compose = """
version: '3.8'
services:
  source-service:
    build: ./services/source-service
    ports:
      - "3001:3001"
  target-service:
    build: ./services/target-service
    ports:
      - "3002:3002"
"""
            with open(project_root / "docker-compose.yml", "w") as f:
                f.write(docker_compose)
            
            yield project_root

    @pytest.fixture
    def merger(self, temp_project_dir):
        """Create ServiceMerger instance with temp directory"""
        return ServiceMerger(str(temp_project_dir))

    @pytest.fixture
    def sample_consolidation_plan(self):
        """Create a sample consolidation plan"""
        return ConsolidationPlan(
            plan_id="test_merge",
            strategy=ConsolidationStrategy.MERGE_SIMILAR,
            source_services=["source-service"],
            target_service="target-service",
            estimated_effort=40,
            risk_level="low",
            preserved_functions=[
                ServiceFunction(
                    name="sourceFunction",
                    description="Source functionality",
                    complexity_score=3
                )
            ]
        )

    @pytest.mark.asyncio
    async def test_create_backup(self, merger, sample_consolidation_plan):
        """Test backup creation functionality"""
        backup_path = await merger._create_backup(sample_consolidation_plan)
        
        assert backup_path.exists()
        assert backup_path.is_dir()
        
        # Check backup manifest
        manifest_path = backup_path / "backup_manifest.json"
        assert manifest_path.exists()
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        assert manifest["plan_id"] == "test_merge"
        assert "source-service" in manifest["source_services"]
        assert manifest["target_service"] == "target-service"
        
        # Check that services were backed up
        backup_source = backup_path / "services" / "source-service"
        assert backup_source.exists()
        assert (backup_source / "package.json").exists()

    @pytest.mark.asyncio
    async def test_plan_merge_operations(self, merger, sample_consolidation_plan):
        """Test merge operation planning"""
        operations = await merger._plan_merge_operations(sample_consolidation_plan)
        
        assert isinstance(operations, list)
        assert len(operations) > 0
        
        # Check operation types
        operation_types = {op.operation_type for op in operations}
        assert "move_file" in operation_types
        assert "merge_code" in operation_types
        
        # Check that source files are planned for migration
        source_operations = [op for op in operations if "source-service" in op.source_path]
        assert len(source_operations) > 0

    @pytest.mark.asyncio
    async def test_plan_source_code_migration(self, merger):
        """Test source code migration planning"""
        source_dir = merger.project_root / "services" / "source-service" / "src"
        operations = await merger._plan_source_code_migration(
            "source-service", "target-service", source_dir
        )
        
        assert isinstance(operations, list)
        assert len(operations) > 0
        
        # Check that index.ts is planned for migration
        index_operations = [op for op in operations if "index.ts" in op.source_path]
        assert len(index_operations) > 0
        
        operation = index_operations[0]
        assert operation.operation_type == "move_file"
        assert "source-service" in operation.source_path
        assert "target-service" in operation.target_path

    @pytest.mark.asyncio
    async def test_plan_configuration_migration(self, merger):
        """Test configuration migration planning"""
        source_path = merger.project_root / "services" / "source-service"
        operations = await merger._plan_configuration_migration(
            "source-service", "target-service", source_path
        )
        
        assert isinstance(operations, list)
        assert len(operations) > 0
        
        # Check for package.json merge operation
        package_operations = [op for op in operations if "package.json" in op.source_path]
        assert len(package_operations) > 0
        
        operation = package_operations[0]
        assert operation.operation_type == "merge_code"

    @pytest.mark.asyncio
    async def test_move_file(self, merger, temp_project_dir):
        """Test file moving functionality"""
        source_file = temp_project_dir / "test_source.txt"
        target_file = temp_project_dir / "subdir" / "test_target.txt"
        
        # Create source file
        source_file.write_text("test content")
        
        # Move file
        await merger._move_file(str(source_file), str(target_file))
        
        # Check results
        assert not source_file.exists()
        assert target_file.exists()
        assert target_file.read_text() == "test content"

    @pytest.mark.asyncio
    async def test_merge_json_files(self, merger):
        """Test JSON file merging"""
        source_content = '{"dependencies": {"axios": "^1.6.2"}, "scripts": {"test": "jest"}}'
        target_content = '{"dependencies": {"express": "^4.18.2"}, "scripts": {"build": "tsc"}}'
        
        merged_content = await merger._merge_json_files(source_content, target_content)
        merged_data = json.loads(merged_content)
        
        # Check that dependencies are merged
        assert "axios" in merged_data["dependencies"]
        assert "express" in merged_data["dependencies"]
        
        # Check that scripts are merged
        assert "test" in merged_data["scripts"]
        assert "build" in merged_data["scripts"]

    def test_deep_merge_dict(self, merger):
        """Test deep dictionary merging"""
        target = {
            "dependencies": {"express": "^4.18.2"},
            "scripts": {"build": "tsc"},
            "config": {"port": 3000}
        }
        
        source = {
            "dependencies": {"axios": "^1.6.2"},
            "scripts": {"test": "jest"},
            "config": {"host": "localhost"}
        }
        
        result = merger._deep_merge_dict(target, source)
        
        assert "express" in result["dependencies"]
        assert "axios" in result["dependencies"]
        assert "build" in result["scripts"]
        assert "test" in result["scripts"]
        assert result["config"]["port"] == 3000
        assert result["config"]["host"] == "localhost"

    @pytest.mark.asyncio
    async def test_merge_typescript_files(self, merger):
        """Test TypeScript file merging"""
        source_content = """
import axios from 'axios';
import { Request } from 'express';

export function sourceFunction() {
    return 'source';
}
"""
        
        target_content = """
import express from 'express';
import winston from 'winston';

export function targetFunction() {
    return 'target';
}
"""
        
        merged_content = await merger._merge_typescript_files(source_content, target_content)
        
        # Check that imports are merged
        assert "import axios from 'axios';" in merged_content
        assert "import express from 'express';" in merged_content
        assert "import winston from 'winston';" in merged_content
        
        # Check that functions are preserved
        assert "sourceFunction" in merged_content
        assert "targetFunction" in merged_content

    def test_extract_imports(self, merger):
        """Test import extraction from TypeScript"""
        content = """
import express from 'express';
import { Router } from 'express';
import axios from 'axios';

const app = express();
"""
        
        imports = merger._extract_imports(content)
        
        assert len(imports) == 3
        assert "import express from 'express';" in imports
        assert "import { Router } from 'express';" in imports
        assert "import axios from 'axios';" in imports

    def test_remove_imports(self, merger):
        """Test import removal from TypeScript"""
        content = """
import express from 'express';
import { Router } from 'express';

const app = express();
const router = Router();
"""
        
        content_without_imports = merger._remove_imports(content)
        
        assert "import express" not in content_without_imports
        assert "import { Router }" not in content_without_imports
        assert "const app = express();" in content_without_imports
        assert "const router = Router();" in content_without_imports

    @pytest.mark.asyncio
    async def test_find_and_update_references(self, merger, sample_consolidation_plan):
        """Test reference finding and updating"""
        reference_updates = await merger._find_and_update_references(sample_consolidation_plan)
        
        assert isinstance(reference_updates, list)
        
        # Should find references in frontend API file
        api_references = [ref for ref in reference_updates if "api.ts" in ref.file_path]
        assert len(api_references) > 0
        
        # Should find references in docker-compose.yml
        docker_references = [ref for ref in reference_updates if "docker-compose.yml" in ref.file_path]
        assert len(docker_references) > 0

    @pytest.mark.asyncio
    async def test_search_references_in_file(self, merger, sample_consolidation_plan):
        """Test reference searching in a single file"""
        file_path = merger.project_root / "frontend" / "src" / "api.ts"
        patterns = ["source-service", "target-service"]
        
        references = await merger._search_references_in_file(file_path, patterns, sample_consolidation_plan)
        
        assert isinstance(references, list)
        assert len(references) > 0
        
        # Check reference structure
        ref = references[0]
        assert isinstance(ref, ReferenceUpdate)
        assert ref.file_path == str(file_path)
        assert ref.line_number > 0
        assert ref.old_reference in patterns

    def test_generate_new_reference(self, merger, sample_consolidation_plan):
        """Test new reference generation"""
        old_ref = "source-service"
        new_ref = merger._generate_new_reference(old_ref, sample_consolidation_plan)
        
        assert new_ref == "target-service"

    @pytest.mark.asyncio
    async def test_execute_reference_update(self, merger, temp_project_dir):
        """Test reference update execution"""
        test_file = temp_project_dir / "test_refs.txt"
        test_file.write_text("This is source-service and target-service")
        
        ref_update = ReferenceUpdate(
            file_path=str(test_file),
            line_number=1,
            old_reference="source-service",
            new_reference="consolidated-service",
            context="test context"
        )
        
        await merger._execute_reference_update(ref_update)
        
        updated_content = test_file.read_text()
        assert "consolidated-service" in updated_content
        assert "source-service" not in updated_content

    @pytest.mark.asyncio
    async def test_validate_single_function(self, merger, sample_consolidation_plan):
        """Test single function validation"""
        function = ServiceFunction(
            name="testFunction",
            description="Test function",
            complexity_score=5
        )
        
        validation = await merger._validate_single_function(function, sample_consolidation_plan)
        
        assert isinstance(validation, FunctionalityValidation)
        assert validation.function_name == "testFunction"
        assert validation.target_service == "target-service"
        assert validation.validation_status in ["passed", "warning", "failed"]
        assert len(validation.test_results) > 0

    @pytest.mark.asyncio
    async def test_validate_functionality_preservation(self, merger, sample_consolidation_plan):
        """Test functionality preservation validation"""
        validations = await merger._validate_functionality_preservation(sample_consolidation_plan)
        
        assert isinstance(validations, list)
        assert len(validations) == len(sample_consolidation_plan.preserved_functions)
        
        if validations:
            validation = validations[0]
            assert isinstance(validation, FunctionalityValidation)
            assert validation.function_name == "sourceFunction"

    @pytest.mark.asyncio
    async def test_rollback_changes(self, merger, sample_consolidation_plan):
        """Test change rollback functionality"""
        # Create backup first
        backup_path = await merger._create_backup(sample_consolidation_plan)
        
        # Modify source service (simulate merge)
        source_service_path = merger.project_root / "services" / "source-service"
        modified_file = source_service_path / "modified.txt"
        modified_file.write_text("modified content")
        
        # Rollback changes
        await merger._rollback_changes(backup_path)
        
        # Check that modifications are reverted
        assert not modified_file.exists()
        assert source_service_path.exists()
        assert (source_service_path / "package.json").exists()

    def test_generate_merge_report(self, merger, sample_consolidation_plan):
        """Test merge report generation"""
        operations = [
            MergeOperation(
                operation_id="test_op",
                operation_type="move_file",
                source_path="/source",
                target_path="/target",
                description="Test operation",
                status="completed"
            )
        ]
        
        references = [
            ReferenceUpdate(
                file_path="/test/file.ts",
                line_number=1,
                old_reference="old-ref",
                new_reference="new-ref",
                context="test context",
                update_status="completed"
            )
        ]
        
        validations = [
            FunctionalityValidation(
                function_name="testFunc",
                original_service="source",
                target_service="target",
                validation_status="passed"
            )
        ]
        
        report = merger._generate_merge_report(sample_consolidation_plan, operations, references, validations)
        
        assert isinstance(report, dict)
        assert "merge_timestamp" in report
        assert report["plan_id"] == "test_merge"
        assert report["operations_summary"]["total_operations"] == 1
        assert report["operations_summary"]["completed_operations"] == 1
        assert report["references_summary"]["total_references"] == 1
        assert report["validation_summary"]["total_functions"] == 1

    @pytest.mark.asyncio
    async def test_execute_service_merge_success(self, merger, sample_consolidation_plan):
        """Test successful service merge execution"""
        result = await merger.execute_service_merge(sample_consolidation_plan)
        
        assert isinstance(result, MergeResult)
        assert result.success is True
        assert result.merged_service == "target-service"
        assert "source-service" in result.original_services
        assert len(result.preserved_functions) > 0

    @pytest.mark.asyncio
    async def test_execute_service_merge_with_backup(self, merger, sample_consolidation_plan):
        """Test service merge with backup creation"""
        # Execute merge
        result = await merger.execute_service_merge(sample_consolidation_plan)
        
        # Check that backup was created
        backup_dir = merger.project_root / ".consolidation_backups"
        assert backup_dir.exists()
        
        # Check backup contents
        backup_subdirs = list(backup_dir.iterdir())
        assert len(backup_subdirs) > 0
        
        backup_path = backup_subdirs[0]
        manifest_path = backup_path / "backup_manifest.json"
        assert manifest_path.exists()


class TestServiceMergerIntegration:
    """Integration tests for ServiceMerger"""

    @pytest.mark.asyncio
    async def test_full_merge_workflow(self, temp_project_dir):
        """Test complete merge workflow"""
        merger = ServiceMerger(str(temp_project_dir))
        
        # Create consolidation plan
        plan = ConsolidationPlan(
            plan_id="integration_test",
            strategy=ConsolidationStrategy.MERGE_SIMILAR,
            source_services=["source-service"],
            target_service="target-service",
            estimated_effort=40,
            risk_level="low",
            preserved_functions=[
                ServiceFunction(name="sourceFunction", description="Source function")
            ]
        )
        
        # Execute merge
        result = await merger.execute_service_merge(plan)
        
        # Verify results
        assert isinstance(result, MergeResult)
        assert result.success is True
        
        # Check that backup was created
        backup_dir = merger.project_root / ".consolidation_backups"
        assert backup_dir.exists()

    @pytest.mark.asyncio
    async def test_merge_with_reference_updates(self, temp_project_dir):
        """Test merge with comprehensive reference updates"""
        merger = ServiceMerger(str(temp_project_dir))
        
        # Create additional files with references
        config_file = temp_project_dir / "config.json"
        config_file.write_text('{"services": {"source-service": "http://localhost:3001"}}')
        
        plan = ConsolidationPlan(
            plan_id="ref_update_test",
            strategy=ConsolidationStrategy.MERGE_SIMILAR,
            source_services=["source-service"],
            target_service="target-service",
            estimated_effort=40,
            risk_level="low"
        )
        
        # Execute merge
        result = await merger.execute_service_merge(plan)
        
        # Verify reference updates
        assert result.success is True
        assert len(result.updated_references) > 0


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory structure for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        
        # Create services directory structure
        services_dir = project_root / "services"
        services_dir.mkdir()
        
        # Create source service
        source_service_dir = services_dir / "source-service"
        source_service_dir.mkdir()
        (source_service_dir / "src").mkdir()
        
        # Create package.json
        package_json = {
            "name": "@ai-code-review/source-service",
            "dependencies": {"express": "^4.18.2"}
        }
        with open(source_service_dir / "package.json", "w") as f:
            json.dump(package_json, f)
        
        # Create target service
        target_service_dir = services_dir / "target-service"
        target_service_dir.mkdir()
        (target_service_dir / "src").mkdir()
        
        yield project_root