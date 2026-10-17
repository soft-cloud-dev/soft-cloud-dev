import { test, expect } from '@playwright/test';

test.describe('SSR Lifecycle & Dynamic Transform Boundary (WA-007, WA-008)', () => {
  test('server-rendered components include valid DSD templates and did-ssr in initial response', async ({
    page,
  }) => {
    const response = await page.goto('/');
    const html = (await response?.text()) || '';

    // Verify presence of did-ssr on server-rendered custom elements
    expect(html).toContain('did-ssr');
    expect(html).toMatch(/<wa-card[^>]*\bdid-ssr\b/);
    expect(html).toMatch(/<wa-callout[^>]*\bdid-ssr\b/);
    expect(html).toMatch(/<wa-button[^>]*\bdid-ssr\b/);
    expect(html).toMatch(/<wa-icon[^>]*\bdid-ssr\b/);

    // Verify DSD open shadowrootmode
    expect(html).toMatch(/<template[^>]*\b(shadowrootmode|shadowroot)="open"/);
  });

  test('client dynamic placeholder transformation does not stamp did-ssr (WA-007)', async ({ page }) => {
    await page.goto('/');

    // Inject a dynamic .sc-wa-host into the page
    const transformedTag = await page.evaluate(() => {
      const container = document.createElement('div');
      container.id = 'dynamic-test-container';

      const host = document.createElement('div');
      host.className = 'sc-wa-host sc-wa-button';

      const meta = document.createElement('span');
      meta.className = 'sc-wa-meta';
      meta.textContent = JSON.stringify({
        schema_version: '2.0.0',
        component: 'wa-button',
        variant: 'brand',
        appearance: 'filled',
      });

      host.appendChild(meta);
      host.appendChild(document.createTextNode('Dynamic Button'));
      container.appendChild(host);
      document.body.appendChild(container);

      // Trigger client transform
      window.SoftCloudTheme.transformHosts(container);

      const dynamicBtn = container.querySelector('wa-button');
      return {
        exists: !!dynamicBtn,
        hasDidSsr: dynamicBtn?.hasAttribute('did-ssr') || false,
        variant: dynamicBtn?.getAttribute('variant'),
        appearance: dynamicBtn?.getAttribute('appearance'),
      };
    });

    expect(transformedTag.exists).toBe(true);
    // Crucial WA-007 check: client-created dynamic element must NEVER have did-ssr!
    expect(transformedTag.hasDidSsr).toBe(false);
    expect(transformedTag.variant).toBe('brand');
    expect(transformedTag.appearance).toBe('filled');
  });

  test('custom elements hydrate without React #418 or recoverable error suppression (WA-008)', async ({
    page,
  }) => {
    const errorLogs: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errorLogs.push(msg.text());
      }
    });

    await page.goto('/');

    // Wait for all custom elements to be defined
    await page.waitForFunction(() => {
      return (
        customElements.get('wa-button') !== undefined &&
        customElements.get('wa-card') !== undefined &&
        customElements.get('wa-callout') !== undefined &&
        customElements.get('wa-icon') !== undefined
      );
    }, { timeout: 10000 });

    // Assert zero React error #418
    const react418 = errorLogs.filter((l) => l.includes('React error #418') || l.includes('Minified React error #418'));
    expect(react418).toEqual([]);

    // Assert zero Lit SSR hydration errors
    const litErrors = errorLogs.filter((l) => l.includes('hydration') || l.includes('LitElement'));
    expect(litErrors).toEqual([]);
  });
});
