import { expect, test } from 'vitest';
import { reactView } from '../view';

test('view unwraps compatible schemas, translates booleans and preserves all literal values', () => {
  const literal = { schemaFormat: 'application/schema+json;version=draft-07', schema: false, $ref: '#/components/schemas/Test/schema' };
  const document = { components: { schemas: { Test: { schemaFormat: literal.schemaFormat, schema: { properties: { denied: false, allowed: true }, example: literal, default: null } }, Ref: { $ref: '#/components/schemas/Test/schema/properties/denied' } } } };
  const result = reactView(document);
  expect(result.components.schemas.Test).toEqual({ properties: { denied: { not: {} }, allowed: {} }, example: literal, default: null });
  expect(result.components.schemas.Ref.$ref).toBe('#/components/schemas/Test/properties/denied');
  expect(document.components.schemas.Test.schema.properties.denied).toBe(false);
});

test('unknown formats and schema-looking literal keys remain untouched', () => {
  const document = { channels: { example: { messages: { default: { payload: { schemaFormat: 'application/avro', schema: { items: false } }, examples: [{ payload: false }] } } } } };
  expect(reactView(document)).toEqual(document);
});

test('nested schema annotations cannot masquerade as a MultiFormat envelope', () => {
  const nested = { type: 'string', schemaFormat: 'application/schema+json;version=draft-07', schema: false };
  const document = { components: { schemas: { Test: { properties: { value: nested } } } } };
  expect(reactView(document)).toEqual(document);
});

test('known websocket binding schema references follow unwrapped components', () => {
  const reference = { $ref: '#/components/schemas/Query/schema' };
  const document = { channels: { test: { bindings: { ws: { query: reference } } } }, components: { channelBindings: { Test: { ws: { headers: reference } } }, schemas: { Query: { schemaFormat: 'application/schema+json;version=draft-07', schema: { type: 'object' } } } } };
  const result = reactView(document);
  expect(result.channels.test.bindings.ws.query.$ref).toBe('#/components/schemas/Query');
  expect(result.components.channelBindings.Test.ws.headers.$ref).toBe('#/components/schemas/Query');
  expect(reference.$ref).toBe('#/components/schemas/Query/schema');
});
