import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: 'frontend/tests',
  testMatch: '*.spec.ts',
  use: { baseURL: 'http://127.0.0.1:8917', browserName: 'chromium' },
  webServer: { command: process.env.ASYNCAPI_BROWSER_SERVER || 'uv run python frontend/tests/server.py', url: 'http://127.0.0.1:8917/asyncapi/asyncapi.json', reuseExistingServer: false },
});
