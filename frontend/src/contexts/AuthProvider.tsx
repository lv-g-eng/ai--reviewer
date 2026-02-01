'use client';

import { AuthProvider as BaseAuthProvider } from './AuthContext';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <BaseAuthProvider>
      {children}
    </BaseAuthProvider>
  );
}

export { AuthContext, useAuth } from './AuthContext';
