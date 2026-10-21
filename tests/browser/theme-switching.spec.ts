import { test, expect } from '@playwright/test';

test.describe('Theme Switching & Appearance', () => {
  test('initializes SoftCloud theme and allows dynamic switching', async ({ page }) => {
    await page.goto('/');

    // Ensure page and theme API are fully initialized
    await page.waitForFunction(() => typeof window.SoftCloudTheme === 'object' && document.readyState === 'complete');

    // Check window.SoftCloudTheme availability
    const hasThemeApi = await page.evaluate(() => typeof window.SoftCloudTheme === 'object');
    expect(hasThemeApi).toBe(true);

    // Switch to dark theme
    await page.evaluate(() => window.SoftCloudTheme.setTheme('dark'));
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
    await expect(page.locator('html')).toHaveClass(/dark/);

    // Switch to light theme
    await page.evaluate(() => window.SoftCloudTheme.setTheme('light'));
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
    await expect(page.locator('html')).not.toHaveClass(/dark/);

    // Switch to auto theme
    await page.evaluate(() => window.SoftCloudTheme.setTheme('auto'));
    const stored = await page.evaluate(() => localStorage.getItem('softcloud-theme'));
    expect(stored).toBe('auto');
  });

  test('applies Web Awesome theme variables and SoftCloud CSS styling', async ({ page }) => {
    await page.goto('/');

    const stylesLoaded = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
      return {
        softcloud: links.some((l) => l.href.includes('softcloud.css')),
        webawesome: links.some((l) => l.href.includes('webawesome.css')),
        fontawesome: links.some((l) => l.href.includes('all.min.css') || l.href.includes('font-awesome')),
      };
    });

    expect(stylesLoaded.softcloud).toBe(true);
    expect(stylesLoaded.webawesome).toBe(true);
    expect(stylesLoaded.fontawesome).toBe(true);
  });
});
