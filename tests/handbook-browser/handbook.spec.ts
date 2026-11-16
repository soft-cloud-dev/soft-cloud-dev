import { test, expect, type Page } from '@playwright/test';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

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

  test(locale.code + ' navbar remains in selected language during navigation', async ({ page, baseURL }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(locale.prefix + '/');
    const origin = (baseURL ?? 'http://127.0.0.1:4174').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    for (let i = 0; i < slugs.length; i++) {
      await page.locator('nav.myst-top-nav-bar')
        .getByRole('link', { name: locale.nav[i], exact: true }).click();
      await expect(page).toHaveURL(new RegExp('^' + origin + locale.prefix + '/' + slugs[i] + '/?$'));
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

test('localized UI Library entry identifies the English-only catalog', async ({ page, baseURL, context }) => {
  const errors: string[] = [];
  const failedResources: string[] = [];
  const collectErrors = (target: Page) => {
    target.on('pageerror', error => errors.push(error.message));
    target.on('response', response => {
      if (response.status() >= 400) failedResources.push(`${response.status()} ${response.url()}`);
    });
  };
  collectErrors(page);
  context.on('page', collectErrors);
  await context.route('https://my.softcloud.dev/components', async route => {
    const response = await route.fetch({ url: `${baseURL}/components/` });
    await route.fulfill({ response });
  });
  const catalogResponse = await page.goto('/components/');
  expect(catalogResponse?.ok(), '/components/ route must return HTTP 200').toBeTruthy();
  await expect(page.locator('main h1').first()).toContainText('Web Awesome — Component Catalog');
  await expect(page.locator('a[title="Edit This Page"]')).toHaveAttribute(
    'href',
    'https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/components/index.md',
  );

  for (const locale of locales) {
    const response = await page.goto(locale.prefix + '/ui-library/');
    expect(response?.ok(), locale.code + ' /ui-library/').toBeTruthy();
    const cta = page.locator('main a[href="https://my.softcloud.dev/components"]').first();
    await expect(cta).toBeVisible();
    await expect(page.locator('main')).toContainText(/web[- ]awesome/i);
    const expectedEditHref =
      locale.code === 'en'
        ? 'https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/ui-library.md'
        : `https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/i18n/${locale.code}/ui-library.md`;
    await expect(page.locator('a[title="Edit This Page"]')).toHaveAttribute('href', expectedEditHref);
    const [catalog] = await Promise.all([page.waitForEvent('popup'), cta.click()]);
    await catalog.waitForLoadState('networkidle');
    await expect(catalog).toHaveURL('https://my.softcloud.dev/components');
    await expect(catalog.locator('main h1').first()).toContainText('Web Awesome — Component Catalog');
    await expect(catalog.locator('html')).toHaveAttribute('lang', 'en');
    await expect(catalog.locator('a[title="Edit This Page"]')).toHaveAttribute(
      'href', 'https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/components/index.md',
    );
    await expect(catalog.locator('body')).not.toContainText('Unexpected Error Occurred');
    await catalog.close();
  }
  expect(errors).toEqual([]);
  expect(failedResources.filter(url => url.includes('127.0.0.1:4174'))).toEqual([]);
});

test('all published page payloads point to existing authoritative repository sources', async ({ request }) => {
  const response = await request.get('/i18n/route-manifest.json');
  expect(response.ok()).toBeTruthy();
  const manifest = await response.json();
  let checked = 0;
  for (const page of Object.values(manifest.pages) as any[]) {
    for (const locale of locales) {
      const translation = page.translations[locale.code];
      if (!translation?.available) continue;
      const route = translation.route.replace(/\/$/, '');
      const payloadResponse = await request.get((route || '') + (page.slug ? '.json' : '/index.json'));
      expect(payloadResponse.ok(), `${locale.code} ${translation.route}`).toBeTruthy();
      const payload = await payloadResponse.json();
      const source = (locale.code === 'en' ? '' : `i18n/${locale.code}/`) + payload.location.replace(/^\//, '');
      expect(existsSync(resolve(source)), `repository source ${source}`).toBeTruthy();
      expect(payload.frontmatter.edit_url).toBe(`https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/${source}`);
      expect(payload.frontmatter.source_url).toBe(`https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/${source}`);
      checked++;
    }
  }
  expect(checked).toBeGreaterThan(150);
});

test('localized homepages hydrate without crashing when browser storage throws SecurityError', async ({ page, baseURL }) => {
  const origin = (baseURL ?? 'http://127.0.0.1:4174').replace(/\/+$/, '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
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
  await expect(page).toHaveURL(new RegExp('^' + origin + '/$'));
  await expect(page.locator('.sc-handbook')).toBeVisible();
  await expect(page.locator('body')).not.toContainText('Unexpected Error Occurred');
  expect(pageErrors).toEqual([]);
  expect(consoleErrors).toEqual([]);
});

test('handbook badges, links, and eyebrow meet WCAG AA contrast in light and dark mode', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/');
  await page.waitForLoadState('networkidle');

  const measureContrast = async () => page.evaluate(() => {
    const parseRgb = (cssColor: string): [number, number, number] => {
      const m = cssColor.match(/\d+(\.\d+)?/g);
      if (!m || m.length < 3) return [0, 0, 0];
      return [Number(m[0]), Number(m[1]), Number(m[2])];
    };
    const relLum = (rgb: [number, number, number]) => {
      const lin = rgb.map(v => {
        const s = v / 255;
        return s <= 0.04045 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
    };
    const ratio = (fg: string, bg: string) => {
      let l1 = relLum(parseRgb(fg));
      let l2 = relLum(parseRgb(bg));
      if (l1 < l2) [l1, l2] = [l2, l1];
      return (l1 + 0.05) / (l2 + 0.05);
    };
    const effectiveBg = (el: Element | null): string => {
      let cur: Element | null = el;
      while (cur) {
        const bg = getComputedStyle(cur).backgroundColor;
        const m = bg.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
        if (m && (m[4] === undefined || parseFloat(m[4]) > 0.1)) return bg;
        cur = cur.parentElement;
      }
      return 'rgb(255, 255, 255)';
    };

    const items: Array<{ label: string; fg: string; bg: string; ratio: number }> = [];
    const targets: Array<[string, Element | null]> = [
      ['eyebrow', document.querySelector('.sc-handbook__intro > p:first-of-type')],
      ['primary-cta', document.querySelector('.sc-handbook__intro > p:last-of-type > span:first-child a')],
      ['secondary-cta', document.querySelector('.sc-handbook__intro > p:last-of-type > span:not(:first-child) a')],
      ['verification-link', document.querySelector('.sc-handbook__verification > p:last-child a')],
    ];
    for (const [label, el] of targets) {
      if (!el) continue;
      const fg = getComputedStyle(el).color;
      const bg = effectiveBg(el);
      items.push({ label, fg, bg, ratio: ratio(fg, bg) });
    }
    for (const p of document.querySelectorAll('.sc-handbook__route > p:last-of-type')) {
      const strong = p.querySelector('strong') ?? p;
      const fg = getComputedStyle(strong).color;
      const bg = effectiveBg(p);
      items.push({ label: 'badge:' + (p.textContent ?? '').trim(), fg, bg, ratio: ratio(fg, bg) });
    }
    return items;
  });

  const lightItems = await measureContrast();
  expect(lightItems.length).toBe(7);
  for (const item of lightItems) {
    expect(item.ratio, 'Light mode contrast for ' + item.label).toBeGreaterThanOrEqual(4.5);
  }

  await page.locator('.myst-theme-button').click();
  await expect(page.locator('html')).toHaveClass(/\bdark\b/);

  const darkItems = await measureContrast();
  expect(darkItems.length).toBe(7);
  for (const item of darkItems) {
    expect(item.ratio, 'Dark mode contrast for ' + item.label).toBeGreaterThanOrEqual(4.5);
  }
  await page.screenshot({ path: testInfo.outputPath('handbook-en-dark-desktop.png'), fullPage: true });
});

test('non-handbook mobile navbar keeps visible clickable SoftCloud logo on /linux/', async ({ page }) => {
  for (const width of [390, 320]) {
    await page.setViewportSize({ width, height: 844 });
    const response = await page.goto('/linux/', { waitUntil: 'networkidle' });
    expect(response?.ok()).toBeTruthy();

    const linkBox = await page.locator('nav.myst-top-nav-bar .myst-home-link').boundingBox();
    expect(linkBox).not.toBeNull();
    expect(linkBox!.width, `Home link width at ${width}px`).toBeGreaterThanOrEqual(50);
    expect(linkBox!.height, `Home link height at ${width}px`).toBeGreaterThanOrEqual(16);

    const visibleLogo = await page.locator('nav.myst-top-nav-bar img[alt="SoftCloud"]').evaluateAll(images =>
      images.some(element => {
        const img = element as HTMLImageElement;
        const rect = img.getBoundingClientRect();
        return img.complete && img.naturalWidth > 0 &&
          rect.width >= 50 && rect.height >= 16 &&
          rect.right > 0 && rect.left < window.innerWidth &&
          getComputedStyle(img).visibility === 'visible';
      })
    );
    expect(visibleLogo, `Visible SoftCloud logo on /linux/ at ${width}px`).toBe(true);
  }
});

test('pricing comparison code snippet tabs render both tabs without fence truncation', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  const response = await page.goto('/pricing-comparison/#sec-pricing-code-snippets', { waitUntil: 'networkidle' });
  expect(response?.ok()).toBeTruthy();

  const tabSet = page.locator('#sec-pricing-code-snippets + .myst-tab-set');
  const headers = tabSet.locator('.myst-tab-item-header');
  await expect(headers).toHaveCount(2);
  await expect(headers.nth(0)).toHaveText('MyST + Lit SSR Authoring');
  await expect(headers.nth(1)).toHaveText('Standalone Web Awesome HTML');

  const articleText = await page.locator('article').innerText();
  expect(articleText).not.toContain('::::{tab-item}');

  const firstTabCode = await tabSet.locator('pre code:visible').first().innerText();
  expect(firstTabCode).toContain(':::::{grid}');
  expect(firstTabCode.trim()).toMatch(/:::::$/);

  await headers.nth(1).click();
  const secondTabCode = await tabSet.locator('pre code:visible').first().innerText();
  expect(secondTabCode).toContain('<wa-radio-group');
  expect(secondTabCode).toContain('Export Sizing Manifest');
});

test('webawesome-docs Interface Parity table has clean copyable code and language switcher preserves fragment', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  for (const route of ['/webawesome-docs/', '/pl/webawesome-docs/']) {
    const response = await page.goto(route, { waitUntil: 'networkidle' });
    expect(response?.ok()).toBeTruthy();

    const paritySection = page.locator('#interface-parity-python-api-vs-myst-directives');
    await expect(paritySection).toBeVisible();
    const tableText = await page.locator('#interface-parity-python-api-vs-myst-directives ~ figure table').first().innerText();
    expect(tableText).not.toContain('&nbsp;');
    expect(tableText).not.toContain('<br/>');
    expect(tableText).not.toContain('````');
    expect(tableText).toContain('UI.callout_text(');
    expect(tableText).toContain('{wa-callout} Title');
  }

  await page.goto('/webawesome-docs/', { waitUntil: 'networkidle' });
  await page.locator('nav a', { hasText: /Interface Parity/i }).first().click();
  await expect(page).toHaveURL(/#interface-parity-python-api-vs-myst-directives$/);

  await page.locator('.sc-lang-trigger').click();
  const plOption = page.locator('.sc-lang-option[data-locale-code="pl"]');
  await expect(plOption).toHaveAttribute('href', '/pl/webawesome-docs#interface-parity-python-api-vs-myst-directives');

  await Promise.all([
    page.waitForURL(/\/pl\/webawesome-docs\/?#interface-parity-python-api-vs-myst-directives$/),
    plOption.click(),
  ]);
  await expect(page).toHaveURL(/\/pl\/webawesome-docs\/?#interface-parity-python-api-vs-myst-directives$/);
});

test('mobile and tablet homepage navigation drawer supports close button, backdrop dismiss, Escape, focus return, and scroll containment', async ({ page }) => {
  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];
  page.on('pageerror', error => pageErrors.push(error.message));
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });

  const viewports = [
    { name: 'mobile', width: 390, height: 844 },
    { name: 'tablet-portrait', width: 768, height: 1024 },
    { name: 'tablet-landscape-compact', width: 980, height: 768 },
  ];

  for (const vp of viewports) {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    const response = await page.goto('/', { waitUntil: 'networkidle' });
    expect(response?.ok()).toBeTruthy();

    const menuButton = page.locator('button.myst-top-nav-menu-button');
    const drawer = page.locator('#myst-primary-sidebar');
    const closeButton = drawer.locator('.myst-drawer-close-button');
    const backdrop = page.locator('.myst-navigation-overlay');

    await expect(menuButton).toBeVisible();
    await expect(menuButton).toHaveAttribute('aria-expanded', 'false');
    await expect(menuButton).toHaveAttribute('aria-controls', 'myst-primary-sidebar');
    await expect(drawer).toBeHidden();

    // 1. Open drawer and verify modal semantics, close button, inertness, bounds, and scroll containment
    await menuButton.click();
    await expect(drawer).toBeVisible();
    await expect(drawer).toHaveAttribute('role', 'dialog');
    await expect(drawer).toHaveAttribute('aria-modal', 'true');
    await expect(drawer).toHaveAttribute('aria-label', 'Navigation menu');
    await expect(menuButton).toHaveAttribute('aria-expanded', 'true');
    await expect(backdrop).toBeVisible();
    await expect(closeButton).toBeVisible();

    const drawerBox = await drawer.boundingBox();
    expect(drawerBox).not.toBeNull();
    expect(drawerBox!.x).toBeGreaterThanOrEqual(0);
    expect(drawerBox!.y).toBeGreaterThanOrEqual(0);
    expect(drawerBox!.x + drawerBox!.width).toBeLessThanOrEqual(vp.width);
    expect(drawerBox!.y + drawerBox!.height).toBeLessThanOrEqual(vp.height + 1);

    const closeBox = await closeButton.boundingBox();
    expect(closeBox).not.toBeNull();
    expect(closeBox!.width).toBeGreaterThanOrEqual(40);
    expect(closeBox!.height).toBeGreaterThanOrEqual(40);
    const closeCenterHit = await page.evaluate(({ x, y }) => {
      const hit = document.elementFromPoint(x, y);
      return Boolean(hit && hit.closest('.myst-drawer-close-button'));
    }, { x: closeBox!.x + closeBox!.width / 2, y: closeBox!.y + closeBox!.height / 2 });
    expect(closeCenterHit, `Close button must not be obscured at ${vp.name}`).toBe(true);

    await expect.poll(async () => page.evaluate(() =>
      document.activeElement?.classList.contains('myst-drawer-close-button') ?? false
    )).toBe(true);

    const modalInvariants = await page.evaluate(() => {
      const main = document.querySelector('main');
      const topNav = document.querySelector('.myst-top-nav');
      const htmlStyle = getComputedStyle(document.documentElement);
      const bodyStyle = getComputedStyle(document.body);
      return {
        mainInert: Boolean(main?.inert),
        topNavInert: Boolean(topNav?.inert),
        htmlOverflow: htmlStyle.overflow,
        bodyOverflow: bodyStyle.overflow,
        bodyPosition: bodyStyle.position,
      };
    });
    expect(modalInvariants.mainInert).toBe(true);
    expect(modalInvariants.topNavInert).toBe(true);
    expect(modalInvariants.htmlOverflow).not.toBe('hidden');
    expect(modalInvariants.bodyOverflow).not.toBe('hidden');
    expect(modalInvariants.bodyPosition).not.toBe('fixed');

    // Background page must not scroll while modal drawer is open
    await page.mouse.move(vp.width - 30, Math.floor(vp.height / 2));
    await page.mouse.wheel(0, 400);
    await page.waitForTimeout(150);
    expect(await page.evaluate(() => window.scrollY)).toBe(0);

    // 2. Clicking outside the drawer closes it without reload and returns focus to hamburger
    const initialUrl = page.url();
    await page.mouse.click(vp.width - 30, Math.floor(vp.height / 2));
    await expect(drawer).toBeHidden();
    await expect(backdrop).toHaveCount(0);
    await expect(menuButton).toHaveAttribute('aria-expanded', 'false');
    expect(page.url()).toBe(initialUrl);
    expect(await page.evaluate(() => ({
      mainInert: Boolean(document.querySelector('main')?.inert),
      topNavInert: Boolean(document.querySelector('.myst-top-nav')?.inert),
      focusedHamburger: document.activeElement?.classList.contains('myst-top-nav-menu-button') ?? false,
    }))).toEqual({ mainInert: false, topNavInert: false, focusedHamburger: true });

    // 3. Reopen and dismiss via visible close button -> returns focus to hamburger
    await menuButton.click();
    await expect(drawer).toBeVisible();
    await closeButton.click();
    await expect(drawer).toBeHidden();
    await expect.poll(async () => page.evaluate(() =>
      document.activeElement?.classList.contains('myst-top-nav-menu-button') ?? false
    )).toBe(true);

    // 4. Reopen and dismiss via Escape -> returns focus to hamburger
    await menuButton.click();
    await expect(drawer).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(drawer).toBeHidden();
    await expect.poll(async () => page.evaluate(() =>
      document.activeElement?.classList.contains('myst-top-nav-menu-button') ?? false
    )).toBe(true);

    // 5. Reopen and click a navigation link inside the drawer -> closes drawer & navigates cleanly
    await menuButton.click();
    await expect(drawer).toBeVisible();
    await drawer.locator('.myst-primary-sidebar-topnav').getByRole('link', { name: 'Guides', exact: true }).click();
    await expect(page).toHaveURL(/\/guides\/?$/);
    await expect(drawer).toBeHidden();
    expect(await page.evaluate(() => Boolean(document.querySelector('main')?.inert))).toBe(false);
  }

  expect(pageErrors).toEqual([]);
  expect(consoleErrors.filter(e => !e.includes('favicon'))).toEqual([]);
});

test('tablet landscape subpages (1024x768, 1180x820), breakpoint resize, and localized /pl/ drawer work cleanly', async ({ page }) => {
  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];
  page.on('pageerror', error => pageErrors.push(error.message));
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });

  // 1. iPad landscape subpage (/guides/) where hamburger is visible up to 1279px
  for (const vp of [{ width: 1024, height: 768 }, { width: 1180, height: 820 }]) {
    await page.setViewportSize(vp);
    await page.goto('/guides/', { waitUntil: 'networkidle' });
    const menuButton = page.locator('button.myst-top-nav-menu-button');
    const drawer = page.locator('#myst-primary-sidebar');
    const closeButton = drawer.locator('.myst-drawer-close-button');
    await expect(menuButton).toBeVisible();
    await menuButton.click();
    await expect(drawer).toBeVisible();
    await expect(closeButton).toBeVisible();

    // Outside click restores page and returns focus
    await page.mouse.click(vp.width - 40, Math.floor(vp.height / 2));
    await expect(drawer).toBeHidden();
    await expect.poll(async () => page.evaluate(() =>
      document.activeElement?.classList.contains('myst-top-nav-menu-button') ?? false
    )).toBe(true);
  }

  // 2. Breakpoint resize from tablet drawer -> desktop closes drawer and clears inert
  await page.setViewportSize({ width: 980, height: 768 });
  await page.goto('/', { waitUntil: 'networkidle' });
  await page.locator('button.myst-top-nav-menu-button').click();
  await expect(page.locator('#myst-primary-sidebar')).toBeVisible();
  await page.setViewportSize({ width: 1024, height: 768 });
  await expect(page.locator('#myst-primary-sidebar')).toBeHidden();
  expect(await page.evaluate(() => Boolean(document.querySelector('main')?.inert))).toBe(false);

  // 3. Localized Polish homepage drawer labels and route navigation
  await page.setViewportSize({ width: 980, height: 768 });
  await page.goto('/pl/', { waitUntil: 'networkidle' });
  await page.locator('button.myst-top-nav-menu-button').click();
  const plDrawer = page.locator('#myst-primary-sidebar');
  await expect(plDrawer).toBeVisible();
  await expect(plDrawer).toHaveAttribute('aria-label', 'Menu nawigacji');
  await expect(plDrawer.locator('.myst-drawer-close-button')).toHaveAttribute('aria-label', 'Zamknij menu');
  await plDrawer.locator('.myst-primary-sidebar-topnav').getByRole('link', { name: 'Poradniki', exact: true }).click();
  await expect(page).toHaveURL(/\/pl\/guides\/?$/);
  await expect(plDrawer).toBeHidden();

  expect(pageErrors).toEqual([]);
  expect(consoleErrors.filter(e => !e.includes('favicon'))).toEqual([]);
});
