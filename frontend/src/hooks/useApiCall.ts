/**
 * useApiCall Hook
 * 
 * Unified API call handler with automatic toast notifications and error handling.
 * Eliminates repetitive try-catch + toast patterns throughout the codebase.
 * 
 * @example
 * const { execute } = useApiCall();
 * 
 * await execute(
 *   () => apiClient.post('/api/users', userData),
 *   {
 *     successMessage: 'User created successfully',
 *     errorMessage: 'Failed to create user',
 *     onSuccess: (user) => router.push(`/users/${user.id}`)
 *   }
 * );
 */

import { useCallback } from 'react';
import { useToast } from '@/hooks/use-toast';

export interface ApiCallOptions<T> {
  /** Toast message to show on success */
  successMessage?: string;
  /** Toast message to show on error (overrides error.message) */
  errorMessage?: string;
  /** Callback executed on successful API call */
  onSuccess?: (data: T) => void;
  /** Callback executed on error */
  onError?: (error: Error) => void;
  /** Whether to show toast on error (default: true) */
  showErrorToast?: boolean;
  /** Whether to show toast on success (default: true if successMessage provided) */
  showSuccessToast?: boolean;
}

export interface ApiCallResult {
  /** Execute an API call with automatic error handling and toast notifications */
  execute: <T>(
    apiCall: () => Promise<T>,
    options?: ApiCallOptions<T>
  ) => Promise<T | null>;
}

/**
 * Hook for unified API call handling with toast notifications
 * 
 * @returns Object with execute function
 * 
 * @example
 * function LoginForm() {
 *   const { execute } = useApiCall();
 *   const router = useRouter();
 *   
 *   const handleLogin = async (email: string, password: string) => {
 *     const user = await execute(
 *       () => login(email, password),
 *       {
 *         successMessage: 'Login successful! Redirecting...',
 *         errorMessage: 'Invalid credentials',
 *         onSuccess: (user) => router.push('/dashboard')
 *       }
 *     );
 *   };
 *   
 *   return <button onClick={() => handleLogin(email, password)}>Login</button>;
 * }
 * 
 * @example
 * // With custom error handling
 * function DeleteButton({ projectId }) {
 *   const { execute } = useApiCall();
 *   
 *   const handleDelete = async () => {
 *     await execute(
 *       () => apiClient.delete(`/api/projects/${projectId}`),
 *       {
 *         successMessage: 'Project deleted',
 *         showErrorToast: false, // Handle error manually
 *         onError: (error) => {
 *           if (error.message.includes('permission')) {
 *             alert('You do not have permission to delete this project');
 *           }
 *         }
 *       }
 *     );
 *   };
 *   
 *   return <button onClick={handleDelete}>Delete</button>;
 * }
 */
export function useApiCall(): ApiCallResult {
  const { toast } = useToast();

  const execute = useCallback(
    async <T>(
      apiCall: () => Promise<T>,
      options: ApiCallOptions<T> = {}
    ): Promise<T | null> => {
      const {
        successMessage,
        errorMessage,
        onSuccess,
        onError,
        showErrorToast = true,
        showSuccessToast = !!successMessage,
      } = options;

      try {
        const data = await apiCall();

        if (showSuccessToast && successMessage) {
          toast({
            title: 'Success',
            description: successMessage,
          });
        }

        onSuccess?.(data);
        return data;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        
        // Extract error message from various error formats
        let message = errorMessage || error.message;
        
        // Check for axios-style error response
        const anyError = err as Record<string, unknown>;
        if (anyError.response && typeof anyError.response === 'object') {
          const response = anyError.response as Record<string, unknown>;
          if (response.data && typeof response.data === 'object') {
            const data = response.data as Record<string, unknown>;
            message = (data.detail as string) || (data.message as string) || message;
          }
        }

        if (showErrorToast) {
          toast({
            variant: 'destructive',
            title: 'Error',
            description: message,
          });
        }

        onError?.(error);
        return null;
      }
    },
    [toast]
  );

  return { execute };
}

export default useApiCall;
