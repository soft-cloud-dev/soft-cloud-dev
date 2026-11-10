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

  test('repeated and DOM-driven theme toggling preserves coordinated surface and text contrast', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });
    await page.waitForFunction(() => typeof window.SoftCloudTheme === 'object' && document.readyState === 'complete');

    function parseRgb(str: string): [number, number, number] {
      const m = str.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      return m ? [parseInt(m[1], 10), parseInt(m[2], 10), parseInt(m[3], 10)] : [0, 0, 0];
    }
    function lum([r, g, b]: [number, number, number]): number {
      const [rs, gs, bs] = [r, g, b].map((c) => {
        const s = c / 255;
        return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    }
    function contrast(fg: string, bg: string): number {
      const l1 = lum(parseRgb(fg));
      const l2 = lum(parseRgb(bg));
      return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    }

    const readProbe = async () =>
      page.evaluate(() => {
        let probe = document.getElementById('sc-token-contrast-probe');
        if (!probe) {
          probe = document.createElement('div');
          probe.id = 'sc-token-contrast-probe';
          probe.style.cssText =
            'border: 1px solid var(--wa-color-surface-border, #e4e5e9);' +
            'background: var(--wa-color-surface-raised, #ffffff);' +
            'color: var(--wa-color-text-normal, #1b1d26);';
          probe.innerHTML =
            '<span class="wa-color-text-normal">Web Awesome Token Architecture</span>' +
            '<span class="wa-color-text-quiet" style="color: var(--wa-color-text-quiet, #545868);">Quiet</span>';
          (document.querySelector('main') || document.body).appendChild(probe);
        }
        const quiet = probe.querySelector('.wa-color-text-quiet')!;
        const cs = getComputedStyle(probe);
        const qcs = getComputedStyle(quiet);
        return {
          htmlClass: document.documentElement.className,
          bg: cs.backgroundColor,
          fg: cs.color,
          quietFg: qcs.color,
        };
      });

    // Rapid repeated toggling via SoftCloudTheme API
    for (const mode of ['dark', 'light', 'dark', 'light'] as const) {
      await page.evaluate((m) => window.SoftCloudTheme.setTheme(m), mode);
      await page.waitForTimeout(50);
      const res = await readProbe();
      expect(contrast(res.fg, res.bg)).toBeGreaterThanOrEqual(4.5);
      expect(contrast(res.quietFg, res.bg)).toBeGreaterThanOrEqual(4.5);
    }

    // Simulate MyST toggle mutating html.classList after SoftCloudTheme.setTheme('dark')
    await page.evaluate(() => window.SoftCloudTheme.setTheme('dark'));
    await page.evaluate(() => {
      const root = document.documentElement;
      root.classList.remove('dark');
      root.classList.add('light');
    });
    // Immediate synchronous check (transient window before MutationObserver settles)
    const transient = await readProbe();
    expect(contrast(transient.fg, transient.bg)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(transient.quietFg, transient.bg)).toBeGreaterThanOrEqual(4.5);

    // After observer runs, wa-light must be synced (not reverted back to dark)
    await page.waitForTimeout(50);
    await expect(page.locator('html')).toHaveClass(/wa-light/);
    await expect(page.locator('html')).not.toHaveClass(/wa-dark/);
    const settled = await readProbe();
    expect(contrast(settled.fg, settled.bg)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(settled.quietFg, settled.bg)).toBeGreaterThanOrEqual(4.5);
  });
});
