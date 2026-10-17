import { test, expect } from '@playwright/test';

test.describe('Web Awesome SSR Rendering & DSD', () => {
  test('renders all Web Awesome components with Declarative Shadow DOM', async ({ page }) => {
    const response = await page.goto('/');
    const serverHtml = (await response?.text()) || '';

    // Verify did-ssr attributes and DSD templates exist in server-rendered HTML
    expect(serverHtml).toMatch(/<wa-callout[^>]*\bdid-ssr\b/);
    expect(serverHtml).toMatch(/<wa-card[^>]*\bdid-ssr\b/);
    expect(serverHtml).toMatch(/<wa-button[^>]*\bdid-ssr\b/);
    expect(serverHtml).toMatch(/<wa-icon[^>]*\bdid-ssr\b/);
    expect(serverHtml).toMatch(/<template[^>]*\b(shadowrootmode|shadowroot)="open"/);

    // 1. Verify Callout component
    const callout = page.locator('wa-callout');
    await expect(callout).toBeVisible();
    await expect(callout).toHaveAttribute('variant', 'brand');
    await expect(callout).toHaveAttribute('appearance', 'filled-outlined');

    // Verify shadow root on wa-callout
    const hasCalloutShadowRoot = await callout.evaluate((el) => !!el.shadowRoot);
    expect(hasCalloutShadowRoot).toBe(true);

    // Verify callout slotted / light DOM content
    await expect(callout).toContainText('Important Overview');
    await expect(callout).toContainText('informational callout');

    // 2. Verify Card component
    const card = page.locator('wa-card');
    await expect(card).toBeVisible();
    await expect(card).toHaveAttribute('appearance', 'filled-outlined');
    await expect(card).toHaveClass(/sc-elevation/);

    const hasCardShadowRoot = await card.evaluate((el) => !!el.shadowRoot);
    expect(hasCardShadowRoot).toBe(true);

    // Verify card content
    await expect(card.locator('h2')).toContainText('Nested Heading in Card');
    await expect(card.locator('li').first()).toContainText('First item');

    // 3. Verify Button component
    const button = page.locator('wa-button');
    await expect(button).toBeVisible();
    await expect(button).toHaveAttribute('variant', 'brand');
    await expect(button).toHaveAttribute('href', 'https://my.softcloud.dev/get-started');

    const hasButtonShadowRoot = await button.evaluate((el) => !!el.shadowRoot);
    expect(hasButtonShadowRoot).toBe(true);
    await expect(button).toContainText('Launch Console');

    // 4. Verify Icon components
    const icons = page.locator('wa-icon');
    const iconCount = await icons.count();
    expect(iconCount).toBeGreaterThanOrEqual(3);

    for (let i = 0; i < iconCount; i++) {
      const icon = icons.nth(i);
      const hasIconShadowRoot = await icon.evaluate((el) => !!el.shadowRoot);
      expect(hasIconShadowRoot).toBe(true);
    }
  });

  test('no unresolved placeholders or meta elements exist in DOM', async ({ page }) => {
    await page.goto('/');

    const hosts = await page.locator('.sc-wa-host').count();
    expect(hosts).toBe(0);

    const metas = await page.locator('.sc-wa-meta').count();
    expect(metas).toBe(0);
  });
});
