import { test, expect, type Page } from '@playwright/test';

async function expectNoErrors(page: Page, fn: () => Promise<void>) {
  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];
  page.on('pageerror', err => pageErrors.push(err.message));
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  await fn();
  expect(pageErrors, 'Uncaught page errors').toEqual([]);
  expect(consoleErrors, 'Console errors (including React hydration mismatches)').toEqual([]);
}

async function readBreadcrumbItems(page: Page) {
  return page.locator('nav.sc-breadcrumbs').evaluate(nav => {
    const ol = nav.querySelector(':scope > ol.sc-breadcrumbs__list');
    const items = Array.from(ol?.querySelectorAll(':scope > li.sc-breadcrumbs__item') ?? []);
    return {
      ariaLabel: nav.getAttribute('aria-label'),
      hasOl: Boolean(ol),
      hasUl: Boolean(nav.querySelector('ul')),
      items: items.map(li => {
        const a = li.querySelector(':scope > a');
        const span = li.querySelector(':scope > span');
        return {
          tag: a ? 'a' : span ? 'span' : 'other',
          text: (a || span || li).textContent?.trim() ?? '',
          href: a?.getAttribute('href') ?? null,
          ariaCurrent: a?.getAttribute('aria-current') ?? null,
          liText: li.textContent?.trim() ?? '',
        };
      }),
    };
  });
}

