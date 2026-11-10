import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/handbook-browser',
  timeout: 30_000,
  fullyParallel: false,
  retries: 0,
  workers: 1,
  use: {
    baseURL: 'http://127.0.0.1:4174',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: 'python3 -m http.server 4174 --bind 127.0.0.1 --directory _build/html',
    url: 'http://127.0.0.1:4174/',
    reuseExistingServer: false,
    timeout: 15_000,
  },
  projects: [
    { name: 'handbook-chromium', use: { browserName: 'chromium' } },
    { name: 'handbook-webkit', use: { browserName: 'webkit' } },
  ],
});
