import { useQuery } from '@tanstack/react-query';

import { queryKeys } from '@/shared/query/queryKeys';
import { STALE_TIME } from '@/shared/query/queryClient';

import { healthApi } from './api';

/** Readiness (backend + DB reachable). Key from the factory + typed error toast. */
export function useReadinessQuery() {
  return useQuery({
    queryKey: queryKeys.health.ready(),
    queryFn: () => healthApi.readiness(),
    staleTime: STALE_TIME.SHORT,
    meta: { errorMessage: 'Failed to reach the backend' },
  });
}
