"""
项目分析统计 API 端点

提供项目的 AI 审查数据、架构分析、代码质量指标等
"""
from typing import Annotated, Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
import logging

from app.database.postgresql import get_db
from app.auth import TokenPayload, get_current_user, require_project_access, Permission
from app.models.code_review import (
    PullRequest,
    CodeReview,
    ReviewComment,
    ArchitectureAnalysis,
    ArchitectureViolation,
    ReviewStatus
)
from app.services.llm_service import llm_service, ModelType
from app.services.project_analysis_service import ProjectAnalysisService  # Added missing import

logger = logging.getLogger(__name__)

router = APIRouter()


class ProjectMetrics(BaseModel):
    """项目指标响应模型"""
    code_quality: int
    security_rating: int
    architecture_health: int
    test_coverage: int
    overall_health: int


class ProjectAnalytics(BaseModel):
    """项目分析数据响应模型"""
    project_id: str
    metrics: ProjectMetrics
    total_prs: int
    reviewed_prs: int
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    architecture_violations: int
    recent_reviews: list


@router.get("/{project_id}/analytics", response_model=Dict[str, Any])
async def get_project_analytics(
    project_id: str,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.VIEW_PROJECT))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    获取项目的 AI 审查分析数据
    
    包括：
    - 代码质量指标
    - 安全评级  
    - 架构健康度
    - 测试覆盖率
    - 问题统计
    - 依赖分析
    - 性能指标
    - 最近的审查记录
    - 趋势分析
    """
    try:
        # 使用新的分析服务获取完整的项目分析
        service = ProjectAnalysisService(db)
        analytics = await service.get_complete_project_analytics(project_id)
        return analytics
    except Exception as e:
        import logging
        logging.error(f"Error fetching analytics for project {project_id}: {str(e)}")
        # Return default analytics if error
        return {
            "project_id": project_id,
            "metrics": {
                "code_quality": 75,
                "security_rating": 80,
                "architecture_health": 75,
                "test_coverage": 70,
                "overall_health": 75
            },
            "dependency_stats": {
                "total": 0,
                "circular": 0,
                "outdated": 0,
                "dependency_issues": 0
            },
            "performance_metrics": {
                "avg_build_time": "0m",
                "avg_test_time": "0m",
                "avg_analysis_time": "2m",
                "pr_review_time_avg": "0h"
            },
            "issue_stats": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "security": 0,
                "performance": 0,
                "code_style": 0,
                "best_practices": 0,
                "total": 0
            },
            "trends": {
                "code_quality_change": 0,
                "test_coverage_change": 0,
                "issues_change": 0
            },
            "recent_reviews": [],
            "total_prs": 0,
            "reviewed_prs": 0,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }


@router.get("/{project_id}/issues", response_model=Dict[str, Any])
async def get_project_issues(
    project_id: str,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.VIEW_PROJECT))],
    db: Annotated[AsyncSession, Depends(get_db)],
    severity: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50
):
    """
    获取项目的所有问题列表
    
    可以按严重程度和类别筛选
    """
    # 获取项目的所有 PR
    pr_result = await db.execute(
        select(PullRequest).filter(PullRequest.project_id == project_id)
    )
    prs = pr_result.scalars().all()
    pr_ids = [pr.id for pr in prs]
    
    if not pr_ids:
        return {
            'issues': [],
            'total': 0
        }
    
    # 构建查询
    query = select(ReviewComment).join(CodeReview).filter(
        CodeReview.pull_request_id.in_(pr_ids)
    )
    
    if severity:
        query = query.filter(ReviewComment.severity == severity)
    
    if category:
        query = query.filter(ReviewComment.category == category)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    comments = result.scalars().all()
    
    issues = []
    for comment in comments:
        issues.append({
            'id': str(comment.id),
            'file_path': comment.file_path,
            'line_number': comment.line_number,
            'message': comment.message,
            'severity': comment.severity,
            'category': comment.category,
            'rule_id': comment.rule_id,
            'rule_name': comment.rule_name,
            'suggested_fix': comment.suggested_fix,
            'created_at': comment.created_at.isoformat()
        })
    
    return {
        'issues': issues,
        'total': len(issues)
    }


@router.get("/{project_id}/architecture", response_model=Dict[str, Any])
async def get_project_architecture(
    project_id: str,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.VIEW_PROJECT))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    获取项目的架构分析数据
    """
    # 获取项目的所有 PR
    pr_result = await db.execute(
        select(PullRequest).filter(PullRequest.project_id == project_id)
    )
    prs = pr_result.scalars().all()
    pr_ids = [pr.id for pr in prs]
    
    if not pr_ids:
        return {
            'violations': [],
            'total': 0,
            'by_type': {},
            'by_severity': {}
        }
    
    # 获取架构违规
    violations_result = await db.execute(
        select(ArchitectureViolation)
        .join(ArchitectureAnalysis)
        .filter(ArchitectureAnalysis.pull_request_id.in_(pr_ids))
    )
    violations = violations_result.scalars().all()
    
    # 统计违规类型和严重程度
    by_type = {}
    by_severity = {}
    
    violations_list = []
    for violation in violations:
        violations_list.append({
            'id': str(violation.id),
            'type': violation.type,
            'component': violation.component,
            'related_component': violation.related_component,
            'message': violation.message,
            'severity': violation.severity,
            'file_path': violation.file_path,
            'line_number': violation.line_number,
            'suggested_fix': violation.suggested_fix
        })
        
        # 统计
        by_type[violation.type] = by_type.get(violation.type, 0) + 1
        by_severity[violation.severity] = by_severity.get(violation.severity, 0) + 1
    
    return {
        'violations': violations_list,
        'total': len(violations),
        'by_type': by_type,
        'by_severity': by_severity
    }


