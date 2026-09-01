import type { Locator, Page } from '@playwright/test';

import { BasePage } from './BasePage';

/** Page Object for the health screen (index route). */
export class HealthPage extends BasePage {
  readonly status: Locator;

  constructor(page: Page) {
    super(page);
    this.status = page.getByTestId('health-status');
  }

  async open() {
    await this.goto('/');
  }
}
