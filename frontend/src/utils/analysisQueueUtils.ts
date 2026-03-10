import { AnalysisTask } from '../types/AnalysisQueue';

export const getTaskTypeText = (type: AnalysisTask['type']): string => {
  switch (type) {
    case 'code_analysis':
      return 'Code Analysis';
    case 'security_scan':
      return 'Security Scan';
    case 'performance_test':
      return 'Performance Test';
    case 'dependency_check':
      return 'Dependency Check';
    default:
      return 'Unknown';
  }
};

export const getStatusColor = (status: AnalysisTask['status']): string => {
  switch (status) {
    case 'pending':
      return '#6b7280';
    case 'running':
      return '#0066cc';
    case 'completed':
      return '#22c55e';
    case 'failed':
      return '#ef4444';
    case 'cancelled':
      return '#f59e0b';
    default:
      return '#6b7280';
  }
};

export const getStatusText = (status: AnalysisTask['status']): string => {
  switch (status) {
    case 'pending':
      return 'Pending';
    case 'running':
      return 'Running';
    case 'completed':
      return 'Completed';
    case 'failed':
      return 'Failed';
    case 'cancelled':
      return 'Cancelled';
    default:
      return 'Unknown';
  }
};

export const getPriorityText = (priority: number): string => {
  if (priority >= 8) return 'Critical';
  if (priority >= 6) return 'High';
  if (priority >= 4) return 'Medium';
  return 'Low';
};

export const getPriorityColor = (priority: number): string => {
  if (priority >= 8) return '#ef4444';
  if (priority >= 6) return '#f59e0b';
  if (priority >= 4) return '#0066cc';
  return '#6b7280';
};

export const formatTime = (date: Date | undefined): string => {
  if (!date) return 'N/A';
  return new Date(date).toLocaleString();
};

export const formatDuration = (seconds: number | undefined): string => {
  if (!seconds) return 'N/A';
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
};

export const calculateEstimatedCompletion = (task: AnalysisTask): Date | null => {
  if (task.status !== 'running') {
    return null;
  }

  if (!task.startedAt || !task.estimatedDuration) {
    return null;
  }

  const startTime = new Date(task.startedAt).getTime();
  const now = Date.now();
  const elapsedSeconds = (now - startTime) / 1000;

  if (task.progress > 0 && task.progress < 100) {
    const estimatedTotalSeconds = (elapsedSeconds / task.progress) * 100;
    const remainingSeconds = estimatedTotalSeconds - elapsedSeconds;
    return new Date(now + remainingSeconds * 1000);
  }

  const remainingSeconds = task.estimatedDuration - elapsedSeconds;
  if (remainingSeconds > 0) {
    return new Date(now + remainingSeconds * 1000);
  }

  return null;
};

export const formatEstimatedCompletion = (estimatedCompletion: Date | null): string => {
  if (!estimatedCompletion) {
    return 'N/A';
  }

  const now = Date.now();
  const completionTime = estimatedCompletion.getTime();
  const remainingMs = completionTime - now;

  if (remainingMs <= 0) {
    return 'Completing soon...';
  }

  const remainingSeconds = Math.floor(remainingMs / 1000);
  
  if (remainingSeconds < 60) {
    return `~${remainingSeconds}s`;
  } else if (remainingSeconds < 3600) {
    const minutes = Math.floor(remainingSeconds / 60);
    return `~${minutes}m`;
  } else {
    const hours = Math.floor(remainingSeconds / 3600);
    const minutes = Math.floor((remainingSeconds % 3600) / 60);
    return `~${hours}h ${minutes}m`;
  }
};

export const countTasksByStatus = (tasks: AnalysisTask[]) => {
  return {
    pending: tasks.filter(t => t.status === 'pending').length,
    running: tasks.filter(t => t.status === 'running').length,
    completed: tasks.filter(t => t.status === 'completed').length,
    failed: tasks.filter(t => t.status === 'failed').length,
  };
};
