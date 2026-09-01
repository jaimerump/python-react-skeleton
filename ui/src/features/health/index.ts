// Public API of the health slice — the ONLY surface other features/app may import.
export { HealthPage } from './pages/HealthPage';
export { useReadinessQuery } from './queries';
export type { HealthStatus } from './types';
