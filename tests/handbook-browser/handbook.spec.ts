import { test, expect } from '@playwright/test';

const locales = [
  { code: 'en', prefix: '', headline: 'Engineering knowledge you can reproduce.', nav: ['Guides', 'Notebooks', 'UI Library', 'Projects'], cta: 'Start with a guide' },
  { code: 'pl', prefix: '/pl', headline: 'Wiedza inżynierska, którą można odtworzyć.', nav: ['Poradniki', 'Notatniki', 'Biblioteka UI', 'Projekty'], cta: 'Rozpocznij od poradnika' },
  { code: 'de', prefix: '/de', headline: 'Ingenieurwissen, das sich reproduzieren lässt.', nav: ['Anleitungen', 'Notebooks', 'UI-Bibliothek', 'Projekte'], cta: 'Mit einer Anleitung beginnen' },
  { code: 'es', prefix: '/es', headline: 'Conocimiento de ingeniería reproducible.', nav: ['Guías', 'Cuadernos', 'Biblioteca UI', 'Proyectos'], cta: 'Empezar con una guía' },
  { code: 'fr', prefix: '/fr', headline: "Un savoir d'ingénierie reproductible.", nav: ['Guides', 'Notebooks', 'Bibliothèque UI', 'Projets'], cta: 'Commencer par un guide' },
] as const;

const slugs = ['guides', 'notebooks', 'ui-library', 'projects'] as const;

for (const locale of locales) {
  test(locale.code + ' homepage and locale-aware navigation links', async ({ page }, testInfo) => {
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.setViewportSize({ width: 1440, height: 900 });
    const response = await page.goto(locale.prefix + '/');
    expect(response?.ok()).toBeTruthy();
    await expect(page.locator('html')).toHaveAttribute('lang', locale.code);
    const root = page.locator('.sc-handbook');
    await expect(root).toBeVisible();
    await expect(root.getByRole('heading', { name: locale.headline })).toBeVisible();
    await expect(root.locator('.sc-handbook__route')).toHaveCount(3);
    await expect(root.getByRole('link', { name: locale.cta })).toHaveAttribute('href', locale.prefix + '/guides');
    const nav = page.locator('nav.myst-top-nav-bar');
    for (let index = 0; index < slugs.length; index++) {
      const href = locale.prefix + '/' + slugs[index];
      await expect(nav.getByRole('link', { name: locale.nav[index], exact: true })).toHaveAttribute('href', href);
      const linkedPage = await page.request.get(href + '/');
      expect(linkedPage.ok(), locale.code + ' route ' + href).toBeTruthy();
    }
    if (locale.code === 'en') {
      const width = await root.evaluate(el => el.getBoundingClientRect().width);
      expect(width).toBeGreaterThan(900);
      const primary = root.locator('.sc-handbook__intro > p:last-of-type > span:first-child a');
      const secondary = root.locator('.sc-handbook__intro > p:last-of-type > span:not(:first-child) a');
      expect(await primary.evaluate(el => getComputedStyle(el).backgroundColor))
        .not.toBe(await secondary.evaluate(el => getComputedStyle(el).backgroundColor));
      const icon = await root.locator('.sc-handbook__route--guide')
        .evaluate(el => getComputedStyle(el, '::after').maskImage);
      expect(icon).toContain('file-lines.svg');
    }
    expect(errors).toEqual([]);
    await page.screenshot({ path: testInfo.outputPath('handbook-' + locale.code + '-desktop.png'), fullPage: true });
  });

  test(locale.code + ' mobile homepage at 390px and 320px', async ({ page }, testInfo) => {
    for (const width of [390, 320]) {
      await page.setViewportSize({ width, height: 844 });
      const response = await page.goto(locale.prefix + '/');
      expect(response?.ok()).toBeTruthy();
      const logo = page.locator('.myst-top-nav-bar .myst-home-link img:visible').first();
      await expect(logo).toBeVisible();
      expect(await logo.evaluate(el => (el as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
      await expect(page.locator('.sc-handbook__route')).toHaveCount(3);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 2)).toBeTruthy();
      await expect(page.locator('.sc-handbook').getByRole('link', { name: locale.cta })).toBeVisible();
      await page.screenshot({
        path: testInfo.outputPath('handbook-' + locale.code + '-mobile-' + width + '.png'),
        fullPage: true
      });
    }
  });

  test(locale.code + ' navbar remains in selected language during navigation', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(locale.prefix + '/');
    for (let i = 0; i < slugs.length; i++) {
      await page.locator('nav.myst-top-nav-bar')
        .getByRole('link', { name: locale.nav[i], exact: true }).click();
      await expect(page).toHaveURL(new RegExp('^http://127\\.0\\.0\\.1:4174' + locale.prefix + '/' + slugs[i] + '/?$'));
      await expect(page.locator('main h1, main h2').first()).toBeVisible();
      await page.goto(locale.prefix + '/');
    }
  });
}

test('introduction and architecture remain reachable in all five locales', async ({ page }) => {
  for (const locale of locales) {
    for (const slug of ['introduction', 'architecture']) {
      const response = await page.request.get(locale.prefix + '/' + slug + '/');
      expect(response.ok(), locale.code + ' ' + slug).toBeTruthy();
    }
  }
});

test('localized UI Library entry identifies the English-only catalog', async ({ page }) => {
  for (const locale of locales.slice(1)) {
    await page.goto(locale.prefix + '/ui-library/');
    await expect(page.locator('main a[href="https://my.softcloud.dev/components"]').first()).toBeVisible();
    expect((await page.locator('main').innerText()).toLowerCase()).toContain('web awesome');
  }
});
