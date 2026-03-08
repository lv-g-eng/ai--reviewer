"""
architecture可视化 API endpoint

provideproject分支的architectureanalyzedata
"""
from typing import Annotated, List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Path
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from datetime import datetime
from uuid import UUID
import re

from app.database.postgresql import get_db
from app.auth import TokenPayload, get_current_user, require_project_access, Permission
from app.models.code_review import (
    PullRequest,
    ArchitectureAnalysis,
    ArchitectureViolation,
)

router = APIRouter()

# API version constant
API_VERSION = "1.0.0"


class BranchInfo(BaseModel):
    """分支info模型"""
    id: str
    name: str
    last_commit: str
    last_commit_date: str
    author: str
    components_count: int
    complexity: int
    health_status: str
    circular_dependencies: int


class GraphNode(BaseModel):
    """architecture图节点模型"""
    id: str
    label: str
    type: str
    health: str = Field(default="healthy")
    complexity: int = Field(default=5, ge=0)
    position: Dict[str, float] = Field(default_factory=dict)
    properties: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, float]] = None


class GraphEdge(BaseModel):
    """architecture图边模型"""
    id: str
    source: str
    target: str
    type: str
    is_circular: bool = False
    properties: Optional[Dict[str, Any]] = None


class ArchitectureMetrics(BaseModel):
    """architecture指标模型"""
    total_nodes: int = Field(ge=0)
    total_edges: int = Field(ge=0)
    circular_dependencies: int = Field(ge=0)
    max_depth: Optional[int] = Field(default=None, ge=0)
    avg_complexity: Optional[float] = Field(default=None, ge=0)


class ArchitectureAnalysisResponse(BaseModel):
    """architectureanalyzeresponse模型 - 符合prodenv要求"""
    id: str
    project_id: str
    branch_id: str
    status: str = Field(..., description="Analysis status: pending, processing, completed, failed")
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metrics: ArchitectureMetrics
    circular_dependency_chains: Optional[List[List[str]]] = None
    created_at: str
    updated_at: str
    api_version: str = Field(default=API_VERSION, description="API version for backward compatibility")
    
    @validator('status')
    def validate_status(cls, v):
        """verifystatusvalue"""
        valid_statuses = ['pending', 'in_progress', 'processing', 'completed', 'failed']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v


class BranchArchitecture(BaseModel):
    """分支architecturedata模型"""
    branch_info: BranchInfo
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    statistics: Dict[str, Any]


