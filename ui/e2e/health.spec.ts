import { expect, test } from './fixtures';

// Requires the backend running (Vite proxies /api → :8000). Gate live suites
// behind an env flag when they get expensive.
test('health page shows backend status', async ({ healthPage }) => {
  await healthPage.open();
  await expect(healthPage.status).toHaveText('ok');
});
