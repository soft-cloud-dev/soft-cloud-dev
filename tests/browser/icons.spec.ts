import { test, expect } from '@playwright/test';

test.describe('Font Awesome & Web Awesome Icon Integration (WA-001, WA-ICON-001, WA-ICON-002, WA-ICON-003)', () => {
  test('all icons resolve locally without any external CDN requests', async ({ page }) => {
    const externalIconRequests: string[] = [];
    const localSvgRequests: string[] = [];

    page.on('request', (request) => {
      const url = request.url();
      if (
        url.includes('fontawesome.com') ||
        url.includes('ka-p.fontawesome.com') ||
        url.includes('kit.fontawesome.com') ||
        (url.includes('svgs/') && !url.includes('127.0.0.1:4173') && !url.includes('localhost:4173'))
      ) {
        externalIconRequests.push(url);
      }
      if (url.includes('/vendor/fontawesome/svgs/')) {
        localSvgRequests.push(url);
      }
    });

    await page.goto('/');

    // Wait for custom elements to define and load icons
    await page.waitForFunction(() => customElements.get('wa-icon') !== undefined, null, { timeout: 10000 });
    await page.waitForTimeout(500);

    // Assert zero external icon requests were made
    expect(externalIconRequests).toEqual([]);

    // Assert that Font Awesome SVGs were fetched from local staged vendor assets
    expect(localSvgRequests.length).toBeGreaterThanOrEqual(4);
    for (const req of localSvgRequests) {
      expect(req).toMatch(/\/vendor\/fontawesome\/svgs\/(solid|regular|brands)\/[\w-]+\.svg/);
    }

    // Check all wa-icon elements
    const icons = page.locator('wa-icon');
    const count = await icons.count();
    expect(count).toBeGreaterThanOrEqual(4);

    for (let i = 0; i < count; i++) {
      const icon = icons.nth(i);
      await expect(icon).toBeVisible();

      // Check rendered bounding box > 0
      const box = await icon.boundingBox();
      expect(box).not.toBeNull();
      expect(box!.width).toBeGreaterThan(0);
      expect(box!.height).toBeGreaterThan(0);

      // Verify shadow root contains SVG
      const hasSvg = await icon.evaluate((el) => {
        return !!el.shadowRoot?.querySelector('svg');
      });
      expect(hasSvg).toBe(true);
    }
  });

  test('verifies classic solid, classic regular, and brand icon families', async ({ page }) => {
    await page.goto('/');
    await page.waitForFunction(() => customElements.get('wa-icon') !== undefined, null, { timeout: 10000 });

    const solidIcon = page.locator('wa-icon[name="terminal"], wa-icon[name="rocket"]').first();
    await expect(solidIcon).toBeVisible();
    await expect(solidIcon).toHaveAttribute('family', 'classic');

    const brandIcon = page.locator('wa-icon[name="github"]').first();
    await expect(brandIcon).toBeVisible();
    await expect(brandIcon).toHaveAttribute('family', 'brands');

    const regularIcon = page.locator('wa-icon[name="circle-check"]');
    await expect(regularIcon).toBeVisible();
    await expect(regularIcon).toHaveAttribute('variant', 'regular');
  });
});
