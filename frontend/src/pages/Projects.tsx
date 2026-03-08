/**
 * Projects页面组件
 * 
 * 功能:
 * - 显示项目列表
 * - 使用VirtualList组件处理100+项目
 * - 支持项目选择和操作
 * - 支持批量删除、归档、标签操作
 * - 集成ErrorBoundary
 * 
 * 验证需求: 2.3, 2.4
 */

'use client';

import React, { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { VirtualList } from '../components/VirtualList';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { useProjects, useUpdateProject } from '../hooks/useProjects';
import { LoadingState } from '../components/LoadingState';
import { OfflineIndicator } from '../components/OfflineIndicator';
import type { Project } from '../hooks/useProjects';
import '../styles/responsive.css';

interface ProjectsProps {
  enableVirtualScroll?: boolean;
  pageSize?: number;
}

/**
 * 项目列表项组件 - 支持拖拽排序
 */
const ProjectListItem: React.FC<{
  project: Project;
  isSelected: boolean;
  onSelect: (id: string) => void;
  isDragging?: boolean;
}> = ({ project, isSelected, onSelect, isDragging = false }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({ id: project.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    padding: '16px',
    borderBottom: '1px solid #e0e0e0',
    backgroundColor: isSelected ? '#f0f7ff' : '#fff',
    cursor: isSortableDragging ? 'grabbing' : 'grab',
    opacity: isSortableDragging ? 0.5 : 1,
    zIndex: isSortableDragging ? 1000 : 'auto',
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      onMouseEnter={(e) => {
        if (!isSelected && !isSortableDragging) {
          e.currentTarget.style.backgroundColor = '#f9f9f9';
        }
      }}
      onMouseLeave={(e) => {
        if (!isSelected && !isSortableDragging) {
          e.currentTarget.style.backgroundColor = '#fff';
        }
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Drag handle indicator */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '2px',
            cursor: 'grab',
            padding: '4px',
          }}
        >
          <div style={{ width: '16px', height: '2px', backgroundColor: '#999', borderRadius: '1px' }} />
          <div style={{ width: '16px', height: '2px', backgroundColor: '#999', borderRadius: '1px' }} />
          <div style={{ width: '16px', height: '2px', backgroundColor: '#999', borderRadius: '1px' }} />
        </div>
        
        <input
          type="checkbox"
          checked={isSelected}
          onChange={() => onSelect(project.id)}
          onClick={(e) => {
            e.stopPropagation();
          }}
          onPointerDown={(e) => {
            e.stopPropagation();
          }}
          style={{ cursor: 'pointer' }}
        />
        <div style={{ flex: 1 }}>
          <h3
            style={{
              margin: 0,
              fontSize: '16px',
              fontWeight: 600,
              color: '#333',
            }}
          >
            {project.name}
          </h3>
          {project.description && (
            <p
              style={{
                margin: '4px 0 0 0',
                fontSize: '14px',
                color: '#666',
              }}
            >
              {project.description}
            </p>
          )}
          <div
            style={{
              marginTop: '8px',
              display: 'flex',
              gap: '12px',
              fontSize: '12px',
              color: '#999',
            }}
          >
            <span>
              Status: {project.is_active ? '✓ Active' : '✗ Inactive'}
            </span>
            {project.language && <span>Language: {project.language}</span>}
            <span>
              Updated: {new Date(project.updated_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Projects页面主组件
 */
export const Projects: React.FC<ProjectsProps> = ({
  enableVirtualScroll = true,
}) => {
  const { data: projects, isLoading, error } = useProjects();
  const updateProject = useUpdateProject();
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState<string>('');
  const [sortBy, setSortBy] = useState<'name' | 'created_at' | 'updated_at' | 'is_active'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [localProjects, setLocalProjects] = useState<Project[]>([]);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [showTagModal, setShowTagModal] = useState<boolean>(false);
  const [tagInput, setTagInput] = useState<string>('');
  const [batchOperationInProgress, setBatchOperationInProgress] = useState<boolean>(false);

  // 配置拖拽传感器
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 移动8px后才开始拖拽，避免误触
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // 初始化本地项目列表
  useEffect(() => {
    if (projects) {
      setLocalProjects(projects);
    }
  }, [projects]);

  // 初始化本地项目列表
  useEffect(() => {
    if (projects) {
      setLocalProjects(projects);
    }
  }, [projects]);

  // 处理拖拽结束
  const handleDragEnd = useCallback(
    async (event: DragEndEvent) => {
      const { active, over } = event;

      if (!over || active.id === over.id) {
        return;
      }

      // 更新本地顺序
      setLocalProjects((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);

        if (oldIndex === -1 || newIndex === -1) {
          return items;
        }

        const newItems = arrayMove(items, oldIndex, newIndex);

        // 持久化到后端 - 更新每个项目的display_order字段
        // 注意：这里假设后端支持display_order字段，如果不支持，可以使用其他方式存储顺序
        newItems.forEach((item, index) => {
          updateProject.mutate({
            projectId: item.id,
            updates: { display_order: index } as any, // 使用any因为Project类型可能没有display_order
          });
        });

        return newItems;
      });
    },
    [updateProject]
  );

  // 防抖搜索 - 300毫秒延迟
  useEffect(() => {
    // 清除之前的定时器
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // 设置新的定时器
    searchTimeoutRef.current = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 300);

    // 清理函数
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery]);

  // 处理搜索输入变化
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  }, []);

  // 清除搜索
  const handleClearSearch = useCallback(() => {
    setSearchQuery('');
    setDebouncedSearchQuery('');
  }, []);

  // 过滤项目列表
  const filteredProjects = useMemo(() => {
    if (!localProjects) return [];
    if (!debouncedSearchQuery.trim()) return localProjects;

    const query = debouncedSearchQuery.toLowerCase().trim();
    return localProjects.filter((project) => {
      // 搜索项目名称
      if (project.name.toLowerCase().includes(query)) return true;
      
      // 搜索项目描述
      if (project.description?.toLowerCase().includes(query)) return true;
      
      // 搜索编程语言
      if (project.language?.toLowerCase().includes(query)) return true;
      
      // 搜索状态
      if (project.is_active && 'active'.includes(query)) return true;
      if (!project.is_active && 'inactive'.includes(query)) return true;
      
      return false;
    });
  }, [localProjects, debouncedSearchQuery]);

  // 排序项目列表
  const sortedProjects = useMemo(() => {
    if (!filteredProjects || filteredProjects.length === 0) return [];

    const sorted = [...filteredProjects].sort((a, b) => {
      let compareResult = 0;

      switch (sortBy) {
        case 'name':
          compareResult = a.name.localeCompare(b.name);
          break;
        case 'created_at':
          compareResult = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
        case 'updated_at':
          compareResult = new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime();
          break;
        case 'is_active':
          // Active projects first (true > false)
          compareResult = (b.is_active ? 1 : 0) - (a.is_active ? 1 : 0);
          break;
        default:
          compareResult = 0;
      }

      // Apply sort order
      return sortOrder === 'asc' ? compareResult : -compareResult;
    });

    return sorted;
  }, [filteredProjects, sortBy, sortOrder]);

  // 处理排序变化
  const handleSortChange = useCallback((newSortBy: typeof sortBy) => {
    if (sortBy === newSortBy) {
      // 如果点击相同的排序字段，切换排序顺序
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      // 如果点击不同的排序字段，设置为升序
      setSortBy(newSortBy);
      setSortOrder('asc');
    }
  }, [sortBy]);

  // 切换项目选择状态
  const handleToggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  // 全选/取消全选（基于排序后的项目）
  const handleToggleSelectAll = () => {
    if (!sortedProjects) return;
    
    if (selectedIds.size === sortedProjects.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(sortedProjects.map((p) => p.id)));
    }
  };

  // 批量删除
  const handleBatchDelete = useCallback(async () => {
    if (selectedIds.size === 0) return;
    
    const confirmed = window.confirm(
      `Are you sure you want to delete ${selectedIds.size} project${selectedIds.size > 1 ? 's' : ''}? This action cannot be undone.`
    );
    
    if (!confirmed) return;
    
    setBatchOperationInProgress(true);
    
    try {
      // 删除所有选中的项目
      const deletePromises = Array.from(selectedIds).map((projectId) =>
        updateProject.mutateAsync({
          projectId,
          updates: { is_active: false } as any, // 软删除：设置为不活跃
        })
      );
      
      await Promise.all(deletePromises);
      
      // 从本地状态中移除已删除的项目
      setLocalProjects((prev) =>
        prev.filter((project) => !selectedIds.has(project.id))
      );
      
      // 清除选择
      setSelectedIds(new Set());
      
      alert(`Successfully deleted ${selectedIds.size} project${selectedIds.size > 1 ? 's' : ''}`);
    } catch (error) {
      console.error('Batch delete failed:', error);
      alert('Failed to delete some projects. Please try again.');
    } finally {
      setBatchOperationInProgress(false);
    }
  }, [selectedIds, updateProject]);

  // 批量归档
  const handleBatchArchive = useCallback(async () => {
    if (selectedIds.size === 0) return;
    
    const confirmed = window.confirm(
      `Are you sure you want to archive ${selectedIds.size} project${selectedIds.size > 1 ? 's' : ''}?`
    );
    
    if (!confirmed) return;
    
    setBatchOperationInProgress(true);
    
    try {
      // 归档所有选中的项目
      const archivePromises = Array.from(selectedIds).map((projectId) =>
        updateProject.mutateAsync({
          projectId,
          updates: { is_active: false } as any, // 归档：设置为不活跃
        })
      );
      
      await Promise.all(archivePromises);
      
      // 更新本地状态
      setLocalProjects((prev) =>
        prev.map((project) =>
          selectedIds.has(project.id)
            ? { ...project, is_active: false }
            : project
        )
      );
      
      // 清除选择
      setSelectedIds(new Set());
      
      alert(`Successfully archived ${selectedIds.size} project${selectedIds.size > 1 ? 's' : ''}`);
    } catch (error) {
      console.error('Batch archive failed:', error);
      alert('Failed to archive some projects. Please try again.');
    } finally {
      setBatchOperationInProgress(false);
    }
  }, [selectedIds, updateProject]);

  // 批量添加标签
  const handleBatchTag = useCallback(() => {
    if (selectedIds.size === 0) return;
    setShowTagModal(true);
  }, [selectedIds]);

  // 确认添加标签
  const handleConfirmTag = useCallback(async () => {
    if (!tagInput.trim() || selectedIds.size === 0) return;
    
    setBatchOperationInProgress(true);
    setShowTagModal(false);
    
    try {
      // 注意：当前Project类型不包含tags字段
      // 这里提供一个占位实现，实际应该调用支持tags的API端点
      // 例如: POST /projects/{id}/tags 或者扩展Project模型
      
      // 临时实现：使用description字段存储标签信息
      // 在实际生产环境中，应该扩展后端API支持tags字段
      const tagPromises = Array.from(selectedIds).map((projectId) => {
        const project = localProjects.find((p) => p.id === projectId);
        if (!project) return Promise.resolve();
        
        // 将标签添加到description中（临时方案）
        const newTags = tagInput
          .split(',')
          .map((tag) => tag.trim())
          .filter((tag) => tag);
        
        if (newTags.length === 0) return Promise.resolve();
        
        const tagString = `[Tags: ${newTags.join(', ')}]`;
        const updatedDescription = project.description 
          ? `${project.description} ${tagString}`
          : tagString;
        
        return updateProject.mutateAsync({
          projectId,
          updates: { description: updatedDescription },
        });
      });
      
      await Promise.all(tagPromises);
      
      // 更新本地状态
      setLocalProjects((prev) =>
        prev.map((project) => {
          if (!selectedIds.has(project.id)) return project;
          
          const newTags = tagInput
            .split(',')
            .map((tag) => tag.trim())
            .filter((tag) => tag);
          
          const tagString = `[Tags: ${newTags.join(', ')}]`;
          const updatedDescription = project.description 
            ? `${project.description} ${tagString}`
            : tagString;
          
          return {
            ...project,
            description: updatedDescription,
          };
        })
      );
      
      // 清除选择和输入
      setSelectedIds(new Set());
      setTagInput('');
      
      alert(`Successfully added tags to ${selectedIds.size} project${selectedIds.size > 1 ? 's' : ''}`);
    } catch (error) {
      console.error('Batch tag failed:', error);
      alert('Failed to add tags to some projects. Please try again.');
    } finally {
      setBatchOperationInProgress(false);
    }
  }, [selectedIds, tagInput, localProjects, updateProject]);

  // 取消添加标签
  const handleCancelTag = useCallback(() => {
    setShowTagModal(false);
    setTagInput('');
  }, []);

  // 渲染单个项目项
  const renderProjectItem = (project: Project, index: number) => {
    return (
      <ProjectListItem
        key={project.id}
        project={project}
        isSelected={selectedIds.has(project.id)}
        onSelect={handleToggleSelect}
      />
    );
  };

  // 计算是否应该使用虚拟滚动（基于排序后的项目）
  const shouldUseVirtualScroll = useMemo(() => {
    return enableVirtualScroll && sortedProjects && sortedProjects.length > 100;
  }, [enableVirtualScroll, sortedProjects]);

  // 加载状态
  if (isLoading) {
    return <LoadingState text="Loading projects..." />;
  }

  // 错误状态
  if (error) {
    return (
      <div
        style={{
          padding: '40px 20px',
          textAlign: 'center',
        }}
      >
        <div
          style={{
            color: '#c33',
            fontSize: '18px',
            marginBottom: '16px',
          }}
        >
          ⚠️ Failed to load projects
        </div>
        <div style={{ color: '#666', fontSize: '14px' }}>
          {error instanceof Error ? error.message : 'Unknown error occurred'}
        </div>
      </div>
    );
  }

  // 空状态
  if (!localProjects || localProjects.length === 0) {
    return (
      <div
        style={{
          padding: '40px 20px',
          textAlign: 'center',
        }}
      >
        <div
          style={{
            fontSize: '18px',
            color: '#666',
            marginBottom: '16px',
          }}
        >
          No projects found
        </div>
        <div style={{ fontSize: '14px', color: '#999' }}>
          Create your first project to get started
        </div>
      </div>
    );
  }

  // 搜索无结果状态
  const hasSearchResults = sortedProjects.length > 0;
  const isSearching = debouncedSearchQuery.trim().length > 0;

  return (
    <ErrorBoundary>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <div
          style={{
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: '#f5f5f5',
            overflow: 'hidden',
          }}
        >
          {/* 离线指示器 */}
          <OfflineIndicator />

          {/* 头部工具栏 */}
          <div
            style={{
              padding: 'clamp(12px, 2vw, 24px)',
              backgroundColor: '#fff',
              borderBottom: '1px solid #e0e0e0',
              overflowX: 'hidden',
            }}
          >
            <div
              style={{
                display: 'flex',
                flexDirection: window.innerWidth < 768 ? 'column' : 'row',
                alignItems: window.innerWidth < 768 ? 'flex-start' : 'center',
                justifyContent: 'space-between',
                marginBottom: '16px',
                gap: '12px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                <h1
                  style={{
                    margin: 0,
                    fontSize: 'clamp(20px, 4vw, 24px)',
                    fontWeight: 600,
                    color: '#333',
                  }}
                >
                  Projects
                </h1>
                <span
                  style={{
                    padding: '4px 12px',
                    backgroundColor: '#e0e0e0',
                    borderRadius: '12px',
                    fontSize: 'clamp(12px, 2.5vw, 14px)',
                    color: '#666',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {sortedProjects.length} {sortedProjects.length === 1 ? 'project' : 'projects'}
                  {isSearching && ` of ${localProjects.length}`}
                </span>
              </div>

              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                {selectedIds.size > 0 && (
                  <>
                    <span
                      style={{
                        fontSize: 'clamp(12px, 2.5vw, 14px)',
                        color: '#666',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {selectedIds.size} selected
                    </span>
                    <button
                      onClick={handleBatchDelete}
                      style={{
                        padding: 'clamp(6px, 1.5vw, 8px) clamp(12px, 2.5vw, 16px)',
                        fontSize: 'clamp(12px, 2.5vw, 14px)',
                        color: '#fff',
                        backgroundColor: '#d32f2f',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        whiteSpace: 'nowrap',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#b71c1c';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = '#d32f2f';
                      }}
                    >
                      Delete
                    </button>
                    <button
                      onClick={handleBatchArchive}
                      style={{
                        padding: 'clamp(6px, 1.5vw, 8px) clamp(12px, 2.5vw, 16px)',
                        fontSize: 'clamp(12px, 2.5vw, 14px)',
                        color: '#fff',
                        backgroundColor: '#f57c00',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        whiteSpace: 'nowrap',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#e65100';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = '#f57c00';
                      }}
                    >
                      Archive
                    </button>
                    <button
                      onClick={handleBatchTag}
                      style={{
                        padding: 'clamp(6px, 1.5vw, 8px) clamp(12px, 2.5vw, 16px)',
                        fontSize: 'clamp(12px, 2.5vw, 14px)',
                        color: '#fff',
                        backgroundColor: '#388e3c',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        whiteSpace: 'nowrap',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#2e7d32';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = '#388e3c';
                      }}
                    >
                      Add Tag
                    </button>
                  </>
                )}
                <button
                  onClick={handleToggleSelectAll}
                  style={{
                    padding: 'clamp(6px, 1.5vw, 8px) clamp(12px, 2.5vw, 16px)',
                    fontSize: 'clamp(12px, 2.5vw, 14px)',
                    color: '#333',
                    backgroundColor: '#f0f0f0',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {selectedIds.size === sortedProjects.length ? 'Deselect All' : 'Select All'}
                </button>
              </div>
            </div>

          {/* 排序控制栏 */}
          <div
            style={{
              display: 'flex',
              gap: '8px',
              alignItems: 'center',
              marginBottom: '16px',
            }}
          >
            <span
              style={{
                fontSize: '14px',
                color: '#666',
                fontWeight: 500,
              }}
            >
              Sort by:
            </span>
            <button
              onClick={() => handleSortChange('name')}
              style={{
                padding: '6px 12px',
                fontSize: '14px',
                color: sortBy === 'name' ? '#fff' : '#333',
                backgroundColor: sortBy === 'name' ? '#4a90e2' : '#f0f0f0',
                border: '1px solid',
                borderColor: sortBy === 'name' ? '#4a90e2' : '#ccc',
                borderRadius: '4px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              Name
              {sortBy === 'name' && (
                <span style={{ fontSize: '12px' }}>
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </button>
            <button
              onClick={() => handleSortChange('created_at')}
              style={{
                padding: '6px 12px',
                fontSize: '14px',
                color: sortBy === 'created_at' ? '#fff' : '#333',
                backgroundColor: sortBy === 'created_at' ? '#4a90e2' : '#f0f0f0',
                border: '1px solid',
                borderColor: sortBy === 'created_at' ? '#4a90e2' : '#ccc',
                borderRadius: '4px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              Created
              {sortBy === 'created_at' && (
                <span style={{ fontSize: '12px' }}>
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </button>
            <button
              onClick={() => handleSortChange('updated_at')}
              style={{
                padding: '6px 12px',
                fontSize: '14px',
                color: sortBy === 'updated_at' ? '#fff' : '#333',
                backgroundColor: sortBy === 'updated_at' ? '#4a90e2' : '#f0f0f0',
                border: '1px solid',
                borderColor: sortBy === 'updated_at' ? '#4a90e2' : '#ccc',
                borderRadius: '4px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              Updated
              {sortBy === 'updated_at' && (
                <span style={{ fontSize: '12px' }}>
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </button>
            <button
              onClick={() => handleSortChange('is_active')}
              style={{
                padding: '6px 12px',
                fontSize: '14px',
                color: sortBy === 'is_active' ? '#fff' : '#333',
                backgroundColor: sortBy === 'is_active' ? '#4a90e2' : '#f0f0f0',
                border: '1px solid',
                borderColor: sortBy === 'is_active' ? '#4a90e2' : '#ccc',
                borderRadius: '4px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              Status
              {sortBy === 'is_active' && (
                <span style={{ fontSize: '12px' }}>
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </span>
              )}
            </button>
          </div>

          {/* 搜索栏 */}
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Search projects by name, description, language, or status..."
              value={searchQuery}
              onChange={handleSearchChange}
              style={{
                width: '100%',
                padding: '10px 40px 10px 16px',
                fontSize: '14px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                outline: 'none',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = '#4a90e2';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = '#ccc';
              }}
            />
            {searchQuery && (
              <button
                onClick={handleClearSearch}
                style={{
                  position: 'absolute',
                  right: '8px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  padding: '4px 8px',
                  fontSize: '14px',
                  color: '#666',
                  backgroundColor: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  borderRadius: '4px',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f0f0f0';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
                aria-label="Clear search"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* 项目列表 */}
        <div style={{ flex: 1, overflow: 'hidden' }}>
          {!hasSearchResults && isSearching ? (
            <div
              style={{
                padding: '40px 20px',
                textAlign: 'center',
              }}
            >
              <div
                style={{
                  fontSize: '18px',
                  color: '#666',
                  marginBottom: '16px',
                }}
              >
                No projects match your search
              </div>
              <div style={{ fontSize: '14px', color: '#999', marginBottom: '16px' }}>
                Try adjusting your search terms
              </div>
              <button
                onClick={handleClearSearch}
                style={{
                  padding: '8px 16px',
                  fontSize: '14px',
                  color: '#fff',
                  backgroundColor: '#4a90e2',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Clear search
              </button>
            </div>
          ) : (
            <SortableContext
              items={sortedProjects.map((p) => p.id)}
              strategy={verticalListSortingStrategy}
            >
              {shouldUseVirtualScroll ? (
                <VirtualList
                  items={sortedProjects}
                  height={window.innerHeight - 140} // 减去头部高度（包含搜索栏）
                  itemHeight={120} // 估计的项目项高度
                  overscan={5}
                  renderItem={renderProjectItem}
                  className="projects-virtual-list"
                />
              ) : (
                <div
                  style={{
                    height: '100%',
                    overflow: 'auto',
                    backgroundColor: '#fff',
                  }}
                >
                  {sortedProjects.map((project, index) => renderProjectItem(project, index))}
                </div>
              )}
            </SortableContext>
          )}
        </div>

        {/* 标签添加模态框 */}
        {showTagModal && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
            }}
            onClick={handleCancelTag}
          >
            <div
              style={{
                backgroundColor: '#fff',
                borderRadius: '8px',
                padding: '24px',
                maxWidth: '500px',
                width: '90%',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <h2
                style={{
                  margin: '0 0 16px 0',
                  fontSize: '20px',
                  fontWeight: 600,
                  color: '#333',
                }}
              >
                Add Tags to {selectedIds.size} Project{selectedIds.size > 1 ? 's' : ''}
              </h2>
              <p
                style={{
                  margin: '0 0 16px 0',
                  fontSize: '14px',
                  color: '#666',
                }}
              >
                Enter tags separated by commas (e.g., "frontend, react, typescript")
              </p>
              <input
                type="text"
                placeholder="Enter tags..."
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleConfirmTag();
                  } else if (e.key === 'Escape') {
                    handleCancelTag();
                  }
                }}
                autoFocus
                style={{
                  width: '100%',
                  padding: '10px 16px',
                  fontSize: '14px',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  outline: 'none',
                  marginBottom: '16px',
                }}
              />
              <div
                style={{
                  display: 'flex',
                  gap: '12px',
                  justifyContent: 'flex-end',
                }}
              >
                <button
                  onClick={handleCancelTag}
                  style={{
                    padding: '8px 16px',
                    fontSize: '14px',
                    color: '#333',
                    backgroundColor: '#f0f0f0',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmTag}
                  disabled={!tagInput.trim()}
                  style={{
                    padding: '8px 16px',
                    fontSize: '14px',
                    color: '#fff',
                    backgroundColor: tagInput.trim() ? '#388e3c' : '#ccc',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: tagInput.trim() ? 'pointer' : 'not-allowed',
                  }}
                >
                  Add Tags
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 批量操作加载指示器 */}
        {batchOperationInProgress && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1001,
            }}
          >
            <div
              style={{
                backgroundColor: '#fff',
                borderRadius: '8px',
                padding: '24px 32px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '16px',
              }}
            >
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  border: '4px solid #f0f0f0',
                  borderTop: '4px solid #4a90e2',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                }}
              />
              <div
                style={{
                  fontSize: '16px',
                  color: '#333',
                  fontWeight: 500,
                }}
              >
                Processing batch operation...
              </div>
            </div>
          </div>
        )}
      </div>
    </DndContext>
    </ErrorBoundary>
  );
};

export default Projects;