test.describe('Breadcrumb navigation', () => {
  test('omitted on all five locale homepages', async ({ page }) => {
    for (const prefix of ['', '/pl', '/de', '/es', '/fr']) {
      await expectNoErrors(page, async () => {
        const res = await page.goto(prefix + '/', { waitUntil: 'networkidle' });
        expect(res?.ok()).toBeTruthy();
        await expect(page.locator('#softcloud-breadcrumbs-root')).toHaveCount(0);
        await expect(page.locator('nav.sc-breadcrumbs')).toHaveCount(0);
      });
    }
  });

  test('renders full TOC hierarchy on English subpages without raw text dividers', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });

    // 1. /guides/
    await expectNoErrors(page, async () => {
      await page.goto('/guides/', { waitUntil: 'networkidle' });
      const trail = await readBreadcrumbItems(page);
      expect(trail.ariaLabel).toBe('Breadcrumbs');
      expect(trail.hasOl).toBe(true);
      expect(trail.hasUl).toBe(false);
      expect(trail.items).toEqual([
        { tag: 'a', text: 'SoftCloud Hub', href: '/', ariaCurrent: null, liText: 'SoftCloud Hub' },
        { tag: 'span', text: 'Platform Engineering', href: null, ariaCurrent: null, liText: 'Platform Engineering' },
        { tag: 'a', text: 'Guides', href: '/guides', ariaCurrent: 'page', liText: 'Guides' },
      ]);
    });

    // 2. /linux/ (folder links to /projects)
    await expectNoErrors(page, async () => {
      await page.goto('/linux/', { waitUntil: 'networkidle' });
      const trail = await readBreadcrumbItems(page);
      expect(trail.items).toEqual([
        { tag: 'a', text: 'SoftCloud Hub', href: '/', ariaCurrent: null, liText: 'SoftCloud Hub' },
        { tag: 'a', text: 'Systems & Laboratories', href: '/projects', ariaCurrent: null, liText: 'Systems & Laboratories' },
        { tag: 'a', text: 'Node Linux', href: '/linux', ariaCurrent: 'page', liText: 'Node Linux' },
      ]);
    });

    // 3. /projects/ (collapses folder landing page cleanly)
    await expectNoErrors(page, async () => {
      await page.goto('/projects/', { waitUntil: 'networkidle' });
      const trail = await readBreadcrumbItems(page);
      expect(trail.items).toEqual([
        { tag: 'a', text: 'SoftCloud Hub', href: '/', ariaCurrent: null, liText: 'SoftCloud Hub' },
        { tag: 'a', text: 'Projects', href: '/projects', ariaCurrent: 'page', liText: 'Projects' },
      ]);
    });

    // 4. /breadcrumb/ (deep component page: links Web Awesome Components -> /components, Navigation is label)
    await expectNoErrors(page, async () => {
      await page.goto('/breadcrumb/', { waitUntil: 'networkidle' });
      const trail = await readBreadcrumbItems(page);
      expect(trail.items).toEqual([
        { tag: 'a', text: 'SoftCloud Hub', href: '/', ariaCurrent: null, liText: 'SoftCloud Hub' },
        { tag: 'span', text: 'Platform Engineering', href: null, ariaCurrent: null, liText: 'Platform Engineering' },
        { tag: 'a', text: 'Web Awesome Components', href: '/components', ariaCurrent: null, liText: 'Web Awesome Components' },
        { tag: 'span', text: 'Navigation', href: null, ariaCurrent: null, liText: 'Navigation' },
        { tag: 'a', text: 'Breadcrumb <wa-breadcrumb>', href: '/breadcrumb', ariaCurrent: 'page', liText: 'Breadcrumb <wa-breadcrumb>' },
      ]);
    });

    // 5. Ancestor link navigates to /components
    await page.locator('nav.sc-breadcrumbs a', { hasText: 'Web Awesome Components' }).click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/components\/?$/);
    const compTrail = await readBreadcrumbItems(page);
    expect(compTrail.items.at(-1)).toEqual({
      tag: 'a',
      text: 'Web Awesome — Component Catalog',
      href: '/components',
      ariaCurrent: 'page',
      liText: 'Web Awesome — Component Catalog',
    });
  });

  test('renders localized breadcrumbs in pl, de, es, and fr', async ({ page }) => {
    const cases = [
      {
        url: '/pl/linux/',
        label: 'Nawigacja okruszkowa',
        items: [
          { text: 'SoftCloud Hub', href: '/pl/' },
          { text: 'Systemy i laboratoria', href: '/pl/projects' },
          { text: 'Węzeł Linux', href: '/pl/linux' },
        ],
      },
      {
        url: '/de/architecture/',
        label: 'Brotkrümelnavigation',
        items: [
          { text: 'SoftCloud Hub', href: '/de/' },
          { text: 'Plattformentwicklung', href: null },
          { text: 'Architektur und Spezifikation', href: '/de/architecture' },
        ],
      },
      {
        url: '/es/contributing/',
        label: 'Migas de pan',
        items: [
          { text: 'SoftCloud Hub', href: '/es/' },
          { text: 'Ingeniería de plataforma', href: null },
          { text: 'Guía de contribución', href: '/es/contributing' },
        ],
      },
      {
        url: '/fr/ui-library/',
        label: "Fil d'Ariane",
        items: [
          { text: 'SoftCloud Hub', href: '/fr/' },
          { text: 'Ingénierie de plateforme', href: null },
          { text: 'Bibliothèque UI', href: '/fr/ui-library' },
        ],
      },
    ];

    for (const c of cases) {
      await expectNoErrors(page, async () => {
        await page.goto(c.url, { waitUntil: 'networkidle' });
        const trail = await readBreadcrumbItems(page);
        expect(trail.ariaLabel).toBe(c.label);
        expect(trail.items.map(i => ({ text: i.text, href: i.href }))).toEqual(c.items);
        expect(trail.items.at(-1)?.ariaCurrent).toBe('page');
      });
    }
  });

  test('works without JavaScript enabled', async ({ browser }) => {
    const context = await browser.newContext({ javaScriptEnabled: false });
    const page = await context.newPage();
    try {
      await page.goto('/', { waitUntil: 'domcontentloaded' });
      await expect(page.locator('#softcloud-breadcrumbs-root')).toHaveCount(0);

      await page.goto('/breadcrumb/', { waitUntil: 'domcontentloaded' });
      const nav = page.locator('nav.sc-breadcrumbs');
      await expect(nav).toBeVisible();
      const listStyle = await nav.locator('ol.sc-breadcrumbs__list').evaluate(el => getComputedStyle(el).listStyleType);
      expect(listStyle).toBe('none');

      const trail = await readBreadcrumbItems(page);
      expect(trail.items).toHaveLength(5);
      expect(trail.items.at(-1)?.ariaCurrent).toBe('page');

      await nav.locator('a', { hasText: 'Web Awesome Components' }).click();
      await page.waitForLoadState('domcontentloaded');
      await expect(page).toHaveURL(/\/components\/?$/);
    } finally {
      await context.close();
    }
  });

  test('synchronizes across MyST SPA navigation without hydration or console errors', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await expectNoErrors(page, async () => {
      await page.goto('/', { waitUntil: 'networkidle' });
      await expect(page.locator('#softcloud-breadcrumbs-root')).toHaveCount(0);

      // Navigate via top navbar (SPA transition from / -> /guides)
      await page.locator('nav.myst-top-nav-bar').getByRole('link', { name: 'Guides', exact: true }).click();
      await expect(page).toHaveURL(/\/guides\/?$/);
      await expect(page.locator('nav.sc-breadcrumbs')).toBeVisible();
      await expect(page.locator('nav.sc-breadcrumbs [aria-current="page"]')).toHaveText('Guides');

      // Navigate via sidebar TOC (SPA transition from /guides -> /architecture)
      await page.locator('nav.myst-primary-sidebar-toc a[href="/architecture"]').click();
      await expect(page).toHaveURL(/\/architecture\/?$/);
      await expect(page.locator('nav.sc-breadcrumbs [aria-current="page"]')).toHaveText('Architecture & Specification');

      // Navigate back to homepage -> breadcrumbs disappear
      await page.locator('nav.myst-top-nav-bar a.myst-home-link').first().click();
      await expect(page).toHaveURL(/\/$/);
      await expect(page.locator('#softcloud-breadcrumbs-root')).toHaveCount(0);
    });
  });

  test('responsive geometry, contrast in light/dark mode, and print hiding', async ({ page }) => {
    for (const width of [320, 390, 768, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto('/breadcrumb/', { waitUntil: 'networkidle' });
      const nav = page.locator('nav.sc-breadcrumbs');
      await expect(nav).toBeVisible();

      const layout = await page.evaluate(() => {
        const navEl = document.querySelector('nav.sc-breadcrumbs')!;
        const fmHeader = document.querySelector('.myst-fm-block-header')!;
        const navRect = navEl.getBoundingClientRect();
        const hdrRect = fmHeader.getBoundingClientRect();
        return {
          navBottom: navRect.bottom,
          hdrTop: hdrRect.top,
          docOverflow: document.documentElement.scrollWidth - window.innerWidth,
        };
      });
      expect(layout.navBottom, `Breadcrumbs must sit above frontmatter header at ${width}px`).toBeLessThanOrEqual(layout.hdrTop + 1);
      expect(layout.docOverflow, `No horizontal overflow at ${width}px`).toBeLessThanOrEqual(1);
    }

    // Contrast in light & dark mode
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto('/breadcrumb/', { waitUntil: 'networkidle' });

    const measure = () =>
      page.evaluate(() => {
        const parseRgb = (cssColor: string): [number, number, number] => {
          const m = cssColor.match(/\d+(\.\d+)?/g);
          if (!m || m.length < 3) return [0, 0, 0];
          return [Number(m[0]), Number(m[1]), Number(m[2])];
        };
        const lum = (rgb: [number, number, number]) => {
          const lin = rgb.map(v => {
            const s = v / 255;
            return s <= 0.04045 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
          });
          return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
        };
        const contrast = (fg: string, bg: string) => {
          let l1 = lum(parseRgb(fg));
          let l2 = lum(parseRgb(bg));
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
          return document.documentElement.classList.contains('dark') ? 'rgb(28, 25, 23)' : 'rgb(255, 255, 255)';
        };

        const els = [
          ['ancestor-link', document.querySelector('nav.sc-breadcrumbs a.sc-breadcrumbs__link:not([aria-current="page"])')],
          ['folder-label', document.querySelector('nav.sc-breadcrumbs span.sc-breadcrumbs__label')],
          ['current-link', document.querySelector('nav.sc-breadcrumbs a.sc-breadcrumbs__link[aria-current="page"]')],
        ] as const;

        return els.map(([name, el]) => {
          const fg = el ? getComputedStyle(el).color : 'rgb(0,0,0)';
          const bg = effectiveBg(el);
          return { name, ratio: contrast(fg, bg) };
        });
      });

    for (const item of await measure()) {
      expect(item.ratio, `Light mode contrast for ${item.name}`).toBeGreaterThanOrEqual(4.5);
    }

    await page.locator('.myst-theme-button').click();
    await expect(page.locator('html')).toHaveClass(/\bdark\b/);
    for (const item of await measure()) {
      expect(item.ratio, `Dark mode contrast for ${item.name}`).toBeGreaterThanOrEqual(4.5);
    }

    // Print mode hides breadcrumbs host
    await page.emulateMedia({ media: 'print' });
    await expect(page.locator('#softcloud-breadcrumbs-root')).toBeHidden();
  });
});
