import { createContext, useContext } from 'react';

export interface User {
  id: string;
  email?: string;
  roles?: string[];
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signOut: () => Promise<void>;
}

/**
 * Split into its own file (not the provider) so the real and test providers can
 * both import the context without a circular dependency.
 */
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
