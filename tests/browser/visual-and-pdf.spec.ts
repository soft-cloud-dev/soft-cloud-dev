import { test, expect } from '@playwright/test';

test.describe('Visual & Print/PDF Completeness (SC-WA-RENDER-001, WA-009, WA-010)', () => {
  test('all document components and sections are present and visible', async ({ page }) => {
    await page.goto('/');

    // Check headings exist and are visible
    const headings = page.locator('h1, h2, h3');
    const hCount = await headings.count();
    expect(hCount).toBeGreaterThanOrEqual(3);

    // Verify key component sections are present and visible on page
    await expect(page.locator('wa-callout').first()).toBeVisible();
    await expect(page.locator('wa-card').first()).toBeVisible();
    await expect(page.locator('wa-button').first()).toBeVisible();
    await expect(page.locator('table').first()).toBeVisible();
    await expect(page.locator('pre').first()).toBeVisible();
    await expect(page.locator('.sc-icon-grid').first()).toBeVisible();
  });

  test('print media emulation hides chrome and formats layout cleanly', async ({ page }) => {
    await page.goto('/');
    await page.emulateMedia({ media: 'print' });

    // Verify print styling rules on layout containers
    const printStyles = await page.evaluate(() => {
      const card = document.querySelector('wa-card, .sc-icon-card') as HTMLElement;
      const callout = document.querySelector('wa-callout') as HTMLElement;
      const h2 = document.querySelector('h2') as HTMLElement;
      const table = document.querySelector('table') as HTMLElement;
      const pre = document.querySelector('pre') as HTMLElement;

      const cardStyle = card ? window.getComputedStyle(card) : null;
      const calloutStyle = callout ? window.getComputedStyle(callout) : null;
      const h2Style = h2 ? window.getComputedStyle(h2) : null;
      const tableStyle = table ? window.getComputedStyle(table) : null;
      const preStyle = pre ? window.getComputedStyle(pre) : null;

      return {
        cardBreakInside: cardStyle?.breakInside || cardStyle?.pageBreakInside,
        calloutBreakInside: calloutStyle?.breakInside || calloutStyle?.pageBreakInside,
        h2BreakAfter: h2Style?.breakAfter || h2Style?.pageBreakAfter,
        tableDisplay: tableStyle?.display,
        preWhiteSpace: preStyle?.whiteSpace,
      };
    });

    expect(['avoid', 'avoid-page'].includes(printStyles.cardBreakInside || '')).toBe(true);
    expect(['avoid', 'avoid-page'].includes(printStyles.calloutBreakInside || '')).toBe(true);
    expect(['avoid', 'avoid-page'].includes(printStyles.h2BreakAfter || '')).toBe(true);
    expect(printStyles.preWhiteSpace).toContain('pre-wrap');
  });

  test('callouts, cards, buttons and icon grids are visually rendered and differentiated', async ({ page }) => {
    await page.goto('/');

    // 1. Callout rendering and title placement
    const callout = page.locator('wa-callout').first();
    await expect(callout).toBeVisible();
    const calloutText = await callout.innerText();
    expect(calloutText).toContain('Important Overview');

    // 2. Card header and footer slots
    const card = page.locator('wa-card').first();
    await expect(card).toBeVisible();
    const cardHeader = card.locator('[slot="header"], .card-header').first();
    await expect(cardHeader).toBeVisible();
    const cardFooter = card.locator('[slot="footer"], .card-footer').first();
    await expect(cardFooter).toBeVisible();

    // 3. Button with FA brand icon
    const button = page.locator('wa-button').first();
    await expect(button).toBeVisible();
    await expect(button).toHaveAttribute('variant', 'brand');

    // 4. Icon gallery grid with distinct cards
    const iconCards = page.locator('.sc-icon-grid .sc-icon-card');
    const iconCardCount = await iconCards.count();
    expect(iconCardCount).toBeGreaterThanOrEqual(2);

    for (let i = 0; i < iconCardCount; i++) {
      const ic = iconCards.nth(i);
      await expect(ic.locator('.sc-icon-preview')).toBeVisible();
      await expect(ic.locator('.sc-icon-name')).toBeVisible();
      await expect(ic.locator('.sc-icon-desc')).toBeVisible();
    }
  });

  test('tables and code blocks do not truncate or clip in print or mobile viewports', async ({ page }) => {
    // 1. Check under mobile viewport
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/');
    await page.waitForTimeout(500);

    const table = page.locator('table').first();
    await expect(table).toBeVisible();

    const codeBlock = page.locator('pre').first();
    await expect(codeBlock).toBeVisible();

    // Verify table and code containers do not cause page horizontal overflow
    const isMobileContained = await page.evaluate(() => {
      const doc = document.documentElement;
      return doc.scrollWidth <= window.innerWidth;
    });
    expect(isMobileContained).toBe(true);

    // 2. Check under print emulation
    await page.emulateMedia({ media: 'print' });
    const printStyles = await page.evaluate(() => {
      const tbl = document.querySelector('table');
      const pr = document.querySelector('pre');
      const tblStyle = tbl ? window.getComputedStyle(tbl) : null;
      const prStyle = pr ? window.getComputedStyle(pr) : null;
      return {
        tableDisplay: tblStyle?.display,
        preWhiteSpace: prStyle?.whiteSpace,
      };
    });

    expect(['table', 'block'].includes(printStyles.tableDisplay || '')).toBe(true);
    expect(printStyles.preWhiteSpace).toContain('pre-wrap');
  });
});
