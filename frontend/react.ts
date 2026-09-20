import { createElement } from 'react';
import { createRoot } from 'react-dom/client';
import AsyncApi from '@asyncapi/react-component';
import '@asyncapi/react-component/styles/default.min.css';
import { parseForReact } from './parse';

export async function render(schema: Record<string, unknown>, options: Record<string, unknown>) {
  createRoot(document.getElementById('asyncapi')!).render(createElement(AsyncApi, { schema: await parseForReact(schema), config: options }));
}
