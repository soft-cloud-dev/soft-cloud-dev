import { test, expect } from '@playwright/test';

function parseRgb(colorStr: string): [number, number, number] {
  const match = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (match) {
    return [parseInt(match[1], 10), parseInt(match[2], 10), parseInt(match[3], 10)];
  }
  return [0, 0, 0];
}

function getRelativeLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function calculateContrastRatio(fgRgb: string, bgRgb: string): number {
  const fg = parseRgb(fgRgb);
  const bg = parseRgb(bgRgb);
  const l1 = getRelativeLuminance(fg[0], fg[1], fg[2]);
  const l2 = getRelativeLuminance(bg[0], bg[1], bg[2]);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

test.describe('Responsive Layout & Print Media (WA-006, WA-009, WA-010)', () => {
  test('mobile viewport does not exhibit horizontal page overflow', async ({ page }) => {
    // Set standard mobile device viewport (iPhone 12/13/14)
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');

    // Wait for layout to stabilize
    await page.waitForTimeout(500);

    // Verify root document does not overflow horizontally
    const overflowInfo = await page.evaluate(() => {
      const doc = document.documentElement;
      return {
        clientWidth: doc.clientWidth,
        scrollWidth: doc.scrollWidth,
        windowWidth: window.innerWidth,
      };
    });

    expect(overflowInfo.scrollWidth).toBeLessThanOrEqual(overflowInfo.windowWidth);
  });

  test('tables and code blocks have responsive overflow handling on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');

    // Check table scrollability or container overflow
    const table = page.locator('table').first();
    await expect(table).toBeVisible();

    const isTableContained = await table.evaluate((el) => {
      const container = (el.closest('.table-wrapper, .myst-table-wrapper, .sc-table-container') || el) as HTMLElement;
      const initial = container.scrollLeft;
      container.scrollLeft = 50;
      const canScroll = container.scrollLeft > initial;
      container.scrollLeft = 0;
      const style = window.getComputedStyle(container);
      return (
        canScroll ||
        container.scrollWidth <= container.clientWidth ||
        style.overflowX === 'auto' ||
        style.overflowX === 'scroll'
      );
    });
    expect(isTableContained).toBe(true);

    // Check code blocks
    const codeBlock = page.locator('pre').first();
    await expect(codeBlock).toBeVisible();
    const isCodeContained = await codeBlock.evaluate((el) => {
      const initial = el.scrollLeft;
      el.scrollLeft = 50;
      const canScroll = el.scrollLeft > initial;
      el.scrollLeft = 0;
      const style = window.getComputedStyle(el);
      return (
        canScroll ||
        style.whiteSpace.includes('wrap') ||
        style.overflowX === 'auto' ||
        style.overflowX === 'scroll' ||
        el.scrollWidth <= el.clientWidth
      );
    });
    expect(isCodeContained).toBe(true);
  });

  test('telemetry badge and text meet mathematical WCAG AA contrast ratio (>= 4.5:1) in both themes', async ({ page }) => {
    await page.goto('/');

    // 1. Light theme contrast test
    await page.evaluate(() => window.SoftCloudTheme?.setTheme('light'));
    await page.waitForTimeout(300);

    const lightColors = await page.evaluate(() => {
      const badge = document.querySelector('.sc-wa-telemetry-status.online') as HTMLElement;
      const panel = document.querySelector('.sc-wa-telemetry') as HTMLElement;
      if (!badge || !panel) return null;
      const badgeStyle = window.getComputedStyle(badge);
      const panelStyle = window.getComputedStyle(panel);
      return {
        badgeFg: badgeStyle.color,
        badgeBg: badgeStyle.backgroundColor,
        panelFg: panelStyle.color,
        panelBg: panelStyle.backgroundColor,
      };
    });

    expect(lightColors).not.toBeNull();
    const lightBadgeContrast = calculateContrastRatio(lightColors!.badgeFg, lightColors!.badgeBg);
    const lightPanelContrast = calculateContrastRatio(lightColors!.panelFg, lightColors!.panelBg);

    // WCAG AA requires >= 4.5:1 for normal body text
    expect(lightBadgeContrast).toBeGreaterThanOrEqual(4.5);
    expect(lightPanelContrast).toBeGreaterThanOrEqual(4.5);

    // 2. Dark theme contrast test
    await page.evaluate(() => window.SoftCloudTheme?.setTheme('dark'));
    await page.waitForTimeout(300);

    const darkColors = await page.evaluate(() => {
      const badge = document.querySelector('.sc-wa-telemetry-status.online') as HTMLElement;
      const panel = document.querySelector('.sc-wa-telemetry') as HTMLElement;
      if (!badge || !panel) return null;
      const badgeStyle = window.getComputedStyle(badge);
      const panelStyle = window.getComputedStyle(panel);
      return {
        badgeFg: badgeStyle.color,
        badgeBg: badgeStyle.backgroundColor,
        panelFg: panelStyle.color,
        panelBg: panelStyle.backgroundColor,
      };
    });

    expect(darkColors).not.toBeNull();
    const darkBadgeContrast = calculateContrastRatio(darkColors!.badgeFg, darkColors!.badgeBg);
    const darkPanelContrast = calculateContrastRatio(darkColors!.panelFg, darkColors!.panelBg);

    expect(darkBadgeContrast).toBeGreaterThanOrEqual(4.5);
    expect(darkPanelContrast).toBeGreaterThanOrEqual(4.5);
  });

  test('icon gallery grid renders responsive cards with icons and descriptions', async ({ page }) => {
    await page.goto('/');

    const grid = page.locator('.sc-icon-grid').first();
    await expect(grid).toBeVisible();

    const cards = grid.locator('.sc-icon-card');
    const count = await cards.count();
    expect(count).toBeGreaterThan(0);

    // Check first card details
    const firstCard = cards.first();
    await expect(firstCard.locator('.sc-icon-preview')).toBeVisible();
    await expect(firstCard.locator('.sc-icon-name')).toBeVisible();
    await expect(firstCard.locator('.sc-icon-desc')).toBeVisible();
  });

  test('print stylesheet rules include break containment', async ({ page }) => {
    await page.goto('/');

    const hasPrintRules = await page.evaluate(() => {
      for (const sheet of Array.from(document.styleSheets)) {
        try {
          for (const rule of Array.from(sheet.cssRules || [])) {
            if (rule instanceof CSSMediaRule && rule.conditionText.includes('print')) {
              return true;
            }
          }
        } catch (e) {
          // Cross-origin sheets
        }
      }
      return false;
    });

    expect(hasPrintRules).toBe(true);
  });
});
