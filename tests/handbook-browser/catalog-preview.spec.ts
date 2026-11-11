import { test, expect } from '@playwright/test';

test.describe('Web Awesome catalog preview', () => {
  for (const width of [390, 1280]) {
    test(`progress bar renders an accessible, full-width track at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      const response = await page.goto('/components/feedback/progress-bar/');
      expect(response?.ok()).toBeTruthy();

      const frame = page.locator('.sc-wa-showcase').first();
      const progress = frame.locator(':scope > wa-progress-bar');
      await expect(frame).toBeVisible();
      await expect(progress).toBeVisible();
      await expect(progress).toHaveAttribute('value', '64');

      const track = progress.locator('[role="progressbar"]');
      await expect(track).toHaveAttribute('aria-label', 'Deployment progress');
      await expect(track).toHaveAttribute('aria-valuenow', '64');
      await expect(track).toHaveText('64%');

      const dimensions = await progress.evaluate(el => {
        const host = el.getBoundingClientRect();
        const container = el.parentElement!.getBoundingClientRect();
        const track = el.shadowRoot!.querySelector('[role="progressbar"]')!.getBoundingClientRect();
        return {
          hostWidth: host.width,
          containerWidth: container.width,
          trackWidth: track.width,
          trackHeight: track.height,
        };
      });
      expect(dimensions.hostWidth).toBeGreaterThan(120);
      expect(dimensions.hostWidth).toBeGreaterThan(dimensions.containerWidth * 0.7);
      expect(dimensions.trackWidth).toBeGreaterThan(120);
      expect(dimensions.trackHeight).toBeGreaterThan(0);

      const nextHeading = page.getByRole('heading', { name: 'Markdown code snippet' });
      const gap = await nextHeading.evaluate(el => {
        const preview = document.querySelector('.sc-wa-showcase')!;
        return el.getBoundingClientRect().top - preview.getBoundingClientRect().bottom;
      });
      expect(gap).toBeGreaterThanOrEqual(12);

      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 2)).toBeTruthy();
    });
  }
});
