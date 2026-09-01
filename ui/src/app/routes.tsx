import { lazy } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';

import { ProtectedRoute } from '@/shared/auth/ProtectedRoute';

import { AppLayout } from './AppLayout';

// Lazy-load pages for code-splitting; rendered under one <Suspense> in App.tsx.
const HealthPage = lazy(() =>
  import('@/features/health').then((m) => ({ default: m.HealthPage })),
);
const LoginPage = lazy(() =>
  import('./pages/LoginPage').then((m) => ({ default: m.LoginPage })),
);

/** The route table. Guard wrappers (ProtectedRoute, role guards) live here. */
export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<AppLayout />}>
        <Route index element={<HealthPage />} />
        {/* Example of a guarded route; the guard redirects to /login when logged out. */}
        <Route
          path="account"
          element={
            <ProtectedRoute>
              <div className="p-8">Account (protected)</div>
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
