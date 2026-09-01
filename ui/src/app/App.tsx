import { QueryClientProvider } from '@tanstack/react-query';
import { Suspense } from 'react';
import { BrowserRouter } from 'react-router-dom';

import { AuthProvider } from '@/shared/auth/AuthProvider';
import { FeatureFlagProvider } from '@/shared/flags/FeatureFlagProvider';
import { queryClient } from '@/shared/query/queryClient';
import { ThemeProvider } from '@/shared/theme/ThemeProvider';
import { ErrorBoundary } from '@/shared/ui/ErrorBoundary';
import { Spinner } from '@/shared/ui/spinner';
import { Toaster } from '@/shared/ui/sonner';
import { TooltipProvider } from '@/shared/ui/tooltip';

import { ViewProvider } from './providers/ViewProvider';
import { AppRoutes } from './routes';

/**
 * The provider tree (§7). Order matters: Router sits ABOVE auth/app-state so those
 * contexts can use useNavigate/useLocation. Toaster is mounted once.
 */
export function App() {
  return (
    <FeatureFlagProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <TooltipProvider>
            <Toaster />
            <BrowserRouter>
              <AuthProvider>
                <ViewProvider>
                  <ErrorBoundary>
                    <Suspense
                      fallback={
                        <div className="flex h-screen items-center justify-center">
                          <Spinner className="h-6 w-6" />
                        </div>
                      }
                    >
                      <AppRoutes />
                    </Suspense>
                  </ErrorBoundary>
                </ViewProvider>
              </AuthProvider>
            </BrowserRouter>
          </TooltipProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </FeatureFlagProvider>
  );
}
