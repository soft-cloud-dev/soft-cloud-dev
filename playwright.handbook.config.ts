import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/handbook-browser',
  timeout: 30_000,
  fullyParallel: false,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  use: {
    baseURL: 'http://127.0.0.1:4174',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: 'PORT=4174 node scripts/serve-test-fixture.mjs _build/html',
    url: 'http://127.0.0.1:4174/',
    reuseExistingServer: false,
    timeout: 15_000,
  },
  projects: [
    {
      name: 'handbook-chromium',
      use: {
        browserName: 'chromium',
        launchOptions: {
          args: ['--disable-dev-shm-usage'],
        },
      },
    },
    { name: 'handbook-webkit', use: { browserName: 'webkit' } },
  ],
});
