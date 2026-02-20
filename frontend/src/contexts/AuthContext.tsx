'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { Session, User } from 'next-auth';
import { signIn, signOut, useSession } from 'next-auth/react';
import { Role, Permission } from '@/types/rbac';

type AuthContextType = {
  user: User | null;
  session: Session | null;
  loading: boolean;
  role: Role | null;
  permissions: Permission[];
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export { AuthContext };

// Role-Permission mapping
const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  [Role.ADMIN]: [
    Permission.VIEW_PROJECTS,
    Permission.CREATE_PROJECT,
    Permission.MODIFY_PROJECT,
    Permission.DELETE_PROJECT,
    Permission.VIEW_USERS,
    Permission.CREATE_USER,
    Permission.MODIFY_USER,
    Permission.DELETE_USER,
    Permission.VIEW_REVIEWS,
    Permission.CREATE_REVIEW,
    Permission.MODIFY_REVIEW,
    Permission.MODIFY_CONFIG,
  ],
  [Role.PROGRAMMER]: [
    Permission.VIEW_PROJECTS,
    Permission.CREATE_PROJECT,
    Permission.MODIFY_PROJECT,
    Permission.VIEW_REVIEWS,
    Permission.CREATE_REVIEW,
    Permission.MODIFY_REVIEW,
  ],
  [Role.VISITOR]: [
    Permission.VIEW_PROJECTS,
    Permission.VIEW_REVIEWS,
  ],
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: session, status } = useSession();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState<Role | null>(null);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const router = useRouter();

  useEffect(() => {
    if (status === 'authenticated') {
      setUser(session?.user || null);
      
      // Extract role from user
      const userRole = (session?.user as any)?.role as Role;
      setRole(userRole || null);
      
      // Set permissions based on role
      if (userRole && ROLE_PERMISSIONS[userRole]) {
        setPermissions(ROLE_PERMISSIONS[userRole]);
      } else {
        setPermissions([]);
      }
      
      setLoading(false);
    } else if (status === 'unauthenticated') {
      setUser(null);
      setRole(null);
      setPermissions([]);
      setLoading(false);
    }
  }, [session, status]);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const result = await signIn('credentials', {
        redirect: false,
        email,
        password,
      });

      if (result?.error) {
        throw new Error(result.error);
      }

      router.push('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (email: string, password: string, name: string) => {
    setLoading(true);
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Registration failed');
      }

      // After successful registration, log the user in
      await login(email, password);
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await signOut({ redirect: false });
      setUser(null);
      setRole(null);
      setPermissions([]);
      router.push('/');
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const refreshToken = async () => {
    // Token refresh is handled by NextAuth automatically
    // This function is provided for compatibility with the RBAC spec
    try {
      // Force session update
      const { data: newSession } = await fetch('/api/auth/session').then(res => res.json());
      if (newSession) {
        const userRole = (newSession?.user as any)?.role as Role;
        setRole(userRole || null);
        if (userRole && ROLE_PERMISSIONS[userRole]) {
          setPermissions(ROLE_PERMISSIONS[userRole]);
        }
      }
    } catch (error) {
      console.error('Token refresh error:', error);
    }
  };

  return (
    <AuthContext.Provider value={{ user, session, loading, role, permissions, login, register, logout, refreshToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
