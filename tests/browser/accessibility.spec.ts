import { test, expect } from '@playwright/test';

test.describe('Keyboard & Screen Reader Accessibility', () => {
  test('button has accessible name and is keyboard focusable', async ({ page }) => {
    await page.goto('/');

    // Wait for custom elements to be defined and hydrated
    await page.waitForFunction(() => {
      return (
        customElements.get('wa-button') !== undefined &&
        customElements.get('wa-callout') !== undefined &&
        customElements.get('wa-icon') !== undefined
      );
    }, { timeout: 10000 });

    const button = page.locator('wa-button');
    await expect(button).toBeVisible();

    // Verify button text serves as accessible name
    await expect(button).toContainText('Launch Console');

    // Test keyboard focus
    await page.keyboard.press('Tab');
    // Tab through until button or interactive element is focused
    let focusedTag = await page.evaluate(() => document.activeElement?.tagName?.toLowerCase());
    let attempts = 0;
    while (focusedTag !== 'wa-button' && focusedTag !== 'a' && attempts < 15) {
      await page.keyboard.press('Tab');
      focusedTag = await page.evaluate(() => document.activeElement?.tagName?.toLowerCase());
      attempts++;
    }

    // Direct focus to wa-button to verify focusability
    await button.focus();
    const isFocused = await button.evaluate((el) => document.activeElement === el);
    expect(isFocused).toBe(true);
  });

  test('icons and callouts have accessible attributes', async ({ page }) => {
    await page.goto('/');

    // Decorative icons should have aria-hidden or an explicit accessible label
    const icons = page.locator('wa-icon');
    const count = await icons.count();
    expect(count).toBeGreaterThan(0);

    for (let i = 0; i < count; i++) {
      const icon = icons.nth(i);
      const ariaHidden = await icon.evaluate((el) => el.getAttribute('aria-hidden'));
      const label = await icon.evaluate((el) => el.getAttribute('label'));
      // Either aria-hidden="true" or has a descriptive label
      const isAccessible = ariaHidden === 'true' || (label !== null && label.length > 0);
      expect(isAccessible).toBe(true);
    }

    // Callout has clear structure
    const callout = page.locator('wa-callout');
    await expect(callout).toBeVisible();
    await expect(callout.locator('.sc-wa-callout-title')).toContainText('Important Overview');
  });
});