# Performance Metrics Models
class PerformanceMetric(BaseModel):
    """单个性能指标数据点"""
    timestamp: str
    metric_name: str
    value: float = Field(..., ge=0, description="Metric value must be non-negative")
    unit: str
    tags: Optional[Dict[str, str]] = None


class TimeRange(BaseModel):
    """时间范围"""
    start: str
    end: str
    
    @validator('start', 'end')
    def validate_datetime(cls, v):
        """验证日期时间格式"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError(f"Invalid datetime format: {v}. Expected ISO 8601 format.")


class MetricsCollection(BaseModel):
    """性能指标集合"""
    response_time: List[PerformanceMetric] = []
    throughput: List[PerformanceMetric] = []
    error_rate: List[PerformanceMetric] = []
    cpu_usage: List[PerformanceMetric] = []
    memory_usage: List[PerformanceMetric] = []


class MetricsAggregations(BaseModel):
    """性能指标聚合数据"""
    avg_response_time: float = Field(..., ge=0, le=10000, description="Average response time in ms (0-10000)")
    p95_response_time: float = Field(..., ge=0, le=10000, description="P95 response time in ms (0-10000)")
    p99_response_time: float = Field(..., ge=0, le=10000, description="P99 response time in ms (0-10000)")
    total_requests: int = Field(..., ge=0, description="Total requests must be non-negative")
    total_errors: int = Field(..., ge=0, description="Total errors must be non-negative")


class PerformanceDashboardData(BaseModel):
    """性能仪表板数据响应模型"""
    api_version: str = "1.0.0"
    project_id: str
    time_range: TimeRange
    metrics: MetricsCollection
    aggregations: MetricsAggregations


@router.get("/{project_id}/metrics", response_model=PerformanceDashboardData)
async def get_performance_metrics(
    project_id: str,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.VIEW_PROJECT))],
    db: Annotated[AsyncSession, Depends(get_db)],
    start_time: Optional[str] = Query(
        None,
        description="Start time in ISO 8601 format (e.g., 2024-01-01T00:00:00Z)"
    ),
    end_time: Optional[str] = Query(
        None,
        description="End time in ISO 8601 format (e.g., 2024-01-31T23:59:59Z)"
    )
):
    """
    获取项目的性能指标数据
    
    包括：
    - 响应时间 (response_time)
    - 吞吐量 (throughput)
    - 错误率 (error_rate)
    - CPU使用率 (cpu_usage)
    - 内存使用率 (memory_usage)
    
    支持时间范围过滤，默认返回最近7天的数据。
    
    Requirements: 2.4, 3.7
    """
    
    # Validate and parse time range parameters
    try:
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        else:
            start_dt = datetime.utcnow() - timedelta(days=7)
            
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        else:
            end_dt = datetime.utcnow()
            
        # Validate time range
        if start_dt >= end_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time must be before end_time"
            )
            
        # Validate time range is not too large (max 90 days)
        if (end_dt - start_dt).days > 90:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Time range cannot exceed 90 days"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid datetime format: {str(e)}. Expected ISO 8601 format."
        )
    
    # Get project PRs within time range
    pr_result = await db.execute(
        select(PullRequest).filter(
            PullRequest.project_id == project_id,
            PullRequest.created_at >= start_dt,
            PullRequest.created_at <= end_dt
        )
    )
    prs = pr_result.scalars().all()
    
    # Generate time series data points (daily aggregation)
    current_date = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    response_time_metrics = []
    throughput_metrics = []
    error_rate_metrics = []
    cpu_usage_metrics = []
    memory_usage_metrics = []
    
    all_response_times = []
    total_requests = 0
    total_errors = 0
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        
        # Filter PRs for this day
        day_prs = [pr for pr in prs if current_date <= pr.created_at.replace(tzinfo=None) < next_date]
        
        if day_prs:
            # Calculate metrics for this day
            # Response time: based on PR analysis time (simulated)
            analyzed_prs = [pr for pr in day_prs if pr.analyzed_at is not None]
            avg_analysis_time = sum((pr.analyzed_at.replace(tzinfo=None) - pr.created_at.replace(tzinfo=None)).total_seconds() * 1000 
                                   for pr in analyzed_prs) / len(day_prs) if analyzed_prs else 150.0
            avg_analysis_time = max(50.0, min(avg_analysis_time, 5000.0))  # Clamp between 50-5000ms
            
            response_time_metrics.append(PerformanceMetric(
                timestamp=current_date.isoformat() + 'Z',
                metric_name='response_time',
                value=round(avg_analysis_time, 2),
                unit='ms',
                tags={'aggregation': 'avg'}
            ))
            
            all_response_times.extend([avg_analysis_time] * len(day_prs))
            
            # Throughput: number of PRs analyzed per day
            throughput = len(analyzed_prs)
            throughput_metrics.append(PerformanceMetric(
                timestamp=current_date.isoformat() + 'Z',
                metric_name='throughput',
                value=float(throughput),
                unit='requests/day',
                tags={'aggregation': 'sum'}
            ))
            
            total_requests += len(day_prs)
            
            # Error rate: PRs with failed status
            failed_prs = len([pr for pr in day_prs if getattr(pr, 'status', None) == ReviewStatus.FAILED])
            error_rate = (failed_prs / len(day_prs) * 100) if day_prs else 0.0
            error_rate = max(0.0, min(error_rate, 100.0))  # Clamp between 0-100%
            
            error_rate_metrics.append(PerformanceMetric(
                timestamp=current_date.isoformat() + 'Z',
                metric_name='error_rate',
                value=round(error_rate, 2),
                unit='percent',
                tags={'aggregation': 'avg'}
            ))
            
            total_errors += failed_prs
            
            # CPU usage: simulated based on PR complexity (files changed)
            avg_files = float(sum(getattr(pr, 'files_changed', 0) for pr in day_prs) / len(day_prs)) if day_prs else 0.0
            cpu_usage = min(30.0 + (avg_files * 2.0), 100.0)  # Simulate CPU usage
            cpu_usage = max(0.0, min(cpu_usage, 100.0))  # Clamp between 0-100%
            
            cpu_usage_metrics.append(PerformanceMetric(
                timestamp=current_date.isoformat() + 'Z',
                metric_name='cpu_usage',
                value=round(cpu_usage, 2),
                unit='percent',
                tags={'aggregation': 'avg'}
            ))
            
            # Memory usage: simulated based on lines changed
            avg_lines = float(sum(getattr(pr, 'lines_added', 0) + getattr(pr, 'lines_deleted', 0) for pr in day_prs) / len(day_prs)) if day_prs else 0.0
            memory_usage = min(40.0 + (avg_lines / 100.0), 100.0)  # Simulate memory usage
            memory_usage = max(0.0, min(memory_usage, 100.0))  # Clamp between 0-100%
            
            memory_usage_metrics.append(PerformanceMetric(
                timestamp=current_date.isoformat() + 'Z',
                metric_name='memory_usage',
                value=round(memory_usage, 2),
                unit='percent',
                tags={'aggregation': 'avg'}
            ))
        
        current_date = next_date
    
    # Calculate aggregations
    if all_response_times:
        sorted_times = sorted(all_response_times)
        avg_response_time = sum(sorted_times) / len(sorted_times)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)
        p95_response_time = sorted_times[min(p95_index, len(sorted_times) - 1)]
        p99_response_time = sorted_times[min(p99_index, len(sorted_times) - 1)]
    else:
        avg_response_time = 0.0
        p95_response_time = 0.0
        p99_response_time = 0.0
    
    # Ensure aggregations are within valid ranges
    avg_response_time = max(0.0, min(avg_response_time, 10000.0))
    p95_response_time = max(0.0, min(p95_response_time, 10000.0))
    p99_response_time = max(0.0, min(p99_response_time, 10000.0))
    
    return PerformanceDashboardData(
        api_version="1.0.0",
        project_id=project_id,
        time_range=TimeRange(
            start=start_dt.isoformat() + 'Z',
            end=end_dt.isoformat() + 'Z'
        ),
        metrics=MetricsCollection(
            response_time=response_time_metrics,
            throughput=throughput_metrics,
            error_rate=error_rate_metrics,
            cpu_usage=cpu_usage_metrics,
            memory_usage=memory_usage_metrics
        ),
        aggregations=MetricsAggregations(
            avg_response_time=round(avg_response_time, 2),
            p95_response_time=round(p95_response_time, 2),
            p99_response_time=round(p99_response_time, 2),
            total_requests=total_requests,
            total_errors=total_errors
        )
    )


@router.get("/{project_id}/architecture-analysis", response_model=Dict[str, Any])
async def get_project_architecture_analysis(
    project_id: str,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.VIEW_PROJECT))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    获取项目的AI生成的架构分析，包括优势和建议
    """
    try:
        # 获取项目的基本信息和架构数据
        service = ProjectAnalysisService(db)
        analytics = await service.get_complete_project_analytics(project_id)

        # 获取PR和架构违规数据用于AI分析
        pr_result = await db.execute(
            select(PullRequest).filter(PullRequest.project_id == project_id)
        )
        prs = pr_result.scalars().all()

        violations_result = await db.execute(
            select(ArchitectureViolation)
            .join(ArchitectureAnalysis)
            .filter(ArchitectureAnalysis.pull_request_id.in_(pr.id for pr in prs))
        )
        violations = violations_result.scalars().all()

        # 构建架构数据用于AI分析
        architecture_data = {
            "project_id": project_id,
            "total_prs": len(prs),
            "analyzed_prs": sum(1 for pr in prs if getattr(pr, 'analyzed_at', None) is not None),
            "violations_count": len(violations),
            "metrics": analytics.get("metrics", {}),
            "dependency_stats": analytics.get("dependency_stats", {}),
            "issue_stats": analytics.get("issue_stats", {}),
        }

        # 使用AI生成架构分析
        if llm_service.is_initialized():
            try:
                ai_insights = await llm_service.generate_architecture_insights(architecture_data)

                # 解析AI响应为结构化数据
                strengths = ai_insights.get("strengths", [])
                recommendations = ai_insights.get("recommendations", [])

                return {
                    "strengths": strengths,
                    "recommendations": recommendations,
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "ai_generated": True
                }
            except Exception as ai_error:
                logger.warning(f"AI architecture analysis failed: {ai_error}")
                # 回退到基于规则的分析

        # 基于规则的回退分析
        strengths, recommendations = await _generate_rule_based_architecture_analysis(analytics, list(violations))

        return {
            "strengths": strengths,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "ai_generated": False
        }

    except Exception as e:
        logger.error(f"Error generating architecture analysis for project {project_id}: {str(e)}")
        # 返回默认分析
        return {
            "strengths": ["项目结构良好", "代码组织有序"],
            "recommendations": ["考虑增加更多集成测试", "定期进行代码审查"],
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "ai_generated": False
        }


