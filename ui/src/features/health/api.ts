import { fetchApi } from '@/shared/api/core';

import type { HealthStatus } from './types';

/**
 * Tier 2: the domain's typed API module — thin fns over the shared fetch wrapper.
 * Paths are relative to the /api base; the dev proxy strips /api so `/ready`
 * reaches the backend's root `/ready`.
 */
export const healthApi = {
  liveness: () => fetchApi<HealthStatus>('/health'),
  readiness: () => fetchApi<HealthStatus>('/ready'),
};
