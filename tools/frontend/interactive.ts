import { createElement, type ComponentType } from 'react';
import { PluginSlot, type AsyncApiPlugin, type ComponentSlotProps, type PluginAPI } from '@asyncapi/react-component';
import { createWsPlugin } from 'asyncapi-ws-plugin';

const containers: unknown[] = ['object', 'array'];

function isJsonContainer(schema: unknown, seen = new WeakSet<object>()): boolean {
  if (typeof schema !== 'object' || schema === null || seen.has(schema)) return false;
  seen.add(schema);
  const { type, oneOf, anyOf } = schema as Record<string, unknown>;
  if (typeof type === 'string') return containers.includes(type);
  if (Array.isArray(type)) {
    return type.some(member => containers.includes(member)) && type.every(member => member === 'null' || containers.includes(member));
  }
  const members = Array.isArray(oneOf) ? oneOf : anyOf;
  return Array.isArray(members) && members.length > 0 && members.every(member => isJsonContainer(member, seen));
}

export function supportsWire(context: ComponentSlotProps<PluginSlot.OPERATION>['context']): boolean {
  const messages = [...context.operation.messages().all(), ...(context.operation.reply()?.messages().all() ?? [])];
  return messages.length > 0 && messages.every(message => {
    const value = message.json();
    const payload = message.payload()?.json();
    return message.contentType()?.split(';')[0].trim().toLowerCase() === 'application/json'
      && [undefined, 'text'].includes(value['x-websocket-mode'])
      && isJsonContainer(payload);
  });
}

export function interactivePlugin(onStatus: (data: unknown) => void): AsyncApiPlugin {
  const upstream = createWsPlugin({ allowUrlEditing: false });
  return {
    ...upstream,
    install(api) {
      api.on("ws:status", onStatus);
      const registerComponent: PluginAPI['registerComponent'] = (slot, component, options) => {
        if (slot !== PluginSlot.OPERATION) return api.registerComponent(slot, component, options);
        const Original = component as ComponentType<ComponentSlotProps<PluginSlot.OPERATION>>;
        const Supported = (props: ComponentSlotProps<PluginSlot.OPERATION>) => supportsWire(props.context)
          ? createElement(Original, props)
          : createElement('p', { role: 'note' }, 'Interactive sending is unavailable for this wire format. Only JSON text object and array contracts are supported; use the schema download for the complete contract.');
        api.registerComponent(PluginSlot.OPERATION, Supported, options);
      };
      return upstream.install({ ...api, registerComponent });
    },
    uninstall(api) { return upstream.uninstall?.(api); },
  };
}
