import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';

import { registerTokenProvider, SESSION_EXPIRED_EVENT } from '@/shared/api/core';

import { AuthContext, type AuthContextType, type User } from './AuthContext';

const TOKEN_STORAGE_KEY = 'app:auth-token';

/**
 * Real auth provider (⇄ swappable: Descope, etc.). Currently a STUB: the backend
 * has no auth vendor wired in (`app/api/middleware/auth.py` fails closed), so this
 * reports an unauthenticated user and hands the fetch wrapper a null token.
 *
 * To make it real, in order:
 *   1. Exchange the vendor session at a backend `/auth/callback` (sets cookies).
 *   2. Store the access token and set `user` / `isAuthenticated`.
 *   3. Return it from `getToken`, and implement `refreshToken`.
 */
function RealAuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading] = useState(false);

  const signOut = useCallback(async () => {
    // TODO: call the vendor sign-out + backend session teardown.
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setUser(null);
  }, []);

  // Bridge the non-React fetch wrapper to the auth state (§5/§8).
  useEffect(() => {
    registerTokenProvider({
      getToken: () => localStorage.getItem(TOKEN_STORAGE_KEY),
      // TODO: hit the vendor/backend refresh endpoint and persist the new token.
      refreshToken: async () => null,
    });
    return () => registerTokenProvider(null);
  }, []);

  // Auto-logout when the fetch wrapper reports an unrecoverable 401.
  useEffect(() => {
    const onExpired = () => void signOut();
    window.addEventListener(SESSION_EXPIRED_EVENT, onExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, onExpired);
  }, [signOut]);

  // Cross-tab logout: another tab clearing the token key logs this one out too.
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === TOKEN_STORAGE_KEY && e.newValue === null) setUser(null);
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  const value = useMemo<AuthContextType>(
    () => ({ user, isLoading, isAuthenticated: !!user, signOut }),
    [user, isLoading, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * In-memory test provider, gated by the build-time `__TEST_AUTH_ENABLED__` flag
 * (false in prod → dead-code-eliminated). Reports a fixed authenticated user so
 * tests and local UI work can bypass the vendor flow.
 */
function TestAuthProvider({ children }: { children: ReactNode }) {
  const value = useMemo<AuthContextType>(
    () => ({
      user: { id: 'test-user', email: 'test@example.com', roles: ['admin'] },
      isLoading: false,
      isAuthenticated: true,
      signOut: async () => {},
    }),
    [],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  if (__TEST_AUTH_ENABLED__) return <TestAuthProvider>{children}</TestAuthProvider>;
  return <RealAuthProvider>{children}</RealAuthProvider>;
}
