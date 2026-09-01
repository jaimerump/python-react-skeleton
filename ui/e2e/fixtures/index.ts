import { test as base } from '@playwright/test';

import { HealthPage } from '../pages/HealthPage';

/**
 * Extends Playwright's `test` with Page Objects (and, later, auth/api-helpers/
 * test-data fixtures). Import `{ test, expect }` from here in specs.
 */
interface Fixtures {
  healthPage: HealthPage;
}

export const test = base.extend<Fixtures>({
  healthPage: async ({ page }, use) => {
    await use(new HealthPage(page));
  },
});

export { expect } from '@playwright/test';
