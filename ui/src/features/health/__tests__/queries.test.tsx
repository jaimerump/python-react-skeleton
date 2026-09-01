import { afterEach, describe, expect, it, vi } from 'vitest';

import { renderWithProviders, screen, waitFor } from '@/test/test-utils';

import { HealthPage } from '../pages/HealthPage';

afterEach(() => {
  vi.restoreAllMocks();
});

describe('HealthPage', () => {
  it('renders the readiness status from the API', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ status: 'ok' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      ),
    );

    renderWithProviders(<HealthPage />);

    await waitFor(() => {
      expect(screen.getByTestId('health-status')).toHaveTextContent('ok');
    });
    expect(fetch).toHaveBeenCalledWith('/api/ready', expect.objectContaining({ method: 'GET' }));
  });

  it('shows an error state when the API is unreachable', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: { message: 'down', error_code: 'internal_error' } }), {
          status: 503,
          headers: { 'Content-Type': 'application/json' },
        }),
      ),
    );

    renderWithProviders(<HealthPage />);

    await waitFor(() => {
      expect(screen.getByText('Unreachable')).toBeInTheDocument();
    });
  });
});
