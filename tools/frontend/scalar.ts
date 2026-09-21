import { createApiReference } from '@scalar/api-reference';
import '@scalar/api-reference/style.css';

export function render(schema: Record<string, unknown>, options: Record<string, unknown>) {
  createApiReference('#asyncapi', { ...options, content: schema, withDefaultFonts: false, agent: { disabled: true }, showDeveloperTools: 'never' });
}
