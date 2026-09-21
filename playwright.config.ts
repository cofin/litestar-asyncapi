import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: 'tools/frontend/tests',
  testMatch: '*.spec.ts',
  outputDir: '.tmp/test-results',
  use: { baseURL: 'http://127.0.0.1:8917', browserName: 'chromium' },
  webServer: { command: process.env.ASYNCAPI_BROWSER_SERVER || 'uv run python tools/frontend/tests/server.py', url: 'http://127.0.0.1:8917/asyncapi/asyncapi.json', reuseExistingServer: false },
});
