import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';
import { Spinner } from '@/shared/ui/spinner';

import { useReadinessQuery } from '../queries';

/**
 * Route-level screen for the health slice. Exercises the full stack:
 * fetch wrapper → api → query → component, against the backend's /ready.
 */
export function HealthPage() {
  const { data, isLoading, isError } = useReadinessQuery();

  return (
    <div className="mx-auto max-w-md p-8">
      <Card>
        <CardHeader>
          <CardTitle>Backend status</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <span className="flex items-center gap-2 text-muted-foreground">
              <Spinner /> Checking…
            </span>
          )}
          {isError && <span className="text-destructive">Unreachable</span>}
          {data && (
            <span className="font-medium text-foreground" data-testid="health-status">
              {data.status}
            </span>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
