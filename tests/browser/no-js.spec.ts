import { test, expect } from '@playwright/test';

test.describe('No-JavaScript SSR Readability', () => {
  test.use({ javaScriptEnabled: false });

  test('renders readable content inside Web Awesome components when JS is disabled', async ({ page }) => {
    await page.goto('/');

    // 1. Verify callout is readable
    const callout = page.locator('wa-callout');
    await expect(callout).toBeVisible();
    await expect(callout).toContainText('Important Overview');
    await expect(callout).toContainText('informational callout');

    // 2. Verify card content is readable
    const card = page.locator('wa-card');
    await expect(card).toBeVisible();
    await expect(card.locator('h2')).toContainText('Nested Heading in Card');
    await expect(card.locator('li').first()).toContainText('First item');

    // 3. Verify button content and link are readable and interactive via HTML
    const button = page.locator('wa-button');
    await expect(button).toBeVisible();
    await expect(button).toContainText('Launch Console');
    await expect(button).toHaveAttribute('href', 'https://my.softcloud.dev/get-started');

    // 4. Verify no flash of broken tags or hidden light DOM
    const calloutDisplay = await callout.evaluate((el) => window.getComputedStyle(el).display);
    expect(calloutDisplay).not.toBe('none');

    const cardDisplay = await card.evaluate((el) => window.getComputedStyle(el).display);
    expect(cardDisplay).not.toBe('none');
  });
});
