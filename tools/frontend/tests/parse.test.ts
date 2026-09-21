import { expect, test } from 'vitest';
import { parseForReact } from '../parse';

function document(payload: unknown) {
  return { asyncapi: '3.1.0', info: { title: 'Parser key regression', version: '1' }, channels: { events: { address: '/events', messages: { message: { payload } } } } };
}

test('literal reference keys survive public parser restoration in all data locations', async () => {
  const literal = { $ref: 'https://example.invalid/literal', nested: { $ref: 'file:///never-read' } };
  const input = document({ type: 'object', example: literal, default: literal, const: literal, enum: [literal], 'x-literal': literal });
  Object.assign(input.channels.events.messages.message, { examples: [{ payload: literal }], 'x-extension': literal });
  const parsed = (await parseForReact(input)).json();
  const message = parsed.channels.events.messages.message;
  for (const key of ['example', 'default', 'const', 'x-literal']) expect(message.payload[key]).toEqual(literal);
  expect(message.payload.enum).toEqual([literal]);
  expect(message.examples[0].payload).toEqual(literal);
  expect(message['x-extension']).toEqual(literal);
  expect(input.channels.events.messages.message.payload).toEqual({ type: 'object', example: literal, default: literal, const: literal, enum: [literal], 'x-literal': literal });
});

test('properties named $ref and structural references to them preserve their contracts', async () => {
  const input = document({ type: 'object', properties: { $ref: { type: 'string', description: 'NAMED_REFERENCE_PROPERTY' }, alias: { $ref: '#/channels/events/messages/message/payload/properties/$ref' } }, required: ['$ref'] });
  const parsed = (await parseForReact(input)).json();
  const payload = parsed.channels.events.messages.message.payload;
  expect(payload.properties.$ref.type).toBe('string');
  expect(payload.properties.alias.type).toBe('string');
  expect(payload.required).toEqual(['$ref']);
});

test('literal own __proto__ keys and many aliases restore without prefix collisions', async () => {
  const literal = JSON.parse('{"__proto__":{"$ref":"https://example.invalid/proto"}}');
  const input = document({ type: 'object', example: literal, enum: Array.from({ length: 12 }, (_, index) => ({ $ref: `literal-${index}` })) });
  const parsed = (await parseForReact(input)).json();
  expect(parsed.channels.events.messages.message.payload.example).toEqual(literal);
  expect(parsed.channels.events.messages.message.payload.enum).toEqual(input.channels.events.messages.message.payload.enum);
});

test('named component bindings retain their names and referenced wire data', async () => {
  const input = { ...document({ type: 'string' }), components: { channelBindings: { $ref: { ws: { method: 'GET' } } } } };
  Object.assign(input.channels.events, { bindings: { $ref: '#/components/channelBindings/$ref' } });
  const parsed = (await parseForReact(input)).json();
  expect(parsed.channels.events.bindings.ws.method).toBe('GET');
  expect(parsed.components.channelBindings.$ref.ws.method).toBe('GET');
});
