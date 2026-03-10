import React from 'react';
import { ScheduleResult } from '../../types/AnalysisQueue';
import { styles } from './AnalysisQueue.styles';

interface ScheduleInfoProps {
  scheduleResult: ScheduleResult;
  maxConcurrent: number;
}

export const ScheduleInfo: React.FC<ScheduleInfoProps> = ({
  scheduleResult,
  maxConcurrent,
}) => {
  return (
    <div style={styles.scheduleInfo}>
      <div style={styles.scheduleInfoItem}>
        <span style={styles.scheduleInfoLabel}>Max Concurrent:</span>
        <span style={styles.scheduleInfoValue}>{maxConcurrent}</span>
      </div>
      <div style={styles.scheduleInfoItem}>
        <span style={styles.scheduleInfoLabel}>Available Slots:</span>
        <span style={styles.scheduleInfoValue}>{scheduleResult.availableSlots}</span>
      </div>
      <div style={styles.scheduleInfoItem}>
        <span style={styles.scheduleInfoLabel}>Scheduled to Execute:</span>
        <span style={styles.scheduleInfoValue}>{scheduleResult.tasksToExecute.length}</span>
      </div>
      <div style={styles.scheduleInfoItem}>
        <span style={styles.scheduleInfoLabel}>Waiting:</span>
        <span style={styles.scheduleInfoValue}>{scheduleResult.waitingTasks.length}</span>
      </div>
    </div>
  );
};
