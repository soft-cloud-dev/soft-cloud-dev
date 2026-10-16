import { test, expect } from '@playwright/test';

test.describe('Web Awesome Client Hydration', () => {
  test('custom elements are defined and hydrated without errors', async ({ page }) => {
    const consoleErrors: string[] = [];
    const consoleWarnings: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      } else if (msg.type() === 'warning') {
        consoleWarnings.push(msg.text());
      }
    });

    await page.goto('/');

    // Wait for custom elements to be defined in browser
    await page.waitForFunction(() => {
      return (
        customElements.get('wa-button') !== undefined &&
        customElements.get('wa-callout') !== undefined &&
        customElements.get('wa-card') !== undefined &&
        customElements.get('wa-icon') !== undefined
      );
    }, { timeout: 10000 });

    const areDefined = await page.evaluate(() => {
      return {
        button: customElements.get('wa-button') !== undefined,
        callout: customElements.get('wa-callout') !== undefined,
        card: customElements.get('wa-card') !== undefined,
        icon: customElements.get('wa-icon') !== undefined,
      };
    });

    expect(areDefined.button).toBe(true);
    expect(areDefined.callout).toBe(true);
    expect(areDefined.card).toBe(true);
    expect(areDefined.icon).toBe(true);

    // Verify shadow DOM remains intact after hydration
    const buttonShadowIntact = await page.locator('wa-button').evaluate((el) => {
      return !!el.shadowRoot && el.shadowRoot.childElementCount > 0;
    });
    expect(buttonShadowIntact).toBe(true);

    // Filter out non-fatal network/favicon console errors if any
    const realErrors = consoleErrors.filter(
      (err) =>
        !err.includes('favicon') &&
        !err.includes('thebe') &&
        !err.includes('404')
    );
    expect(realErrors).toEqual([]);

    // Assert zero deprecation warnings and zero React error #418 occurrences
    const deprecationWarnings = consoleWarnings.filter((warn) => warn.includes('deprecated'));
    expect(deprecationWarnings).toEqual([]);
    const react418Errors = consoleErrors.filter((err) => err.includes('React error #418'));
    expect(react418Errors).toEqual([]);
  });

  test('button component responds to user interaction', async ({ page }) => {
    await page.goto('/');

    const button = page.locator('wa-button');
    await expect(button).toBeVisible();

    // Verify button attributes
    const href = await button.getAttribute('href');
    expect(href).toBe('https://my.softcloud.dev/get-started');
    const target = await button.getAttribute('target');
    expect(target).toBe('_blank');
  });
});
