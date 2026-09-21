import { test as base, expect } from '@playwright/test';

const test = base.extend<{ javascriptErrors: void }>({
  javascriptErrors: [async ({page}, use) => {
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(String(error)));
    await use();
    expect(errors).toEqual([]);
  }, {auto:true}],
});

test('opt-in console explains advisory validation and sends exact invalid text', async ({ page, request }) => {
  const received: (string | Buffer)[] = [];
  page.on('websocket', socket => socket.on('framereceived', event => received.push(event.payload)));
  const initial = await (await request.get('/probe')).json();
  await page.goto('/interactive/');
  await expect(page.getByText('Validation is advisory', { exact: false })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Connect', exact: true }).first()).toBeVisible();
  expect((await (await request.get('/probe')).json()).connections).toBe(initial.connections);
  const panel = page.getByRole('region', { name: 'WebSocket: send', exact: true });
  await panel.getByRole('button', { name: 'Connect', exact: true }).click();
  const send = panel.getByRole('button', { name: 'Send', exact: true });
  await expect(send).toBeEnabled();
  for (const [text, warning] of [['{"value":"valid"}', ''], ['{"value":123}', 'You can still send it.'], ['not-json', 'It will be sent as plain text.']]) {
    await panel.locator('textarea').fill(text);
    if (warning) await expect(panel.getByText(warning, { exact: false })).toBeVisible();
    await send.click();
    await expect.poll(async () => (await (await request.get('/probe')).json()).frames.at(-1)).toBe(text);
    await expect.poll(() => received.at(-1)).toBe(text);
  }
  await expect(page.getByRole('region', {name:'WebSocket: receive',exact:true}).getByRole('button',{name:'Disconnect',exact:true})).toBeVisible();
  await page.getByRole('button',{name:'Parameters',exact:true}).first().click();
  await expect(send).toBeEnabled();
  const connected = await (await request.get('/probe')).json();
  expect(connected.connections).toBe(initial.connections+1);
  expect(connected.urls.at(-1)).toBe('ws://127.0.0.1:8917/echo/room');
  await page.goto('/asyncapi/');
  await expect.poll(async () => (await (await request.get('/probe')).json()).closed).toBe(connected.closed + 1);
});

test('unsupported wire contracts stay readable and cannot connect', async ({ page, request }) => {
  const before = await (await request.get('/probe')).json();
  await page.route('**/interactive/asyncapi.json', async route => {
    const response = await route.fetch();
    const schema = await response.json();
    for (const message of Object.values(schema.channels.logicalEvents.messages) as any[]) message['x-websocket-mode'] = 'binary';
    await route.fulfill({response,json:schema});
  });
  await page.goto('/interactive/playground');
  await expect(page.getByText('Interactive sending is unavailable', {exact:false}).first()).toBeVisible();
  await expect(page.getByRole('button',{name:'Connect',exact:true})).toHaveCount(0);
  expect((await (await request.get('/probe')).json()).connections).toBe(before.connections);
});

test('upstream refuses unresolved parameters and missing servers', async ({ page, request }) => {
  const before = await (await request.get('/probe')).json();
  let missing = false;
  await page.route('**/interactive/asyncapi.json', async route => {
    const response = await route.fetch();
    const schema = await response.json();
    if (missing) delete schema.servers;
    else schema.channels.logicalEvents.parameters.room = {description:'Unresolved room'};
    await route.fulfill({response,json:schema});
  });
  await page.goto('/interactive/playground');
  await expect(page.getByRole('button',{name:'Connect',exact:true}).first()).toBeDisabled();
  missing = true;
  await page.reload();
  await expect(page.getByText('Configure an explicit ws/wss server', {exact:false})).toBeVisible();
  await expect(page.getByRole('button',{name:'Connect',exact:true})).toHaveCount(0);
  expect((await (await request.get('/probe')).json()).connections).toBe(before.connections);
});

test('upstream tuple composer sends arrays and query credentials', async ({ page, request }) => {
  await page.route('**/interactive/asyncapi.json', async route => {
    const response = await route.fetch();
    const schema = await response.json();
    for (const message of Object.values(schema.channels.logicalEvents.messages) as any[]) {
      message.payload = {type:'array',items:[{type:'string'},{type:'integer'}], minItems:2,maxItems:2};
      message.examples = [{payload:['tuple',2]}];
    }
    schema.servers.echo.security = [{type:'httpApiKey',in:'query',name:'token'}];
    schema.channels.logicalEvents.parameters.room.default = 'secure';
    await route.fulfill({response,json:schema});
  });
  await page.goto('/interactive/playground');
  const panel = page.getByRole('region', {name:'WebSocket: send',exact:true});
  await panel.locator('input[type="password"]').fill('wrong-token');
  await panel.getByRole('button',{name:'Connect',exact:true}).click();
  await expect(page.locator('#asyncapi-status')).toHaveAttribute('role','alert');
  await panel.locator('input[type="password"]').fill('secret-query');
  await panel.getByRole('button',{name:'Reconnect',exact:true}).click();
  await expect(panel.getByRole('button',{name:'Send',exact:true})).toBeEnabled();
  await expect(page.locator('#asyncapi-status')).toHaveAttribute('role','status');
  await expect(page.locator('#asyncapi-status')).toBeEmpty();
  await panel.locator('textarea').fill('["tuple",2]');
  await panel.getByRole('button',{name:'Send',exact:true}).click();
  await expect.poll(async () => (await (await request.get('/probe')).json()).frames.at(-1)).toBe('["tuple",2]');
  expect((await (await request.get('/probe')).json()).urls.at(-1)).toBe('ws://127.0.0.1:8917/echo/secure?token=secret-query');
  await panel.getByRole('button',{name:'Disconnect',exact:true}).click();
  await expect(panel.getByRole('button',{name:'Send',exact:true})).toBeDisabled();
});

test('Scalar links to the shared mounted console and prefixes the socket once', async ({ page, request }) => {
  const before = await (await request.get('/probe')).json();
  await page.goto('/socket-app/docs/');
  await page.getByRole('link',{name:'PLAYGROUND',exact:true}).click();
  await expect(page).toHaveURL(/\/socket-app\/docs\/playground$/);
  const panel = page.getByRole('region',{name:'WebSocket: send',exact:true});
  await panel.getByRole('button',{name:'Connect',exact:true}).click();
  await expect(panel.getByRole('button',{name:'Send',exact:true})).toBeEnabled();
  expect((await (await request.get('/probe')).json()).urls.at(-1)).toBe('ws://127.0.0.1:8917/socket-app/echo/room');
  await page.evaluate(() => window.dispatchEvent(new Event('pagehide')));
  await expect(page.locator('#asyncapi')).toBeEmpty();
  await expect.poll(async () => (await (await request.get('/probe')).json()).closed).toBe(before.closed+1);
  await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted:true})));
  await expect(page.getByRole('button',{name:'Connect',exact:true}).first()).toBeEnabled();
  expect((await (await request.get('/probe')).json()).connections).toBe(before.connections+1);
});

