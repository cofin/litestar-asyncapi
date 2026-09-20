import { describe, it, expect } from 'vitest';
import { PluginSlot } from '@asyncapi/react-component';
import { parseForReact } from '../parse';
import { supportsWire } from '../interactive';

async function supported(payload: unknown, extra: Record<string, unknown> = {}, reply?: Record<string, unknown>) {
  const message = { payload, contentType: 'application/json', ...extra };
  const schema = { asyncapi: '3.1.0', info: {title:'Test',version:'1'},
    channels: {events: {address:'/events', messages:{message}}, ...(reply ? {replies:{address:'/replies',messages:{reply}}} : {})},
    operations:{listen:{action:'receive', channel:{$ref:'#/channels/events'}, messages:[{$ref:'#/channels/events/messages/message'}],
      ...(reply ? {reply:{channel:{$ref:'#/channels/replies'},messages:[{$ref:'#/channels/replies/messages/reply'}]}} : {})}} };
  const document = await parseForReact(schema);
  return supportsWire({slot:PluginSlot.OPERATION, document, operation:document.operations().get('listen')!,channel:document.channels().get('events')!,channelName:'events',type:'subscribe' as never});
}

describe('upstream wire-format boundary', () => {
  it('accepts JSON object/array contracts', async () => {
    expect(await supported({type:'object'})).toBe(true);
    expect(await supported({type:'array',items:{type:'string'}})).toBe(true);
  });
  it('declines binary, plain text, strings, unknown and mixed reply contracts', async () => {
    expect(await supported({type:'object'},{'x-websocket-mode':'binary'})).toBe(false);
    expect(await supported({type:'object'},{contentType:'text/plain'})).toBe(false);
    expect(await supported({type:'string'})).toBe(false);
    expect(await supported({})).toBe(false);
    expect(await supported(false)).toBe(false);
    expect(await supported({type:'object'}, {}, {payload:{type:'object'},contentType:'application/json','x-websocket-mode':'binary'})).toBe(false);
  });
});
