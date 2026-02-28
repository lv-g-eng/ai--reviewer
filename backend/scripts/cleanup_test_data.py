"""
Cleanup Test Data Script

This script removes test data from the staging database to ensure
clean state for end-to-end tests.

Usage:
    python backend/scripts/cleanup_test_data.py
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.postgresql import AsyncSessionLocal
from app.models import Project, PullRequest, CodeEntity, User
from app.services.graph_builder.service import GraphBuilderService
from sqlalchemy import select, delete


async def cleanup_test_projects():
    """Remove test projects and related data"""
    async with AsyncSessionLocal() as db:
        # Find test projects (those with 'test' or 'e2e' in name/url)
        result = await db.execute(
            select(Project).where(
                (Project.name.ilike('%test%')) |
                (Project.name.ilike('%e2e%')) |
                (Project.github_repo_url.ilike('%test%')) |
                (Project.github_repo_url.ilike('%e2e%'))
            )
        )
        test_projects = result.scalars().all()
        
        if not test_projects:
            print("No test projects found to clean up")
            return
        
        print(f"Found {len(test_projects)} test projects to clean up")
        
        for project in test_projects:
            print(f"  Cleaning project: {project.name} (ID: {project.id})")
            
            # Delete code entities
            await db.execute(
                delete(CodeEntity).where(CodeEntity.project_id == project.id)
            )
            
            # Delete pull requests
            await db.execute(
                delete(PullRequest).where(PullRequest.project_id == project.id)
            )
            
            # Delete from Neo4j
            try:
                graph_service = GraphBuilderService()
                await graph_service.delete_project_graph(project.id)
                await graph_service.close()
                print(f"    ✓ Deleted Neo4j graph data")
            except Exception as e:
                print(f"    ⚠ Warning: Could not delete Neo4j data: {e}")
            
            # Delete project
            await db.delete(project)
            print(f"    ✓ Deleted project and related data")
        
        await db.commit()
        print(f"\n✓ Cleaned up {len(test_projects)} test projects")


async def cleanup_test_users():
    """Remove test users"""
    async with AsyncSessionLocal() as db:
        # Find test users
        result = await db.execute(
            select(User).where(
                (User.email.ilike('%test%')) |
                (User.email.ilike('%e2e%')) |
                (User.username.ilike('%test%')) |
                (User.username.ilike('%e2e%'))
            )
        )
        test_users = result.scalars().all()
        
        if not test_users:
            print("No test users found to clean up")
            return
        
        print(f"Found {len(test_users)} test users to clean up")
        
        for user in test_users:
            print(f"  Cleaning user: {user.email} (ID: {user.id})")
            await db.delete(user)
        
        await db.commit()
        print(f"✓ Cleaned up {len(test_users)} test users")


async def cleanup_orphaned_data():
    """Remove orphaned data (entities without projects, etc.)"""
    async with AsyncSessionLocal() as db:
        # Find orphaned code entities
        result = await db.execute(
            select(CodeEntity).where(
                ~CodeEntity.project_id.in_(
                    select(Project.id)
                )
            )
        )
        orphaned_entities = result.scalars().all()
        
        if orphaned_entities:
            print(f"Found {len(orphaned_entities)} orphaned code entities")
            for entity in orphaned_entities:
                await db.delete(entity)
            await db.commit()
            print(f"✓ Cleaned up {len(orphaned_entities)} orphaned entities")
        
        # Find orphaned pull requests
        result = await db.execute(
            select(PullRequest).where(
                ~PullRequest.project_id.in_(
                    select(Project.id)
                )
            )
        )
        orphaned_prs = result.scalars().all()
        
        if orphaned_prs:
            print(f"Found {len(orphaned_prs)} orphaned pull requests")
            for pr in orphaned_prs:
                await db.delete(pr)
            await db.commit()
            print(f"✓ Cleaned up {len(orphaned_prs)} orphaned PRs")


async def main():
    """Main cleanup function"""
    print("=" * 60)
    print("Cleaning Up Test Data")
    print("=" * 60)
    print()
    
    try:
        # Cleanup test projects
        await cleanup_test_projects()
        print()
        
        # Cleanup test users
        await cleanup_test_users()
        print()
        
        # Cleanup orphaned data
        await cleanup_orphaned_data()
        print()
        
        print("=" * 60)
        print("✓ Cleanup Complete")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
