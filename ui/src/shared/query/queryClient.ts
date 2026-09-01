import { MutationCache, QueryCache, QueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

/**
 * Named staleTime tiers instead of magic numbers scattered across hooks. Pick the
 * tier that matches how fast the data changes.
 */
export const STALE_TIME = {
  SHORT: 30_000, // frequently changing (members, notifications)
  DEFAULT: 60_000, // most data
  LONG: 5 * 60_000, // analytics, stats
  STATIC: 10 * 60_000, // rarely changing
} as const;

/**
 * Type the `meta.errorMessage` so hooks can set a custom toast string or opt out
 * with `false`. Augments TanStack Query's `Register` interface.
 */
declare module '@tanstack/react-query' {
  interface Register {
    queryMeta: { errorMessage?: string | false };
    mutationMeta: { errorMessage?: string | false };
  }
}

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: STALE_TIME.DEFAULT,
      gcTime: 5 * 60_000,
      retry: 1,
      retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 30_000),
      refetchOnWindowFocus: false, // avoid flashing during auth redirects
    },
    mutations: { retry: 1 },
  },
  // Global error surfacing: each query/mutation opts out or overrides.
  queryCache: new QueryCache({
    onError: (_error, query) => {
      const message = query.meta?.errorMessage;
      if (message === false) return; // silenced
      toast.error(typeof message === 'string' ? message : 'Failed to load data', {
        duration: 8000,
      });
    },
  }),
  mutationCache: new MutationCache({
    onError: (_error, _vars, _ctx, mutation) => {
      // Don't double-toast if the mutation defines its own onError.
      if (mutation.options.onError) return;
      const message = mutation.meta?.errorMessage;
      if (message === false) return;
      toast.error(typeof message === 'string' ? message : 'Something went wrong');
    },
  }),
});