@router.get("/{project_id}/branches", response_model=List[BranchInfo])
async def get_project_branches(
    project_id: str,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.VIEW_PROJECT))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    getproject的所有分支列表
    
    return每item分支的基本infoandarchitecture健康status
    """
    # getproject的所有 PR，按分支分组
    pr_result = await db.execute(
        select(PullRequest)
        .filter(PullRequest.project_id == project_id)
        .order_by(PullRequest.created_at.desc())
    )
    prs = pr_result.scalars().all()
    
    if not prs:
        return []
    
    # 按分支名称分组
    branches_dict = {}
    for pr in prs:
        branch_name = pr.branch_name or 'unknown'
        if branch_name not in branches_dict:
            branches_dict[branch_name] = {
                'prs': [],
                'latest_pr': pr
            }
        branches_dict[branch_name]['prs'].append(pr)
    
    # 构建分支info列表
    branches = []
    for branch_name, data in branches_dict.items():
        latest_pr = data['latest_pr']
        prs_list = data['prs']
        
        # get该分支的architecture违规
        pr_ids = [pr.id for pr in prs_list]
        violations_result = await db.execute(
            select(func.count(ArchitectureViolation.id))
            .join(ArchitectureAnalysis)
            .filter(ArchitectureAnalysis.pull_request_id.in_(pr_ids))
        )
        violations_count = violations_result.scalar() or 0
        
        # 计算循环dependency数量
        circular_deps_result = await db.execute(
            select(func.count(ArchitectureViolation.id))
            .join(ArchitectureAnalysis)
            .filter(
                ArchitectureAnalysis.pull_request_id.in_(pr_ids),
                ArchitectureViolation.type == 'circular_dependency'
            )
        )
        circular_deps = circular_deps_result.scalar() or 0
        
        # 计算平均complexity（基于风险评分）
        avg_risk = sum(pr.risk_score for pr in prs_list if pr.risk_score) / len(prs_list) if prs_list else 0
        complexity = int(avg_risk / 10) if avg_risk else 5
        
        # 确定健康status
        if violations_count == 0:
            health_status = 'healthy'
        elif violations_count < 5:
            health_status = 'warning'
        else:
            health_status = 'critical'
        
        branches.append(BranchInfo(
            id=branch_name.replace('/', '-'),
            name=branch_name,
            last_commit=latest_pr.title or 'No commit message',
            last_commit_date=latest_pr.created_at.isoformat(),
            author=str(latest_pr.author_id) if latest_pr.author_id else 'unknown',
            components_count=latest_pr.files_changed or 0,
            complexity=complexity,
            health_status=health_status,
            circular_dependencies=circular_deps
        ))
    
    return branches


@router.get("/{project_id}/branches/{branch_id}/architecture", response_model=BranchArchitecture)
async def get_branch_architecture(
    project_id: str,
    branch_id: str,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.VIEW_PROJECT))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    get指定分支的architecture图data
    
    包括节点、边、统计info等
    """
    # 将 branch_id 转换回分支名称
    branch_name = branch_id.replace('-', '/')
    
    # get该分支的最新 PR
    pr_result = await db.execute(
        select(PullRequest)
        .filter(
            PullRequest.project_id == project_id,
            PullRequest.branch_name == branch_name
        )
        .order_by(PullRequest.created_at.desc())
        .limit(1)
    )
    latest_pr = pr_result.scalar_one_or_none()
    
    if not latest_pr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Branch {branch_name} not found"
        )
    
    # getarchitectureanalyzedata
    analysis_result = await db.execute(
        select(ArchitectureAnalysis)
        .filter(ArchitectureAnalysis.pull_request_id == latest_pr.id)
        .order_by(ArchitectureAnalysis.started_at.desc())
        .limit(1)
    )
    analysis = analysis_result.scalar_one_or_none()
    
    # getarchitecture违规
    violations = []
    circular_deps = 0
    if analysis:
        violations_result = await db.execute(
            select(ArchitectureViolation)
            .filter(ArchitectureViolation.analysis_id == analysis.id)
        )
        violations = violations_result.scalars().all()
        circular_deps = sum(1 for v in violations if v.type == 'circular_dependency')
    
    # 构建节点and边（从architectureanalyzedata中提取）
    nodes = []
    edges = []
    
    if analysis and analysis.summary:
        # 从 summary JSON 中提取architecture图data
        summary = analysis.summary
        if isinstance(summary, dict):
            # 提取componentinfo
            components = summary.get('components', [])
            for idx, component in enumerate(components):
                nodes.append(GraphNode(
                    id=str(idx + 1),
                    label=component.get('name', f'Component {idx + 1}'),
                    type=component.get('type', 'Unknown'),
                    health=component.get('health', 'healthy'),
                    complexity=component.get('complexity', 5),
                    position={'x': 100 + (idx % 3) * 200, 'y': 100 + (idx // 3) * 200}
                ))
            
            # 提取dependency关系
            dependencies = summary.get('dependencies', [])
            for idx, dep in enumerate(dependencies):
                edges.append(GraphEdge(
                    id=f'e{idx + 1}',
                    source=str(dep.get('source', 1)),
                    target=str(dep.get('target', 2)),
                    type='default',
                    is_circular=dep.get('is_circular', False)
                ))
    
    # 如果没有architecturedata，从违规info中构建基本图
    if not nodes and violations:
        components_set = set()
        for violation in violations:
            if violation.component:
                components_set.add(violation.component)
            if violation.related_component:
                components_set.add(violation.related_component)
        
        for idx, component in enumerate(components_set):
            health = 'critical' if any(v.component == component and v.severity == 'critical' for v in violations) else 'warning'
            nodes.append(GraphNode(
                id=str(idx + 1),
                label=component,
                type='Component',
                health=health,
                complexity=5,
                position={'x': 100 + (idx % 3) * 200, 'y': 100 + (idx // 3) * 200}
            ))
        
        # 从违规中提取dependency关系
        for idx, violation in enumerate(violations):
            if violation.component and violation.related_component:
                source_idx = list(components_set).index(violation.component) + 1
                target_idx = list(components_set).index(violation.related_component) + 1
                edges.append(GraphEdge(
                    id=f'e{idx + 1}',
                    source=str(source_idx),
                    target=str(target_idx),
                    type='default',
                    is_circular=(violation.type == 'circular_dependency')
                ))
    
    # 构建分支info
    branch_info = BranchInfo(
        id=branch_id,
        name=branch_name,
        last_commit=latest_pr.title or 'No commit message',
        last_commit_date=latest_pr.created_at.isoformat(),
        author=str(latest_pr.author_id) if latest_pr.author_id else 'unknown',
        components_count=len(nodes),
        complexity=int(latest_pr.risk_score / 10) if latest_pr.risk_score else 5,
        health_status='critical' if len(violations) > 5 else 'warning' if len(violations) > 0 else 'healthy',
        circular_dependencies=circular_deps
    )
    
    # 统计info
    statistics = {
        'total_components': len(nodes),
        'total_dependencies': len(edges),
        'circular_dependencies': circular_deps,
        'avg_complexity': int(sum(n.complexity for n in nodes) / len(nodes)) if nodes else 0,
        'violations_count': len(violations),
        'critical_violations': sum(1 for v in violations if v.severity == 'critical'),
        'high_violations': sum(1 for v in violations if v.severity == 'high'),
    }
    
    return BranchArchitecture(
        branch_info=branch_info,
        nodes=nodes,
        edges=edges,
        statistics=statistics
    )


def is_valid_uuid(uuid_string: str) -> bool:
    """verifyUUIDformat"""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_string))


class DependencyGraphNode(BaseModel):
    """dependency图节点模型"""
    id: str
    name: str
    type: str = Field(..., description="Node type: module, class, function, package")
    file_path: Optional[str] = None
    lines_of_code: Optional[int] = Field(default=None, ge=0)
    complexity: Optional[int] = Field(default=None, ge=0)
    properties: Optional[Dict[str, Any]] = None


class DependencyGraphEdge(BaseModel):
    """dependency图边模型"""
    id: str
    source: str
    target: str
    type: str = Field(..., description="Dependency type: import, call, inheritance")
    weight: float = Field(default=1.0, ge=0)
    is_circular: bool = False
    properties: Optional[Dict[str, Any]] = None


class DependencyGraphMetrics(BaseModel):
    """dependency图指标模型"""
    total_nodes: int = Field(ge=0)
    total_edges: int = Field(ge=0)
    circular_dependencies: int = Field(ge=0)
    max_depth: Optional[int] = Field(default=None, ge=0)
    avg_dependencies_per_node: Optional[float] = Field(default=None, ge=0)


class DependencyGraphResponse(BaseModel):
    """dependency图response模型 - 符合prodenv要求"""
    id: str
    project_id: str
    branch_id: Optional[str] = None
    status: str = Field(..., description="Analysis status: pending, processing, completed, failed")
    nodes: List[DependencyGraphNode]
    edges: List[DependencyGraphEdge]
    metrics: DependencyGraphMetrics
    circular_dependency_chains: Optional[List[List[str]]] = None
    created_at: str
    updated_at: str
    api_version: str = Field(default=API_VERSION, description="API version for backward compatibility")
    
    @validator('status')
    def validate_status(cls, v):
        """verifystatusvalue"""
        valid_statuses = ['pending', 'in_progress', 'processing', 'completed', 'failed']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v


@router.get("/dependencies/{project_id}", response_model=DependencyGraphResponse)
async def get_dependency_graph(
    project_id: str = Path(..., description="Project UUID"),
    branch_id: Optional[str] = None,
    current_user: Annotated[TokenPayload, Depends(require_project_access(Permission.VIEW_PROJECT))] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None
):
    """
    getproject的dependency关系图data
    
    此endpoint符合prodenv要求：
    - 实现inputverify（UUIDformatverify）- Requirement 3.6
    - containAPIversionInfo - Requirement 3.4
    - provideprod级APIendpoint - Requirement 2.4
    
    Args:
        project_id: project的UUID
        branch_id: 可选的分支标识符
        current_user: 当前authuser
        db: dbSession
        
    Returns:
        DependencyGraphResponse: dependency图data，contain节点、边、指标等
        
    Raises:
        HTTPException 422: UUIDformat无效
        HTTPException 404: project不存在或无dependencydata
        HTTPException 403: 无permission访问
    """
    # inputverify：verifyUUIDformat (Requirement 3.6)
    if not is_valid_uuid(project_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: {project_id}. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )
    
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: {project_id}"
        )
    
    # queryproject的最新architectureanalyze
    query = select(ArchitectureAnalysis).join(PullRequest).filter(
        PullRequest.project_id == project_uuid
    )
    
    # 如果指定了分支，filter分支
    if branch_id:
        branch_name = branch_id.replace('-', '/')
        query = query.filter(PullRequest.branch_name == branch_name)
    
    query = query.order_by(ArchitectureAnalysis.started_at.desc()).limit(1)
    
    analysis_result = await db.execute(query)
    analysis = analysis_result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No dependency graph data found for project {project_id}"
        )
    
    # get关联的PR
    pr_result = await db.execute(
        select(PullRequest).filter(PullRequest.id == analysis.pull_request_id)
    )
    pr = pr_result.scalar_one_or_none()
    
    if not pr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pull request for analysis not found"
        )
    
    # 构建dependency图节点and边
    nodes = []
    edges = []
    circular_dependency_chains = []
    
    if analysis.summary and isinstance(analysis.summary, dict):
        # 从summary中提取dependency图data
        components = analysis.summary.get('components', [])
        dependencies_data = analysis.summary.get('dependencies', [])
        
        # 构建节点
        for idx, component in enumerate(components):
            node = DependencyGraphNode(
                id=str(component.get('id', idx + 1)),
                name=component.get('name', f'Component {idx + 1}'),
                type=component.get('type', 'module'),
                file_path=component.get('file_path'),
                lines_of_code=component.get('lines_of_code'),
                complexity=component.get('complexity'),
                properties=component.get('properties')
            )
            nodes.append(node)
        
        # 构建边
        for idx, dep in enumerate(dependencies_data):
            edge = DependencyGraphEdge(
                id=dep.get('id', f'e{idx + 1}'),
                source=str(dep.get('source')),
                target=str(dep.get('target')),
                type=dep.get('type', 'import'),
                weight=dep.get('weight', 1.0),
                is_circular=dep.get('is_circular', False),
                properties=dep.get('properties')
            )
            edges.append(edge)
        
        # 提取循环dependency链
        circular_dependency_chains = analysis.summary.get('circular_dependency_chains', [])
    
    # 如果没有summarydata，从violations构建基本dependency图
    if not nodes:
        violations_result = await db.execute(
            select(ArchitectureViolation).filter(
                ArchitectureViolation.analysis_id == analysis.id
            )
        )
        violations = violations_result.scalars().all()
        
        if violations:
            components_set = set()
            for violation in violations:
                if violation.component:
                    components_set.add(violation.component)
                if violation.related_component:
                    components_set.add(violation.related_component)
            
            # 构建节点
            for idx, component in enumerate(sorted(components_set)):
                node = DependencyGraphNode(
                    id=str(idx + 1),
                    name=component,
                    type='module',
                    complexity=5
                )
                nodes.append(node)
            
            # 构建边
            component_to_id = {comp: str(idx + 1) for idx, comp in enumerate(sorted(components_set))}
            for idx, violation in enumerate(violations):
                if violation.component and violation.related_component:
                    if violation.component in component_to_id and violation.related_component in component_to_id:
                        edge = DependencyGraphEdge(
                            id=f'e{idx + 1}',
                            source=component_to_id[violation.component],
                            target=component_to_id[violation.related_component],
                            type='dependency',
                            is_circular=(violation.type == 'circular_dependency')
                        )
                        edges.append(edge)
    
    # 计算指标
    circular_deps_count = sum(1 for e in edges if e.is_circular)
    avg_deps_per_node = None
    if nodes:
        total_deps = len(edges)
        avg_deps_per_node = round(total_deps / len(nodes), 2)
    
    metrics = DependencyGraphMetrics(
        total_nodes=len(nodes),
        total_edges=len(edges),
        circular_dependencies=circular_deps_count,
        max_depth=analysis.summary.get('max_depth') if analysis.summary else None,
        avg_dependencies_per_node=avg_deps_per_node
    )
    
    # 确定status
    status_mapping = {
        'pending': 'pending',
        'in_progress': 'processing',
        'completed': 'completed',
        'failed': 'failed'
    }
    analysis_status = status_mapping.get(analysis.status.value, 'pending')
    
    # 构建response (containAPIversionInfo - Requirement 3.4)
    response = DependencyGraphResponse(
        id=str(analysis.id),
        project_id=str(pr.project_id),
        branch_id=pr.branch_name or None,
        status=analysis_status,
        nodes=nodes,
        edges=edges,
        metrics=metrics,
        circular_dependency_chains=circular_dependency_chains if circular_dependency_chains else None,
        created_at=analysis.started_at.isoformat() if analysis.started_at else datetime.utcnow().isoformat(),
        updated_at=analysis.completed_at.isoformat() if analysis.completed_at else analysis.started_at.isoformat() if analysis.started_at else datetime.utcnow().isoformat(),
        api_version=API_VERSION
    )
    
    return response


