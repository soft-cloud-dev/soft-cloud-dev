import { test, expect } from '@playwright/test';

test.describe('Canonical Component Contract & Slot Handling (WA-002, WA-003, WA-004, WA-COMP-001 - WA-COMP-004)', () => {
  test('callout titles render in default content slot and not in slot="title"', async ({ page }) => {
    await page.goto('/');

    const callout = page.locator('wa-callout');
    await expect(callout).toBeVisible();

    // Verify zero occurrences of slot="title"
    const titleSlotElements = await page.locator('[slot="title"]').count();
    expect(titleSlotElements).toBe(0);

    // Verify callout title is rendered inside .sc-wa-callout-content > .sc-wa-callout-title
    const title = callout.locator('.sc-wa-callout-content > .sc-wa-callout-title');
    await expect(title).toBeVisible();
    await expect(title).toHaveText('Important Overview');

    // Verify slotted icon
    const icon = callout.locator('wa-icon[slot="icon"]');
    await expect(icon).toBeVisible();
    await expect(icon).toHaveAttribute('name', 'circle-info');
    await expect(icon).toHaveAttribute('aria-hidden', 'true');
  });

  test('card has valid slot presence attributes and canonical appearance', async ({ page }) => {
    await page.goto('/');

    const card = page.locator('wa-card');
    await expect(card).toBeVisible();

    // Verify SSR presence attributes (WA-004)
    await expect(card).toHaveAttribute('with-media', '');
    await expect(card).toHaveAttribute('with-header', '');
    await expect(card).toHaveAttribute('with-footer', '');

    // Verify canonical appearance (WA-003, WA-COMP-004)
    await expect(card).toHaveAttribute('appearance', 'filled-outlined');
    await expect(card).toHaveClass(/sc-elevation/);
    const obsoleteAppearance = await card.getAttribute('appearance');
    expect(obsoleteAppearance).not.toBe('elevated');

    // Verify slotted elements
    const media = card.locator('img[slot="media"]');
    await expect(media).toBeVisible();

    const header = card.locator('div[slot="header"]');
    await expect(header).toBeVisible();
    await expect(header).toHaveText('Card Header Title');

    const footer = card.locator('div[slot="footer"]');
    await expect(footer).toBeVisible();
    await expect(footer).toHaveText('System Operational');
  });

  test('button has canonical variant, appearance, and with-caret attribute', async ({ page }) => {
    await page.goto('/');

    const button = page.locator('wa-button');
    await expect(button).toBeVisible();

    // Verify canonical brand variant and filled appearance
    await expect(button).toHaveAttribute('variant', 'brand');
    await expect(button).toHaveAttribute('appearance', 'filled');

    // Verify caret boolean attribute
    const hasCaret = await button.evaluate((el) => el.hasAttribute('with-caret'));
    expect(hasCaret).toBe(true);

    // Verify obsolete attributes are not emitted
    const variantAttr = await button.getAttribute('variant');
    expect(variantAttr).not.toBe('primary');
  });
});