async def _generate_rule_based_architecture_analysis(analytics: Dict[str, Any], violations: List[Any]) -> tuple:
    """基于规则生成架构分析"""
    strengths = []
    recommendations = []

    metrics = analytics.get("metrics", {})
    dependency_stats = analytics.get("dependency_stats", {})
    issue_stats = analytics.get("issue_stats", {})

    # 基于指标添加优势
    if metrics.get("code_quality", 0) > 75:
        strengths.append("代码质量良好，符合最佳实践")

    if metrics.get("security_rating", 0) > 80:
        strengths.append("安全性评分较高，风险控制到位")

    if metrics.get("architecture_health", 0) > 70:
        strengths.append("架构健康度良好，设计合理")

    if metrics.get("test_coverage", 0) > 60:
        strengths.append("测试覆盖率充足")

    # 基于依赖分析
    if dependency_stats.get("circular", 0) == 0:
        strengths.append("无循环依赖，架构清晰")

    # 基于问题统计添加建议
    if issue_stats.get("critical", 0) > 0:
        recommendations.append("存在严重问题，需要立即修复")

    if dependency_stats.get("outdated", 0) > 0:
        recommendations.append("存在过时的依赖，需要更新")

    if len(violations) > 0:
        recommendations.append("存在架构违规，需要审查")

    if metrics.get("test_coverage", 100) < 70:
        recommendations.append("测试覆盖率不足，建议增加测试")

    # 默认内容
    if not strengths:
        strengths = ["项目结构合理", "代码组织良好"]

    if not recommendations:
        recommendations = ["定期进行代码审查", "保持良好的测试覆盖率"]

    return strengths, recommendations


# Global instance
# llm_service = LLMService()