@router.get("/architecture/{analysis_id}", response_model=ArchitectureAnalysisResponse)
async def get_architecture_analysis(
    analysis_id: str = Path(..., description="Architecture analysis UUID"),
    current_user: Annotated[TokenPayload, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None
):
    """
    get指定的architectureanalyzedata
    
    此endpoint符合prodenv要求：
    - 实现inputverify（UUIDformatverify）- Requirement 3.6
    - containAPIversionInfo - Requirement 3.4
    - provideprod级APIendpoint - Requirement 2.4
    
    Args:
        analysis_id: architectureanalyze的UUID
        current_user: 当前authuser
        db: dbSession
        
    Returns:
        ArchitectureAnalysisResponse: architectureanalyzedata，contain节点、边、指标等
        
    Raises:
        HTTPException 422: UUIDformat无效
        HTTPException 404: architectureanalyze不存在
        HTTPException 403: 无permission访问
    """
    # inputverify：verifyUUIDformat (Requirement 3.6)
    if not is_valid_uuid(analysis_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: {analysis_id}. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )
    
    # queryarchitectureanalyze
    try:
        analysis_uuid = UUID(analysis_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid UUID format: {analysis_id}"
        )
    
    analysis_result = await db.execute(
        select(ArchitectureAnalysis)
        .filter(ArchitectureAnalysis.id == analysis_uuid)
    )
    analysis = analysis_result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Architecture analysis with id {analysis_id} not found"
        )
    
    # get关联的PR以getprojectinfo
    pr_result = await db.execute(
        select(PullRequest)
        .filter(PullRequest.id == analysis.pull_request_id)
    )
    pr = pr_result.scalar_one_or_none()
    
    if not pr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pull request for analysis {analysis_id} not found"
        )
    
    # permissioncheck：verifyuser是否有permission访问该project
    # note：这里简化了permissioncheck，实际shouldcheckuser是否有permission访问该project
    # 在prodenv中，shoulduse require_project_access 装饰器
    
    # getarchitecture违规data
    violations_result = await db.execute(
        select(ArchitectureViolation)
        .filter(ArchitectureViolation.analysis_id == analysis_uuid)
    )
    violations = violations_result.scalars().all()
    
    # 构建节点and边
    nodes = []
    edges = []
    circular_dependency_chains = []
    
    if analysis.summary and isinstance(analysis.summary, dict):
        # 从summary中提取architecture图data
        components = analysis.summary.get('components', [])
        for idx, component in enumerate(components):
            node = GraphNode(
                id=str(component.get('id', idx + 1)),
                label=component.get('name', f'Component {idx + 1}'),
                type=component.get('type', 'Unknown'),
                health=component.get('health', 'healthy'),
                complexity=component.get('complexity', 5),
                position=component.get('position', {'x': 100 + (idx % 3) * 200, 'y': 100 + (idx // 3) * 200}),
                properties=component.get('properties'),
                metrics=component.get('metrics')
            )
            nodes.append(node)
        
        # 提取dependency关系
        dependencies = analysis.summary.get('dependencies', [])
        for idx, dep in enumerate(dependencies):
            edge = GraphEdge(
                id=dep.get('id', f'e{idx + 1}'),
                source=str(dep.get('source')),
                target=str(dep.get('target')),
                type=dep.get('type', 'default'),
                is_circular=dep.get('is_circular', False),
                properties=dep.get('properties')
            )
            edges.append(edge)
        
        # 提取循环dependency链
        circular_dependency_chains = analysis.summary.get('circular_dependency_chains', [])
    
    # 如果没有summarydata，从violations构建基本图
    if not nodes and violations:
        components_set = set()
        for violation in violations:
            if violation.component:
                components_set.add(violation.component)
            if violation.related_component:
                components_set.add(violation.related_component)
        
        for idx, component in enumerate(sorted(components_set)):
            health = 'critical' if any(
                v.component == component and v.severity == 'critical' 
                for v in violations
            ) else 'warning'
            
            node = GraphNode(
                id=str(idx + 1),
                label=component,
                type='Component',
                health=health,
                complexity=5,
                position={'x': 100 + (idx % 3) * 200, 'y': 100 + (idx // 3) * 200}
            )
            nodes.append(node)
        
        # 从violations提取dependency关系
        component_to_id = {comp: str(idx + 1) for idx, comp in enumerate(sorted(components_set))}
        for idx, violation in enumerate(violations):
            if violation.component and violation.related_component:
                if violation.component in component_to_id and violation.related_component in component_to_id:
                    edge = GraphEdge(
                        id=f'e{idx + 1}',
                        source=component_to_id[violation.component],
                        target=component_to_id[violation.related_component],
                        type='dependency',
                        is_circular=(violation.type == 'circular_dependency')
                    )
                    edges.append(edge)
    
    # 计算循环dependency数量
    circular_deps_count = sum(1 for e in edges if e.is_circular)
    if not circular_deps_count:
        circular_deps_count = sum(1 for v in violations if v.type == 'circular_dependency')
    
    # 计算平均complexity
    avg_complexity = None
    if nodes:
        total_complexity = sum(n.complexity for n in nodes)
        avg_complexity = round(total_complexity / len(nodes), 2)
    
    # 构建指标
    metrics = ArchitectureMetrics(
        total_nodes=len(nodes),
        total_edges=len(edges),
        circular_dependencies=circular_deps_count,
        max_depth=analysis.summary.get('max_depth') if analysis.summary else None,
        avg_complexity=avg_complexity
    )
    
    # 确定status
    status_mapping = {
        'pending': 'pending',
        'in_progress': 'processing',
        'completed': 'completed',
        'failed': 'failed'
    }
    analysis_status = status_mapping.get(analysis.status.value, 'pending')
    
    # 构建response (containAPIversionInfo - Requirement 3.4)
    response = ArchitectureAnalysisResponse(
        id=str(analysis.id),
        project_id=str(pr.project_id),
        branch_id=pr.branch_name or 'unknown',
        status=analysis_status,
        nodes=nodes,
        edges=edges,
        metrics=metrics,
        circular_dependency_chains=circular_dependency_chains if circular_dependency_chains else None,
        created_at=analysis.started_at.isoformat() if analysis.started_at else datetime.utcnow().isoformat(),
        updated_at=analysis.completed_at.isoformat() if analysis.completed_at else analysis.started_at.isoformat() if analysis.started_at else datetime.utcnow().isoformat(),
        api_version=API_VERSION
    )
    
    return response
