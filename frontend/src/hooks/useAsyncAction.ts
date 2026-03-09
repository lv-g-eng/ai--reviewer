/**
 * useAsyncAction Hook
 * 
 * Manages async operation state (loading, error) with a simple execute function.
 * Eliminates repetitive try-catch and loading state management patterns.
 * 
 * @example
 * const { execute, loading, error } = useAsyncAction<User>();
 * 
 * const handleLogin = async () => {
 *   const user = await execute(() => loginUser(email, password));
 *   if (user) {
 *     router.push('/dashboard');
 *   }
 * };
 */

import { useState, useCallback } from 'react';

export interface AsyncActionResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  execute: (action: () => Promise<T>, onSuccess?: (data: T) => void) => Promise<T | null>;
  reset: () => void;
}

/**
 * Hook for managing async operation state
 * 
 * @returns Object with loading, error states and execute function
 * 
 * @example
 * function MyComponent() {
 *   const { execute, loading, error } = useAsyncAction();
 *   
 *   const handleSubmit = async () => {
 *     await execute(
 *       () => apiClient.post('/api/data', data),
 *       (result) => {
 *         console.log('Success:', result);
 *       }
 *     );
 *   };
 *   
 *   return (
 *     <div>
 *       {loading && <Spinner />}
 *       {error && <ErrorMessage error={error} />}
 *       <button onClick={handleSubmit} disabled={loading}>
 *         Submit
 *       </button>
 *     </div>
 *   );
 * }
 */
export function useAsyncAction<T = unknown>(): AsyncActionResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(
    async (action: () => Promise<T>, onSuccess?: (data: T) => void): Promise<T | null> => {
      setLoading(true);
      setError(null);

      try {
        const result = await action();
        setData(result);
        onSuccess?.(result);
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    setData(null);
    setLoading(false);
    setError(null);
  }, []);

  return { data, loading, error, execute, reset };
}

export default useAsyncAction;
