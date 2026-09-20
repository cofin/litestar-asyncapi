import { Parser } from '@asyncapi/parser';
import { reactView } from './view';

const maps = new Set([
  'channels', 'operations', 'servers', 'messages', 'parameters', 'schemas', 'messageTraits',
  'operationTraits', 'securitySchemes', 'correlationIds', 'replies', 'replyAddresses',
  'serverVariables', 'properties', 'patternProperties', 'definitions', '$defs', 'variables',
  'dependencies', 'dependentSchemas', 'serverBindings', 'channelBindings', 'operationBindings', 'messageBindings',
]);
const literals = new Set(['examples', 'example', 'const', 'default', 'enum']);
const escape = (key: string) => key.replaceAll('~', '~0').replaceAll('/', '~1');

/** Shield data keys from the upstream generic resolver, then restore its public document graph. */
export async function parseForReact(source: Record<string, unknown>) {
  const view = reactView(source);
  let prefix = 'x-litestar-protected-ref-';
  const serialized = JSON.stringify(view);
  while (serialized.includes(prefix)) prefix += '-';
  const aliases = new Map<string, string>();
  const moves: [string, string][] = [];
  const references: Record<string, any>[] = [];
  function protect(value: any, original = '#', target = '#', inMap = false, literal = false): any {
    if (value === null || typeof value !== 'object') return value;
    if (Array.isArray(value)) return value.map((child, index) => protect(child, `${original}/${index}`, `${target}/${index}`, false, literal));
    const output: Record<string, any> = Object.create(null);
    for (const [key, child] of Object.entries(value)) {
      let name = key;
      if ((key === '$ref' || key === '__proto__') && (literal || inMap)) {
        name = prefix + aliases.size;
        aliases.set(name, key);
        if (inMap) moves.push([`${original}/${escape(key)}`, `${target}/${escape(name)}`]);
      }
      output[name] = protect(child, `${original}/${escape(key)}`, `${target}/${escape(name)}`, !inMap && maps.has(key), literal || (!inMap && (literals.has(key) || key.startsWith('x-'))));
      if (key === '$ref' && name === key && typeof child === 'string') references.push(output);
    }
    return output;
  }
  const protectedView = protect(view);
  moves.sort((a, b) => b[0].length - a[0].length);
  for (const value of references) {
    if (!value.$ref.startsWith('#/')) continue;
    const pointer = '#' + decodeURIComponent(value.$ref.slice(1));
    const move = moves.find(([from]) => pointer === from || pointer.startsWith(from + '/'));
    if (move) value.$ref = '#' + encodeURI(move[1].slice(1) + pointer.slice(move[0].length)).replaceAll('#', '%23');
  }
  const { document, diagnostics } = await new Parser().parse(protectedView);
  if (!document || diagnostics.some(item => item.severity === 0)) throw new Error('AsyncAPI document could not be parsed');
  const replacements = [...aliases].sort((a, b) => b[0].length - a[0].length);
  const visited = new WeakSet<object>();
  function restore(value: any): any {
    if (typeof value === 'string') {
      for (const [alias, original] of replacements) value = value.replaceAll(alias, original);
      return value;
    }
    if (value === null || typeof value !== 'object' || visited.has(value)) return value;
    visited.add(value);
    for (const key of Object.keys(value)) {
      const name = aliases.get(key) || key;
      const child = restore(value[key]);
      if (name !== key) delete value[key];
      Object.defineProperty(value, name, { value: child, enumerable: true, writable: true, configurable: true });
    }
    return value;
  }
  restore(document.json());
  return document;
}
