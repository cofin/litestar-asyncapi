import { createElement } from 'react';
import { createRoot } from 'react-dom/client';
import AsyncApi, { PLUGIN_EVENT_ERROR } from '@asyncapi/react-component';
import '@asyncapi/react-component/styles/default.min.css';
import { parseForReact } from './parse';

export async function render(schema: Record<string, unknown>, options: Record<string, unknown>) {
  const { interactive, ...config } = options;
  const root = createRoot(document.getElementById('asyncapi')!);
  const onPluginEvent = (event: string, data: unknown) => {
    if (event === 'ws:status' && (data as { status?: string })?.status === 'open') {
      const status = document.getElementById('asyncapi-status')!;
      status.setAttribute('role', 'status');
      status.textContent = '';
    }
    if (event === PLUGIN_EVENT_ERROR || (event === 'ws:status' && ['blocked-precheck', 'closed-unexpected'].includes((data as { status: string })?.status))) {
      const status = document.getElementById('asyncapi-status')!;
      status.setAttribute('role', 'alert');
      status.textContent = 'WebSocket interaction failed. Check connection details, access and browser content security settings; the schema download remains available.';
    }
  };
  const plugins = interactive ? [(await import('./interactive')).interactivePlugin(data => onPluginEvent('ws:status', data))] : [];
  root.render(createElement(AsyncApi, { schema: await parseForReact(schema), config,
    plugins, onPluginEvent }));
  return () => root.unmount();
}
