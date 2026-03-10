import React from 'react';
import { styles } from './AnalysisQueue.styles';

interface TaskStatsProps {
  total: number;
  pending: number;
  running: number;
  completed: number;
  failed: number;
}

export const TaskStats: React.FC<TaskStatsProps> = ({
  total,
  pending,
  running,
  completed,
  failed,
}) => {
  return (
    <div style={styles.statsGrid}>
      <div style={styles.statCard}>
        <div style={styles.statValue}>{total}</div>
        <div style={styles.statLabel}>Total Tasks</div>
      </div>
      <div style={styles.statCard}>
        <div style={{ ...styles.statValue, color: '#6b7280' }}>{pending}</div>
        <div style={styles.statLabel}>Pending</div>
      </div>
      <div style={styles.statCard}>
        <div style={{ ...styles.statValue, color: '#0066cc' }}>{running}</div>
        <div style={styles.statLabel}>Running</div>
      </div>
      <div style={styles.statCard}>
        <div style={{ ...styles.statValue, color: '#22c55e' }}>{completed}</div>
        <div style={styles.statLabel}>Completed</div>
      </div>
      <div style={styles.statCard}>
        <div style={{ ...styles.statValue, color: '#ef4444' }}>{failed}</div>
        <div style={styles.statLabel}>Failed</div>
      </div>
    </div>
  );
};
