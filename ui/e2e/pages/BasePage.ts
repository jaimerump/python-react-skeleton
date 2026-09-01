import type { Locator, Page } from '@playwright/test';

/** Shared page behavior and locators for every screen's Page Object. */
export class BasePage {
  readonly toast: Locator;
  readonly spinner: Locator;

  constructor(protected readonly page: Page) {
    // Sonner renders toasts in a region; spinners carry role="status".
    this.toast = page.locator('[data-sonner-toast]');
    this.spinner = page.getByRole('status');
  }

  async goto(path = '/') {
    await this.page.goto(path);
  }
}
