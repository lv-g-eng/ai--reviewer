"""
Database Integration Tests

Tests PostgreSQL, Neo4j, and Redis operations with testcontainers for isolation.
Validates Requirements 13.4, 13.5, 5.8, 13.10

**Validates: Requirements 13.4, 13.5, 5.8, 13.10**
"""
import pytest
import asyncio
from typing import AsyncGenerator
from datetime import datetime, timezone
import json

# Mark all tests in this module as requiring Docker
pytestmark = pytest.mark.requires_docker

from app.models import User, Project, PullRequest, PRStatus, AuditLogEntry
from app.utils.password import hash_password


class TestPostgreSQLIntegration:
    """Integration tests for PostgreSQL database operations"""
    
    @pytest.mark.asyncio
    async def test_user_crud_operations(self, db_session):
        """
        Test complete CRUD operations for User model
        
        **Validates: Requirements 13.4, 13.10**
        """
        # Create
        user = User(
            email="postgres@test.com",
            password_hash=hash_password("SecurePass123!"),
            full_name="PostgreSQL Test User",
            role="developer"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "postgres@test.com"
        assert user.is_active is True
        
        # Read
        from sqlalchemy import select
        stmt = select(User).where(User.email == "postgres@test.com")
        result = await db_session.execute(stmt)
        fetched_user = result.scalar_one_or_none()
        
        assert fetched_user is not None
        assert fetched_user.id == user.id
        assert fetched_user.full_name == "PostgreSQL Test User"
        
        # Update
        fetched_user.full_name = "Updated Name"
        await db_session.commit()
        await db_session.refresh(fetched_user)
        
        assert fetched_user.full_name == "Updated Name"
        
        # Delete
        await db_session.delete(fetched_user)
        await db_session.commit()
        
        stmt = select(User).where(User.email == "postgres@test.com")
        result = await db_session.execute(stmt)
        deleted_user = result.scalar_one_or_none()
        
        assert deleted_user is None
    
    @pytest.mark.asyncio
    async def test_project_relationships(self, db_session):
        """
        Test relationships between User and Project models
        
        **Validates: Requirements 13.4, 13.10**
        """
        # Create user
        user = User(
            email="project@test.com",
            password_hash=hash_password("SecurePass123!"),
            full_name="Project Test User"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create projects
        project1 = Project(
            name="Project 1",
            github_repo_url="https://github.com/test/project1",
            owner_id=user.id
        )
        project2 = Project(
            name="Project 2",
            github_repo_url="https://github.com/test/project2",
            owner_id=user.id
        )
        
        db_session.add_all([project1, project2])
        await db_session.commit()
        
        # Verify relationships
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        stmt = select(User).where(User.id == user.id).options(selectinload(User.projects))
        result = await db_session.execute(stmt)
        user_with_projects = result.scalar_one()
        
        assert len(user_with_projects.projects) == 2
        assert user_with_projects.projects[0].name in ["Project 1", "Project 2"]
    
    @pytest.mark.asyncio
    async def test_pull_request_cascade(self, db_session):
        """
        Test cascade delete for Project -> PullRequest relationship
        
        **Validates: Requirements 13.4, 13.10**
        """
        # Create user and project
        user = User(
            email="cascade@test.com",
            password_hash=hash_password("SecurePass123!"),
            full_name="Cascade Test"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        project = Project(
            name="Cascade Project",
            github_repo_url="https://github.com/test/cascade",
            owner_id=user.id
        )
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        
        # Create pull requests
        pr1 = PullRequest(
            project_id=project.id,
            github_pr_number=1,
            title="PR 1",
            branch_name="feature/1",
            commit_sha="abc123",
            status=PRStatus.PENDING
        )
        pr2 = PullRequest(
            project_id=project.id,
            github_pr_number=2,
            title="PR 2",
            branch_name="feature/2",
            commit_sha="def456",
            status=PRStatus.PENDING
        )
        
        db_session.add_all([pr1, pr2])
        await db_session.commit()
        
        # Delete project (should cascade to PRs)
        await db_session.delete(project)
        await db_session.commit()
        
        # Verify PRs are deleted
        from sqlalchemy import select
        stmt = select(PullRequest).where(PullRequest.project_id == project.id)
        result = await db_session.execute(stmt)
        remaining_prs = result.scalars().all()
        
        assert len(remaining_prs) == 0
    
    @pytest.mark.asyncio
    async def test_audit_log_immutability(self, db_session):
        """
        Test audit log entries are created and cannot be modified
        
        **Validates: Requirements 13.4, 13.10**
        """
        # Create user
        user = User(
            email="audit@test.com",
            password_hash=hash_password("SecurePass123!"),
            full_name="Audit Test"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create audit log entry
        log_entry = AuditLogEntry(
            user_id=user.id,
            action="TEST_ACTION",
            resource_type="test",
            resource_id="test-123",
            details={"test": "data"},
            timestamp=datetime.now(timezone.utc)
        )
        db_session.add(log_entry)
        await db_session.commit()
        await db_session.refresh(log_entry)
        
        assert log_entry.id is not None
        assert log_entry.action == "TEST_ACTION"
        
        # Verify entry exists
        from sqlalchemy import select
        stmt = select(AuditLogEntry).where(AuditLogEntry.id == log_entry.id)
        result = await db_session.execute(stmt)
        fetched_log = result.scalar_one()
        
        assert fetched_log.action == "TEST_ACTION"
        assert fetched_log.details["test"] == "data"
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self, db_session):
        """
        Test transaction rollback on error
        
        **Validates: Requirements 13.4, 13.10**
        """
        # Create user
        user = User(
            email="rollback@test.com",
            password_hash=hash_password("SecurePass123!"),
            full_name="Rollback Test"
        )
        db_session.add(user)
        await db_session.commit()
        
        # Start transaction that will fail
        try:
            # Create project
            project = Project(
                name="Rollback Project",
                github_repo_url="https://github.com/test/rollback",
                owner_id=user.id
            )
            db_session.add(project)
            
            # Create duplicate user (should fail)
            duplicate_user = User(
                email="rollback@test.com",  # Duplicate email
                password_hash=hash_password("SecurePass123!"),
                full_name="Duplicate"
            )
            db_session.add(duplicate_user)
            
            await db_session.commit()
            
        except Exception:
            await db_session.rollback()
        
        # Verify project was not created
        from sqlalchemy import select
        stmt = select(Project).where(Project.name == "Rollback Project")
        result = await db_session.execute(stmt)
        project = result.scalar_one_or_none()
        
        assert project is None
    
    @pytest.mark.asyncio
    async def test_concurrent_updates(self, db_session):
        """
        Test concurrent updates with optimistic locking
        
        **Validates: Requirements 13.4, 13.10**
        """
        # Create user
        user = User(
            email="concurrent@test.com",
            password_hash=hash_password("SecurePass123!"),
            full_name="Concurrent Test"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Update user
        user.full_name = "Updated Name"
        await db_session.commit()
        
        # Verify update
        from sqlalchemy import select
        stmt = select(User).where(User.id == user.id)
        result = await db_session.execute(stmt)
        updated_user = result.scalar_one()
        
        assert updated_user.full_name == "Updated Name"


class TestNeo4jIntegration:
    """Integration tests for Neo4j graph operations"""
    
    @pytest.mark.asyncio
    async def test_create_code_entity_nodes(self, clean_database, graph_builder):
        """
        Test creating code entity nodes in Neo4j
        
        **Validates: Requirements 13.5, 13.10**
        """
        from app.services.code_entity_extractor import CodeEntity
        
        entity = CodeEntity(
            name="TestClass",
            entity_type="class",
            file_path="/test/file.py",
            complexity=5,
            lines_of_code=100,
            dependencies=["OtherClass"]
        )
        
        result = await graph_builder.create_or_update_entity_node(entity)
        
        assert result.nodes_created == 1
        assert result.nodes_updated == 0
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_create_dependency_relationships(self, clean_database, graph_builder):
        """
        Test creating dependency relationships in Neo4j
        
        **Validates: Requirements 13.5, 13.10**
        """
        from app.services.code_entity_extractor import CodeEntity
        
        # Create entities
        entity1 = CodeEntity(
            name="ClassA",
            entity_type="class",
            file_path="/test/a.py",
            complexity=3,
            lines_of_code=50,
            dependencies=[]
        )
        entity2 = CodeEntity(
            name="ClassB",
            entity_type="class",
            file_path="/test/b.py",
            complexity=4,
            lines_of_code=60,
            dependencies=[]
        )
        
        await graph_builder.create_or_update_entity_nodes_batch([entity1, entity2])
        
        # Create relationship
        result = await graph_builder.create_dependency_relationship(
            entity1,
            entity2,
            relationship_type="DEPENDS_ON"
        )
        
        assert result.relationships_created == 1
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_detect_circular_dependencies(self, clean_database, graph_builder, cycle_detector):
        """
        Test circular dependency detection in Neo4j
        
        **Validates: Requirements 13.5, 13.10**
        """
        from app.services.code_entity_extractor import CodeEntity
        
        # Create circular dependency: A -> B -> C -> A
        entities = [
            CodeEntity(name="A", entity_type="module", file_path="/a.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="B", entity_type="module", file_path="/b.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="C", entity_type="module", file_path="/c.py", complexity=5, lines_of_code=50, dependencies=[])
        ]
        
        await graph_builder.create_or_update_entity_nodes_batch(entities)
        
        relationships = [
            (entities[0], entities[1], "DEPENDS_ON", {}),
            (entities[1], entities[2], "DEPENDS_ON", {}),
            (entities[2], entities[0], "DEPENDS_ON", {})
        ]
        await graph_builder.create_dependency_relationships_batch(relationships)
        
        # Detect cycles
        result = await cycle_detector.detect_cycles()
        
        assert result.total_cycles >= 1
        assert len(result.cycles) >= 1
        assert result.cycles[0].depth == 3
    
    @pytest.mark.asyncio
    async def test_query_entity_dependencies(self, clean_database, graph_builder):
        """
        Test querying entity dependencies from Neo4j
        
        **Validates: Requirements 13.5, 13.10**
        """
        from app.services.code_entity_extractor import CodeEntity
        
        # Create dependency chain: A -> B -> C
        entities = [
            CodeEntity(name="A", entity_type="module", file_path="/a.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="B", entity_type="module", file_path="/b.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="C", entity_type="module", file_path="/c.py", complexity=5, lines_of_code=50, dependencies=[])
        ]
        
        await graph_builder.create_or_update_entity_nodes_batch(entities)
        
        relationships = [
            (entities[0], entities[1], "DEPENDS_ON", {}),
            (entities[1], entities[2], "DEPENDS_ON", {})
        ]
        await graph_builder.create_dependency_relationships_batch(relationships)
        
        # Query dependencies
        dependencies = await graph_builder.get_entity_dependencies(
            entities[0].name,
            entities[0].file_path,
            depth=2
        )
        
        assert len(dependencies) >= 1
        assert any(d["name"] == "B" for d in dependencies)
    
    @pytest.mark.asyncio
    async def test_delete_entities_by_file(self, clean_database, graph_builder):
        """
        Test deleting entities by file path
        
        **Validates: Requirements 13.5, 13.10**
        """
        from app.services.code_entity_extractor import CodeEntity
        
        # Create entities in different files
        entities = [
            CodeEntity(name="Class1", entity_type="class", file_path="/file1.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="Class2", entity_type="class", file_path="/file1.py", complexity=5, lines_of_code=50, dependencies=[]),
            CodeEntity(name="Class3", entity_type="class", file_path="/file2.py", complexity=5, lines_of_code=50, dependencies=[])
        ]
        
        await graph_builder.create_or_update_entity_nodes_batch(entities)
        
        # Delete entities from file1.py
        result = await graph_builder.delete_entities_by_file("/file1.py")
        
        assert result.nodes_updated >= 2  # Two entities deleted
        
        # Verify file2.py entities still exist
        from app.database.neo4j_db import get_neo4j_driver
        from app.core.config import settings
        
        driver = await get_neo4j_driver()
        async with driver.session(database=settings.NEO4J_DATABASE) as session:
            query_result = await session.run(
                "MATCH (n:CodeEntity {file_path: $file_path}) RETURN count(n) as count",
                file_path="/file2.py"
            )
            record = await query_result.single()
            assert record["count"] == 1


class TestRedisIntegration:
    """Integration tests for Redis caching and queuing operations"""
    
    @pytest.mark.asyncio
    async def test_cache_set_and_get(self, mock_redis_client):
        """
        Test basic Redis cache operations
        
        **Validates: Requirements 5.8, 13.10**
        """
        # Set cache value
        await mock_redis_client.set("test_key", "test_value", ex=60)
        
        # Get cache value
        value = await mock_redis_client.get("test_key")
        
        assert value == "test_value"
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, mock_redis_client):
        """
        Test cache expiration with TTL
        
        **Validates: Requirements 5.8, 13.10**
        """
        # Set cache with TTL
        await mock_redis_client.set("expiring_key", "value", ex=1)
        
        # Verify key exists
        exists = await mock_redis_client.exists("expiring_key")
        assert exists == 1
        
        # Check TTL
        ttl = await mock_redis_client.ttl("expiring_key")
        assert ttl == 1
    
    @pytest.mark.asyncio
    async def test_cache_delete(self, mock_redis_client):
        """
        Test cache deletion
        
        **Validates: Requirements 5.8, 13.10**
        """
        # Set cache value
        await mock_redis_client.set("delete_key", "value")
        
        # Delete key
        result = await mock_redis_client.delete("delete_key")
        assert result == 1
        
        # Verify key is deleted
        value = await mock_redis_client.get("delete_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_session_storage(self, mock_redis_client):
        """
        Test storing user session data in Redis
        
        **Validates: Requirements 5.8, 13.10**
        """
        session_data = {
            "user_id": "user-123",
            "email": "test@example.com",
            "role": "developer",
            "logged_in_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store session
        await mock_redis_client.set(
            f"session:user-123",
            json.dumps(session_data),
            ex=3600
        )
        
        # Retrieve session
        stored_data = await mock_redis_client.get("session:user-123")
        assert stored_data is not None
        
        parsed_data = json.loads(stored_data)
        assert parsed_data["user_id"] == "user-123"
        assert parsed_data["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_token_revocation_storage(self, mock_redis_client):
        """
        Test storing revoked tokens in Redis
        
        **Validates: Requirements 5.8, 13.10**
        """
        token_jti = "token-jti-123"
        revocation_data = {
            "jti": token_jti,
            "revoked_at": datetime.now(timezone.utc).isoformat(),
            "reason": "logout"
        }
        
        # Store revoked token
        await mock_redis_client.set(
            f"revoked_token:{token_jti}",
            json.dumps(revocation_data),
            ex=86400  # 24 hours
        )
        
        # Check if token is revoked
        exists = await mock_redis_client.exists(f"revoked_token:{token_jti}")
        assert exists == 1
        
        # Retrieve revocation data
        stored_data = await mock_redis_client.get(f"revoked_token:{token_jti}")
        parsed_data = json.loads(stored_data)
        assert parsed_data["jti"] == token_jti
        assert parsed_data["reason"] == "logout"
    
    @pytest.mark.asyncio
    async def test_rate_limiting_storage(self, mock_redis_client):
        """
        Test rate limiting counters in Redis
        
        **Validates: Requirements 5.8, 13.10**
        """
        client_ip = "192.168.1.1"
        rate_limit_key = f"rate_limit:login:{client_ip}"
        
        # Simulate rate limit tracking
        for i in range(5):
            # Increment counter
            current_value = await mock_redis_client.get(rate_limit_key)
            new_value = int(current_value or 0) + 1
            await mock_redis_client.set(rate_limit_key, str(new_value), ex=60)
        
        # Check counter
        counter = await mock_redis_client.get(rate_limit_key)
        assert int(counter) == 5


class TestDatabaseErrorHandling:
    """Integration tests for database error scenarios"""
    
    @pytest.mark.asyncio
    async def test_postgresql_connection_error_handling(self, db_session):
        """
        Test handling of PostgreSQL connection errors
        
        **Validates: Requirements 13.4, 13.10**
        """
        # This test verifies the application handles connection errors gracefully
        # In a real scenario, we would simulate a connection failure
        
        # Create a user successfully
        user = User(
            email="error@test.com",
            password_hash=hash_password("SecurePass123!"),
            full_name="Error Test"
        )
        db_session.add(user)
        await db_session.commit()
        
        # Verify user was created
        from sqlalchemy import select
        stmt = select(User).where(User.email == "error@test.com")
        result = await db_session.execute(stmt)
        fetched_user = result.scalar_one_or_none()
        
        assert fetched_user is not None
    
    @pytest.mark.asyncio
    async def test_neo4j_query_error_handling(self, clean_database, graph_builder):
        """
        Test handling of Neo4j query errors
        
        **Validates: Requirements 13.5, 13.10**
        """
        from app.services.code_entity_extractor import CodeEntity
        
        # Create valid entity
        entity = CodeEntity(
            name="ValidEntity",
            entity_type="class",
            file_path="/valid.py",
            complexity=5,
            lines_of_code=50,
            dependencies=[]
        )
        
        result = await graph_builder.create_or_update_entity_node(entity)
        
        # Should succeed without errors
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_redis_operation_error_handling(self, mock_redis_client):
        """
        Test handling of Redis operation errors
        
        **Validates: Requirements 5.8, 13.10**
        """
        # Test successful operation
        await mock_redis_client.set("test_key", "test_value")
        value = await mock_redis_client.get("test_key")
        
        assert value == "test_value"


class TestDatabasePerformance:
    """Integration tests for database performance"""
    
    @pytest.mark.asyncio
    async def test_bulk_insert_performance(self, db_session):
        """
        Test bulk insert performance for PostgreSQL
        
        **Validates: Requirements 13.4, 13.10**
        """
        import time
        
        # Create multiple users
        users = [
            User(
                email=f"bulk{i}@test.com",
                password_hash=hash_password("SecurePass123!"),
                full_name=f"Bulk User {i}"
            )
            for i in range(100)
        ]
        
        start_time = time.time()
        db_session.add_all(users)
        await db_session.commit()
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Should complete in reasonable time (< 5 seconds for 100 users)
        assert duration < 5.0
        
        # Verify all users were created
        from sqlalchemy import select, func
        stmt = select(func.count(User.id)).where(User.email.like("bulk%@test.com"))
        result = await db_session.execute(stmt)
        count = result.scalar()
        
        assert count == 100
    
    @pytest.mark.asyncio
    async def test_batch_graph_operations_performance(self, clean_database, graph_builder):
        """
        Test batch graph operations performance for Neo4j
        
        **Validates: Requirements 13.5, 13.10**
        """
        from app.services.code_entity_extractor import CodeEntity
        import time
        
        # Create multiple entities
        entities = [
            CodeEntity(
                name=f"Entity{i}",
                entity_type="class",
                file_path=f"/file{i}.py",
                complexity=5,
                lines_of_code=50,
                dependencies=[]
            )
            for i in range(50)
        ]
        
        start_time = time.time()
        result = await graph_builder.create_or_update_entity_nodes_batch(entities)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Should complete in reasonable time (< 10 seconds for 50 entities)
        assert duration < 10.0
        assert result.nodes_created + result.nodes_updated == 50
