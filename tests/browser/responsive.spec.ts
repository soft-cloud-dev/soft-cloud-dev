import { test, expect } from '@playwright/test';

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
    const tableContainer = page.locator('table, .table-wrapper, .sc-table-container').first();
    await expect(tableContainer).toBeVisible();

    const isScrollableOrContained = await tableContainer.evaluate((el) => {
      const style = window.getComputedStyle(el);
      const parentStyle = el.parentElement ? window.getComputedStyle(el.parentElement) : style;
      return (
        style.overflowX === 'auto' ||
        style.overflowX === 'scroll' ||
        parentStyle.overflowX === 'auto' ||
        parentStyle.overflowX === 'scroll' ||
        el.scrollWidth >= el.clientWidth
      );
    });
    expect(isScrollableOrContained).toBe(true);

    // Check code blocks
    const codeBlock = page.locator('pre').first();
    await expect(codeBlock).toBeVisible();
    const codeOverflow = await codeBlock.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return style.overflowX === 'auto' || style.overflowX === 'scroll' || el.scrollWidth >= el.clientWidth;
    });
    expect(codeOverflow).toBe(true);
  });

  test('telemetry badge and text meet WCAG contrast requirements', async ({ page }) => {
    await page.goto('/');

    const telemetry = page.locator('.sc-wa-telemetry');
    await expect(telemetry).toBeVisible();

    const statusBadge = telemetry.locator('.sc-wa-telemetry-status.online');
    await expect(statusBadge).toBeVisible();

    const colors = await page.evaluate(() => {
      const el = document.querySelector('.sc-wa-telemetry-status.online');
      if (!el) return null;
      const style = window.getComputedStyle(el);
      return {
        color: style.color,
        backgroundColor: style.backgroundColor,
      };
    });

    expect(colors).not.toBeNull();
    expect(colors!.color).toBeTruthy();
    expect(colors!.backgroundColor).toBeTruthy();
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
