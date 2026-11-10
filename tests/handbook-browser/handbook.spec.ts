import { test, expect } from '@playwright/test';

test('handbook presents task-based navigation and authentic verification framing', async ({ page }, testInfo) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  const response = await page.goto('/handbook/');
  expect(response?.ok()).toBeTruthy();

  const handbook = page.locator('.sc-handbook');
  await expect(handbook).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Engineering knowledge you can reproduce.' })).toBeVisible();
  await expect(handbook.locator('.sc-handbook__route')).toHaveCount(3);
  await expect(handbook.getByRole('link', { name: 'Start with a guide' })).toBeVisible();
  await expect(handbook.getByRole('link', { name: 'Browse notebooks' })).toBeVisible();
  await expect(handbook.getByRole('link', { name: 'Open verification notebook' })).toBeVisible();
  await expect(handbook.getByText('Required execution profile')).toBeVisible();

  const grid = await handbook.locator('.sc-handbook__hero').evaluate(el => getComputedStyle(el).display);
  expect(grid).toBe('grid');
  const contentWidth = await handbook.evaluate(el => el.getBoundingClientRect().width);
  expect(contentWidth).toBeGreaterThan(900);

  const headlineSize = await handbook.locator('.sc-handbook__intro h2').evaluate(el =>
    parseFloat(getComputedStyle(el).fontSize)
  );
  expect(headlineSize).toBeGreaterThanOrEqual(42);

  const firstCta = handbook.locator('.sc-handbook__intro > p:last-of-type > span:first-child a');
  const secondCta = handbook.locator('.sc-handbook__intro > p:last-of-type > span:not(:first-child) a');
  const primaryBackground = await firstCta.evaluate(el => getComputedStyle(el).backgroundColor);
  const secondaryBackground = await secondCta.evaluate(el => getComputedStyle(el).backgroundColor);
  expect(primaryBackground).not.toBe(secondaryBackground);

  const routeIcon = await handbook.locator('.sc-handbook__route--guide').evaluate(el =>
    getComputedStyle(el, '::after').maskImage
  );
  expect(routeIcon).toContain('file-lines.svg');
  expect(errors).toEqual([]);
  await page.screenshot({ path: testInfo.outputPath('handbook-desktop.png'), fullPage: true });
});

test('mobile handbook has no horizontal scrolling and retains all primary actions', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const response = await page.goto('/handbook/');
  expect(response?.ok()).toBeTruthy();
  const handbook = page.locator('.sc-handbook');
  await expect(handbook).toBeVisible();
  const mobileBrand = await page.evaluate(() => {
    const selectors = [
      '.myst-top-nav-bar',
      '.myst-top-nav-bar > div:first-child',
      '.myst-home-link',
      '.myst-home-link-logo',
      '.myst-home-link-logo img:first-child',
      '.myst-home-link-logo img:last-child',
      '.myst-top-nav-menu-button'
    ];
    return selectors.map(selector => {
      const el = document.querySelector(selector);
      if (!el) return { selector, exists: false };
      const computed = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return {
        selector, exists: true, tag: el.tagName,
        display: computed.display, visibility: computed.visibility,
        opacity: computed.opacity, width: rect.width, height: rect.height,
        x: rect.x, y: rect.y,
        naturalWidth: el instanceof HTMLImageElement ? el.naturalWidth : undefined,
        src: el instanceof HTMLImageElement ? el.getAttribute('src') : undefined
      };
    });
  });
  console.log('HANDBOOK_MOBILE_BRAND_DIAGNOSTIC', JSON.stringify(mobileBrand));
  await expect(page.locator('.myst-top-nav-bar .myst-home-link img:visible').first()).toBeVisible();
  await expect(handbook.locator('.sc-handbook__route')).toHaveCount(3);
  const fits = await page.evaluate(() =>
    document.documentElement.scrollWidth <= window.innerWidth + 2
  );
  expect(fits).toBeTruthy();
  await expect(handbook.getByRole('link', { name: 'Start with a guide' })).toBeVisible();
  await expect(handbook.getByRole('link', { name: 'Explore SoftCloud projects' })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath('handbook-mobile.png'), fullPage: true });
});

test('core handbook routes resolve through the compiled publication', async ({ page }) => {
  for (const [path, title] of [
    ['/guides/', 'Guides'],
    ['/notebooks/', 'Computational Notebooks'],
    ['/projects/', 'Systems & Laboratories'],
    ['/freeipa/', 'FreeIPA Identity & Directory'],
  ] as const) {
    const response = await page.goto(path);
    expect(response?.ok(), path).toBeTruthy();
    await expect(page.getByRole('heading', { name: title, exact: true }).first()).toBeVisible();
  }
});
