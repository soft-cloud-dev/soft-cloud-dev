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
  expect(errors).toEqual([]);
  await page.screenshot({ path: testInfo.outputPath('handbook-desktop.png'), fullPage: true });
});

test('mobile handbook has no horizontal scrolling and retains all primary actions', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const response = await page.goto('/handbook/');
  expect(response?.ok()).toBeTruthy();
  const handbook = page.locator('.sc-handbook');
  await expect(handbook).toBeVisible();
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
    ['/projects/freeipa/', 'FreeIPA Identity & Directory'],
  ] as const) {
    const response = await page.goto(path);
    expect(response?.ok(), path).toBeTruthy();
    await expect(page.getByRole('heading', { name: title, exact: true }).first()).toBeVisible();
  }
});
