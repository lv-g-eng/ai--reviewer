/**
 * Hook for accessing backend availability status
 * 
 * Validates Requirements: 3.1, 3.4, 3.5, 10.1, 10.2
 */

import { useBackendStatusContext } from '@/contexts/BackendStatusContext';

export function useBackendStatus() {
  const context = useBackendStatusContext();
  
  return {
    isOnline: context.isOnline,
    isChecking: context.isChecking,
    retry: context.retry,
    lastChecked: context.lastChecked,
  };
}
