import { expect, test } from '@playwright/test';

for (const route of ['asyncapi', 'v30/asyncapi', 'scalar', 'v30/scalar', 'mounted/docs']) {
  test(`${route} renders packaged UI with external network blocked`, async ({ page }) => {
    const errors: string[] = [];
    const requested: string[] = [];
    page.on('pageerror', error => errors.push(String(error)));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    await page.route('**/*', route => {
      const url = route.request().url(); requested.push(url);
      return url.startsWith('http://127.0.0.1:8917/') ? route.continue() : route.abort();
    });
    const fetchedSchema = page.waitForResponse(response => /\/(asyncapi|contract)\.json$/.test(new URL(response.url()).pathname));
    await page.goto(`/${route}/`);
    await expect(page.locator('#asyncapi')).not.toBeEmpty({ timeout: 20000 });
    await expect(page.locator('#asyncapi-status')).toHaveText('');
    await expect(page.locator('#asyncapi')).toContainText('TupleMessage');
    if (route.includes('scalar')) {
      for (let round = 0; round < 2; round++) {
        const buttons = page.locator('button[aria-expanded="false"]');
        for (let index = await buttons.count() - 1; index >= 0; index--) {
          const button = buttons.nth(index);
          if (await button.isVisible()) await button.click({ timeout: 1000 });
        }
      }
    } else {
      for (let round = 0; round < 3; round++) {
        await page.getByText('Expand all', { exact: true }).evaluateAll(elements => {
          for (const element of elements) if (element.getClientRects().length) (element as HTMLElement).click();
        });
      }
    }
    await expect(page.locator('#asyncapi')).toContainText('TupleMessage');
    await expect(page.locator('#asyncapi')).toContainText('RecursiveMessage');
    await expect(page.locator('#asyncapi')).toContainText('ForbiddenMessage');
    await expect(page.locator('#asyncapi')).toContainText('requestId');
    await expect(page.locator('#asyncapi')).toContainText('example.invalid');
    const visible = await page.locator('#asyncapi').innerText();
    if (route.includes('scalar')) {
      expect(visible).not.toContain('POSITION_ONE_STRING');
      expect(visible).not.toContain('<= 0 items');
      await expect(page.getByRole('note')).toContainText('Scalar currently omits');
    } else {
      expect(visible).toContain('POSITION_ONE_STRING');
      expect(visible).toContain('POSITION_TWO_INTEGER');
      expect(visible).toContain('Never');
      expect(visible).toContain('null');
      expect(visible).toContain('\n2 items\n');
      expect(visible).toContain('<= 0 items');
      expect(visible).toContain('[CIRCULAR]');
      expect(visible).toContain('children');
      expect(visible).toContain('value');
    }
    const config = await page.locator('#asyncapi-config').textContent();
    const document = await (await page.request.get(JSON.parse(config!).schemaUrl)).json();
    expect(await (await fetchedSchema).json()).toEqual(document);
    expect(document.asyncapi).toBe(route.startsWith('v30/') ? '3.0.0' : '3.1.0');
    expect(document.channels.events.messages.ForbiddenMessage.payload.schema).toBe(false);
    expect(errors).toEqual([]);
    expect(await page.evaluate(() => (window as any).pwned)).toBeUndefined();
    expect(requested.filter(url => !url.startsWith('http://127.0.0.1:8917/'))).toEqual([]);
    if (route.includes('scalar')) expect(requested.some(url => /react-.*\.js/.test(url))).toBe(false);
  });
}

test('failed schema fetch and missing renderer asset have readable error states', async ({ page }) => {
  await page.route('**/asyncapi.json', route => route.fulfill({ status: 503, body: 'unavailable' }));
  await page.goto('/asyncapi/');
  await expect(page.getByRole('alert')).toContainText('Documentation could not be loaded');
  await expect(page.getByRole('link', { name: 'JSON', exact: true })).toBeVisible();
  await page.unroute('**/asyncapi.json');
  await page.route('**/react-*.js', route => route.abort());
  await page.reload();
  await expect(page.getByRole('alert')).toContainText('Documentation could not be loaded');
});

test('invalid downloaded document exposes an accessible failure', async ({ page }) => {
  await page.route('**/asyncapi.json', route => route.fulfill({ contentType: 'application/json', body: '{"wrong":"document"}' }));
  await page.goto('/asyncapi/');
  await expect(page.getByRole('alert')).toContainText('Documentation could not be loaded');
});

test('restrictive CSP retains the schema download and readable fallback', async ({ page }) => {
  await page.route('**/asyncapi/', async route => {
    const response = await route.fetch();
    await route.fulfill({ response, headers: { ...response.headers(), 'content-security-policy': "script-src 'none'; style-src 'self'" } });
  });
  await page.goto('/asyncapi/');
  await expect(page.getByRole('status')).toContainText('use the JSON download');
  await expect(page.getByRole('link', { name: 'JSON', exact: true })).toBeVisible();
});

test('literal reference keys display without external resolution', async ({ page }) => {
  const external: string[] = [];
  await page.route('**/*', async route => {
    if (!route.request().url().startsWith('http://127.0.0.1:8917/')) {
      external.push(route.request().url());
      return route.abort();
    }
    if (route.request().url().endsWith('/asyncapi.json')) {
      const response = await route.fetch();
      const document = await response.json();
      const message = document.channels.events.messages.TupleMessage;
      const literal = { $ref: 'https://example.invalid/literal-data', nested: { $ref: 'https://example.invalid/nested-data' } };
      message.examples = [{ payload: { $ref: 'https://example.invalid/literal-example', literalObject: literal } }];
      message['x-literal'] = literal;
      message.payload['x-literal'] = literal;
      message.payload.properties.literalObject = { type: 'object', const: literal, default: literal, enum: [literal], example: literal };
      message.payload.properties.$ref = { type: 'string', description: 'NAMED_REFERENCE_PROPERTY' };
      message.payload.properties.alias = { $ref: '#/channels/events/messages/TupleMessage/payload/properties/$ref' };
      return route.fulfill({ response, json: document });
    }
    return route.continue();
  });
  await page.goto('/asyncapi/');
  await expect(page.locator('#asyncapi')).toContainText('TupleMessage');
  for (let round = 0; round < 3; round++) await page.getByText('Expand all', { exact: true }).evaluateAll(elements => {
    for (const element of elements) if (element.getClientRects().length) (element as HTMLElement).click();
  });
  await expect(page.locator('#asyncapi')).toContainText('https://example.invalid/literal-example');
  await expect(page.locator('#asyncapi')).toContainText('https://example.invalid/literal-data');
  await expect(page.locator('#asyncapi')).toContainText('NAMED_REFERENCE_PROPERTY');
  await expect(page.locator('#asyncapi')).toContainText('$ref');
  await expect(page.locator('#asyncapi')).not.toContainText('x-litestar-protected-ref-');
  expect(external).toEqual([]);
});
