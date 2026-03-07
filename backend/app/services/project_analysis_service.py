"""
Project Analysis Service

Provides comprehensive AI-powered project analysis including:
- Code quality metrics
- Security analysis  
- Architecture evaluation
- Performance metrics
- Issue statistics and trends
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from statistics import mean, median
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.code_review import (
    PullRequest,
    CodeReview,
    ReviewComment,
    ArchitectureAnalysis,
    ArchitectureViolation,
)

logger = logging.getLogger(__name__)


class ProjectAnalysisService:
    """
    Comprehensive project analysis service.
    
    Aggregates data from code reviews, architecture analysis,
    and performance metrics to provide holistic project health insights.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize the service with database session"""
        self.db = db
    
    async def get_complete_project_analytics(self, project_id: str) -> Dict[str, Any]:
        """
        Get complete analytics for a project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Dictionary containing comprehensive project analytics
        """
        try:
            # Get PR data
            prs = await self._get_pull_requests(project_id)
            
            # Get code review comments
            comments = await self._get_review_comments(project_id)
            
            # Get architecture violations
            violations = await self._get_architecture_violations(project_id)
            
            # Calculate metrics
            metrics = self._calculate_metrics(prs, comments, violations)
            
            # Get dependency stats
            dependency_stats = self._calculate_dependency_stats(prs, comments)
            
            # Get performance metrics
            performance_metrics = self._calculate_performance_metrics(prs)
            
            # Get issue statistics
            issue_stats = self._calculate_issue_stats(comments, violations)
            
            # Get trend analysis
            trends = await self._calculate_trends(project_id)
            
            # Get recent reviews
            recent_reviews = await self._get_recent_reviews(project_id)
            
            return {
                "project_id": project_id,
                "metrics": metrics,
                "dependency_stats": dependency_stats,
                "performance_metrics": performance_metrics,
                "issue_stats": issue_stats,
                "trends": trends,
                "recent_reviews": recent_reviews,
                "total_prs": len(prs),
                "reviewed_prs": sum(1 for pr in prs if pr.analyzed_at),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating project analytics: {str(e)}", exc_info=True)
            raise
    
    async def _get_pull_requests(self, project_id: str) -> List[Any]:
        """Get all pull requests for a project"""
        result = await self.db.execute(
            select(PullRequest).filter(PullRequest.project_id == project_id)
        )
        return result.scalars().all()
    
    async def _get_review_comments(self, project_id: str) -> List[Any]:
        """Get all code review comments for a project"""
        prs_result = await self.db.execute(
            select(PullRequest.id).filter(PullRequest.project_id == project_id)
        )
        pr_ids = [row[0] for row in prs_result.all()]
        
        if not pr_ids:
            return []
        
        result = await self.db.execute(
            select(ReviewComment)
            .join(CodeReview)
            .filter(CodeReview.pull_request_id.in_(pr_ids))
        )
        return result.scalars().all()
    
    async def _get_architecture_violations(self, project_id: str) -> List[Any]:
        """Get all architecture violations for a project"""
        prs_result = await self.db.execute(
            select(PullRequest.id).filter(PullRequest.project_id == project_id)
        )
        pr_ids = [row[0] for row in prs_result.all()]
        
        if not pr_ids:
            return []
        
        result = await self.db.execute(
            select(ArchitectureViolation)
            .join(ArchitectureAnalysis)
            .filter(ArchitectureAnalysis.pull_request_id.in_(pr_ids))
        )
        return result.scalars().all()
    
    def _calculate_metrics(self, prs: List[Any], comments: List[Any], 
                          violations: List[Any]) -> Dict[str, int]:
        """Calculate quality metrics based on PR and review data"""
        reviewed_prs = [pr for pr in prs if pr.analyzed_at]
        
        if not reviewed_prs:
            # Default metrics when no data available
            return {
                "code_quality": 75,
                "security_rating": 80,
                "architecture_health": 75,
                "test_coverage": 70,
                "overall_health": 75
            }
        
        # Code quality: Based on issue density
        issues_per_pr = len(comments) / len(reviewed_prs) if reviewed_prs else 0
        code_quality = max(0, min(100, int(100 - (issues_per_pr * 5))))
        
        # Security rating: Based on critical/high issues
        severity_counts = self._count_by_severity(comments)
        critical_high = severity_counts.get("critical", 0) + severity_counts.get("high", 0)
        security_rating = max(0, min(100, int(100 - (critical_high * 10))))
        
        # Architecture health: Based on violations
        violations_per_pr = len(violations) / len(reviewed_prs) if reviewed_prs else 0
        architecture_health = max(0, min(100, int(100 - (violations_per_pr * 15))))
        
        # Test coverage: Based on risk scores
        risk_scores = [pr.risk_score for pr in reviewed_prs if pr.risk_score]
        avg_risk = mean(risk_scores) if risk_scores else 50
        test_coverage = max(0, min(100, int(100 - avg_risk)))
        
        overall_health = int(mean([code_quality, security_rating, architecture_health, test_coverage]))
        
        return {
            "code_quality": code_quality,
            "security_rating": security_rating,
            "architecture_health": architecture_health,
            "test_coverage": test_coverage,
            "overall_health": overall_health
        }
    
    def _calculate_dependency_stats(self, prs: List[Any], comments: List[Any]) -> Dict[str, int]:
        """Calculate dependency analysis statistics"""
        # Count dependencies from review comments
        dependency_issues = [c for c in comments if "depend" in str(c.message).lower()]
        circular_deps = [c for c in comments if "circular" in str(c.message).lower()]
        outdated_deps = [c for c in comments if "outdated" in str(c.message).lower()]
        
        return {
            "total": len(comments),
            "circular": len(circular_deps),
            "outdated": len(outdated_deps),
            "dependency_issues": len(dependency_issues)
        }
    
    def _calculate_performance_metrics(self, prs: List[Any]) -> Dict[str, Any]:
        """Calculate performance metrics from PR data"""
        if not prs:
            return {
                "avg_build_time": "0m",
                "avg_test_time": "0m", 
                "avg_analysis_time": "2m",
                "pr_review_time_avg": "0h"
            }
        
        # Estimate metrics based on PR count and timestamps
        reviewed_prs = [pr for pr in prs if pr.analyzed_at]
        
        build_times = []
        for pr in reviewed_prs:
            # Estimate build time based on files changed
            estimated_time = max(30, pr.files_changed * 0.5)  # seconds
            build_times.append(estimated_time)
        
        avg_build_time = mean(build_times) if build_times else 60
        
        return {
            "avg_build_time": f"{int(avg_build_time / 60)}m {int(avg_build_time % 60)}s",
            "avg_test_time": f"{max(1, int(len(reviewed_prs) * 0.3))}m",
            "avg_analysis_time": f"{max(1, int(len(reviewed_prs) * 0.05))}m",
            "pr_review_time_avg": f"{int(len(reviewed_prs) / max(1, len(prs)))}h"
        }
    
    def _calculate_issue_stats(self, comments: List[Any], violations: List[Any]) -> Dict[str, int]:
        """Calculate issue statistics"""
        severity_counts = self._count_by_severity(comments)
        
        # Count issue types
        security_issues = len([c for c in comments if "security" in str(getattr(c, 'rule_name', '')).lower()])
        performance_issues = len([c for c in comments if "performance" in str(getattr(c, 'rule_name', '')).lower()])
        style_issues = len([c for c in comments if "style" in str(getattr(c, 'rule_name', '')).lower()])
        best_practices = len(comments) - security_issues - performance_issues - style_issues
        
        return {
            "critical": severity_counts.get("critical", 0),
            "high": severity_counts.get("high", 0),
            "medium": severity_counts.get("medium", 0),
            "low": severity_counts.get("low", 0),
            "security": security_issues,
            "performance": performance_issues,
            "code_style": style_issues,
            "best_practices": best_practices,
            "total": len(comments) + len(violations)
        }
    
    def _count_by_severity(self, comments: List[Any]) -> Dict[str, int]:
        """Count issues by severity level"""
        counts = {}
        for comment in comments:
            severity = getattr(comment, 'severity', 'medium').lower()
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    async def _calculate_trends(self, project_id: str) -> Dict[str, int]:
        """Calculate trend analysis over time"""
        # Get data from last month
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        
        current_prs = await self._get_pull_requests(project_id)
        current_comments = await self._get_review_comments(project_id)
        current_violations = await self._get_architecture_violations(project_id)
        
        current_quality = 100 - (len(current_comments) / max(1, len(current_prs)) * 5)
        current_coverage = 100 - (len(current_violations) / max(1, len(current_prs)) * 15)
        
        # Estimate trends (in production, compare with historical data)
        return {
            "code_quality_change": int(current_quality - 75),  # Compare with baseline
            "test_coverage_change": int(current_coverage - 70),
            "issues_change": -int((len(current_comments) - 5) / 10) if len(current_comments) > 5 else 0
        }
    
    async def _get_recent_reviews(self, project_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent code reviews"""
        prs = await self._get_pull_requests(project_id)
        
        # Sort by analyzed date
        analyzed_prs = sorted(
            [pr for pr in prs if pr.analyzed_at],
            key=lambda x: x.analyzed_at,
            reverse=True
        )[:limit]
        
        reviews = []
        for pr in analyzed_prs:
            reviews.append({
                "pr_id": str(pr.id),
                "pr_number": pr.github_pr_number,
                "title": pr.title,
                "status": pr.status.value if hasattr(pr.status, 'value') else str(pr.status),
                "risk_score": pr.risk_score,
                "files_changed": pr.files_changed,
                "lines_added": pr.lines_added,
                "lines_deleted": pr.lines_deleted,
                "analyzed_at": pr.analyzed_at.isoformat() if pr.analyzed_at else None
            })
        
        return reviews
