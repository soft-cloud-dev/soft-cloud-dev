import { test, expect, type Page } from '@playwright/test';

const locales = [
  { code: 'en', prefix: '', headline: 'Engineering knowledge you can reproduce.', nav: ['Guides', 'Notebooks', 'UI Library', 'Projects'], cta: 'Start with a guide' },
  { code: 'pl', prefix: '/pl', headline: 'Wiedza inżynierska, którą można odtworzyć.', nav: ['Poradniki', 'Notatniki', 'Biblioteka UI', 'Projekty'], cta: 'Rozpocznij od poradnika' },
  { code: 'de', prefix: '/de', headline: 'Ingenieurwissen, das sich reproduzieren lässt.', nav: ['Anleitungen', 'Notebooks', 'UI-Bibliothek', 'Projekte'], cta: 'Mit einer Anleitung beginnen' },
  { code: 'es', prefix: '/es', headline: 'Conocimiento de ingeniería reproducible.', nav: ['Guías', 'Cuadernos', 'Biblioteca UI', 'Proyectos'], cta: 'Empezar con una guía' },
  { code: 'fr', prefix: '/fr', headline: 'Un savoir d’ingénierie reproductible.', nav: ['Guides', 'Notebooks', 'Bibliothèque UI', 'Projets'], cta: 'Commencer par un guide' },
] as const;

const slugs = ['guides', 'notebooks', 'ui-library', 'projects'] as const;

async function expectVerificationContentFits(page: Page) {
  const card = page.locator('.sc-handbook__verification');
  await expect(card).toBeVisible();
  const codeWhitespace = await card.locator('pre code').evaluate(el => getComputedStyle(el).whiteSpace);
  expect(codeWhitespace, 'MyST inline code style must not prevent wrapping').toBe('pre-wrap');
  for (const selector of ['pre', 'p > code']) {
    const element = card.locator(selector).first();
    await expect(element).toBeVisible();
    const overflow = await element.evaluate(node => node.scrollWidth - node.clientWidth);
    expect(overflow, selector + ' must not require horizontal scrolling').toBeLessThanOrEqual(1);
  }
}

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
    const heroHeading = root.locator('.sc-handbook__intro h2').first();
    await expect(heroHeading).toBeVisible();
    const normalizedHeading = (await heroHeading.innerText())
      .replace(/[\u2018\u2019]/g, "'")
      .replace(/\s*¶\s*$/, '')
      .replace(/\s+/g, ' ').trim();
    expect(normalizedHeading).toBe(locale.headline.replace(/[\u2018\u2019]/g, "'"));
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
      await expect.poll(async () => {
        return page.locator('nav.myst-top-nav-bar img[alt="SoftCloud"]').evaluateAll(images =>
          images.some(element => {
            const img = element as HTMLImageElement;
            const rect = img.getBoundingClientRect();
            return img.complete && img.naturalWidth > 0 &&
              rect.width > 0 && rect.height > 0 &&
              rect.right > 0 && rect.left < window.innerWidth &&
              getComputedStyle(img).visibility === 'visible';
          })
        );
      }, { message: 'A loaded SoftCloud logo must be visible in the mobile navbar' }).toBe(true);
      await expect(page.locator('.sc-handbook__route')).toHaveCount(3);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 2)).toBeTruthy();
      await expect(page.locator('.sc-handbook').getByRole('link', { name: locale.cta })).toBeVisible();
      await expectVerificationContentFits(page);
      await page.screenshot({
        path: testInfo.outputPath('handbook-' + locale.code + '-mobile-' + width + '.png'),
        fullPage: true
      });
    }
  });

  test(locale.code + ' tablet verification and projects fit without clipping', async ({ page }, testInfo) => {
    for (const width of [768, 820, 834, 1024]) {
      await page.setViewportSize({ width, height: 1024 });
      const response = await page.goto(locale.prefix + '/');
      expect(response?.ok()).toBeTruthy();

      await expectVerificationContentFits(page);
      const projects = page.locator('.sc-handbook__projects');
      const geometry = await projects.evaluate(element => {
        const heading = element.querySelector(':scope > h3, :scope > h4');
        const paragraphs = Array.from(element.querySelectorAll(':scope > p'));
        return {
          headingBottom: heading?.getBoundingClientRect().bottom ?? 0,
          itemTops: paragraphs.map(p => p.getBoundingClientRect().top),
          overflow: element.scrollWidth - element.clientWidth,
        };
      });
      expect(geometry.itemTops).toHaveLength(2);
      expect(geometry.overflow, 'project grid must not overflow').toBeLessThanOrEqual(1);
      for (const top of geometry.itemTops) {
        expect(top, 'project links must appear below their heading')
          .toBeGreaterThanOrEqual(geometry.headingBottom - 1);
      }
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 2))
        .toBeTruthy();
      await page.screenshot({
        path: testInfo.outputPath('handbook-' + locale.code + '-tablet-' + width + '.png'),
        fullPage: true,
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
    await expect(page.locator('main')).toContainText(/web[- ]awesome/i);
  }
});

test('localized homepages hydrate without crashing when browser storage throws SecurityError', async ({ page }) => {
  await page.addInitScript(() => {
    const blocked = {
      get() {
        throw new DOMException('The operation is insecure.', 'SecurityError');
      },
    };
    Object.defineProperty(window, 'localStorage', blocked);
    Object.defineProperty(window, 'sessionStorage', blocked);
  });

  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];
  page.on('pageerror', error => pageErrors.push(error.message));
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });

  await page.setViewportSize({ width: 390, height: 844 });
  for (const locale of locales.slice(0, 2)) {
    await page.goto(locale.prefix + '/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(300);
    await expect(page.locator('body')).not.toContainText('Unexpected Error Occurred');
    await expect(page.locator('.sc-handbook')).toBeVisible();
  }

  await page.reload({ waitUntil: 'networkidle' });
  await expect(page.locator('body')).not.toContainText('Unexpected Error Occurred');
  await page.locator('button.myst-theme-button').click();
  await expect(page.locator('body')).not.toContainText('Unexpected Error Occurred');

  await page.locator('[data-sc-lang-switcher] button').first().click();
  await page.locator('[data-sc-lang-switcher] a, [data-sc-lang-switcher] button, [data-sc-lang-switcher] [role="menuitem"]')
    .filter({ hasText: 'English' })
    .first()
    .click();
  await page.waitForLoadState('networkidle');
  await expect(page).toHaveURL(/^http:\/\/127\.0\.0\.1:4174\/$/);
  await expect(page.locator('.sc-handbook')).toBeVisible();
  await expect(page.locator('body')).not.toContainText('Unexpected Error Occurred');
  expect(pageErrors).toEqual([]);
  expect(consoleErrors).toEqual([]);
});