test('restrictive connect CSP surfaces errors without losing downloads', async ({ page, request }) => {
  const before = await (await request.get('/probe')).json();
  await page.route('**/interactive/playground',async route => {
    const response = await route.fetch();
    await route.fulfill({response,headers:{...response.headers(),'content-security-policy': "connect-src http://127.0.0.1:8917"}});
  });
  await page.goto('/interactive/playground');
  await page.getByRole('region',{name:'WebSocket: send',exact:true}).getByRole('button',{name:'Connect',exact:true}).click();
  await expect(page.locator('#asyncapi-status')).toHaveAttribute('role','alert', {timeout:15000});
  await expect(page.getByRole('link',{name:'JSON',exact:true})).toBeVisible();
  expect((await (await request.get('/probe')).json()).connections).toBe(before.connections);
});

test('the real endpoint rejects missing query authentication', async ({page,request}) => {
  const before = await (await request.get('/probe')).json();
  await page.route('**/interactive/asyncapi.json',async route => {
    const response = await route.fetch(); const schema = await response.json();
    schema.channels.logicalEvents.parameters.room.default = 'secure';
    await route.fulfill({response,json:schema});
  });
  await page.goto('/interactive/playground');
  const panel = page.getByRole('region',{name:'WebSocket: send',exact:true});
  await panel.getByRole('button',{name:'Connect',exact:true}).click();
  await expect(page.locator('#asyncapi-status')).toHaveAttribute('role','alert');
  await expect(panel.getByRole('button',{name:'Send',exact:true})).toBeDisabled();
  expect((await (await request.get('/probe')).json()).connections).toBe(before.connections);
});

for (const fallback of ['examples', 'enum']) {
  test(`upstream resolves channel parameter ${fallback}`, async ({page,request}) => {
    await page.route('**/interactive/asyncapi.json', async route => {
      const response = await route.fetch(); const schema = await response.json();
      schema.channels.logicalEvents.parameters.room = {[fallback]:['resolved']};
      await route.fulfill({response,json:schema});
    });
    await page.goto('/interactive/playground');
    const panel = page.getByRole('region',{name:'WebSocket: send',exact:true});
    await panel.getByRole('button',{name:'Connect',exact:true}).click();
    await expect(panel.getByRole('button',{name:'Send',exact:true})).toBeEnabled();
    expect((await (await request.get('/probe')).json()).urls.at(-1)).toBe('ws://127.0.0.1:8917/echo/resolved');
  });
}

test('upstream resolves secure server variables without auto-connecting', async ({page,request}) => {
  const before = await (await request.get('/probe')).json();
  await page.route('**/interactive/asyncapi.json', async route => {
    const response = await route.fetch(); const schema = await response.json();
    schema.servers.echo.protocol = 'wss';
    await route.fulfill({response,json:schema});
  });
  await page.goto('/interactive/playground');
  await expect(page.getByRole('textbox',{name:'WebSocket URL'}).first()).toHaveValue('wss://127.0.0.1:8917/echo/room');
  expect((await (await request.get('/probe')).json()).connections).toBe(before.connections);
});
