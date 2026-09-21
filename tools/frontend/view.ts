type Document = Record<string, any>;
const schemaMaps = ['properties', 'patternProperties', 'definitions', '$defs', 'dependentSchemas'];
const schemaSingles = ['additionalProperties', 'additionalItems', 'contains', 'not', 'if', 'then', 'else', 'propertyNames', 'unevaluatedProperties', 'unevaluatedItems'];
const schemaArrays = ['allOf', 'anyOf', 'oneOf', 'prefixItems'];
const compatible = new Set(['application/schema+json;version=draft-07', 'application/schema+json;version=draft-07;charset=utf-8']);
const escape = (token: string) => token.replaceAll('~', '~0').replaceAll('/', '~1');

/** Adapt only the disposable React view, leaving canonical downloads and literal data unchanged. */
export function reactView(document: Document): Document {
  const view = structuredClone(document);
  const moves: [string, string][] = [];
  const references: Document[] = [];
  const object = (value: any): value is Document => value !== null && typeof value === 'object' && !Array.isArray(value);
  function schema(value: any, path: string, envelope = false): any {
    if (value === false) return { not: {} };
    if (value === true) return {};
    if (!object(value)) return value;
    if (envelope && compatible.has(value.schemaFormat) && Object.hasOwn(value, 'schema')) {
      moves.push([path + '/schema', path]);
      return schema(value.schema, path);
    }
    if (typeof value.$ref === 'string') references.push(value);
    for (const key of schemaMaps) if (object(value[key])) {
      for (const name of Object.keys(value[key])) value[key][name] = schema(value[key][name], `${path}/${key}/${escape(name)}`);
    }
    for (const key of schemaSingles) if (Object.hasOwn(value, key)) value[key] = schema(value[key], `${path}/${key}`);
    for (const key of schemaArrays) if (Array.isArray(value[key])) value[key] = value[key].map((item: any, index: number) => schema(item, `${path}/${key}/${index}`));
    if (Array.isArray(value.items)) value.items = value.items.map((item: any, index: number) => schema(item, `${path}/items/${index}`));
    else if (Object.hasOwn(value, 'items')) value.items = schema(value.items, `${path}/items`);
    if (object(value.dependencies)) for (const name of Object.keys(value.dependencies)) {
      if (!Array.isArray(value.dependencies[name])) value.dependencies[name] = schema(value.dependencies[name], `${path}/dependencies/${escape(name)}`);
    }
    return value;
  }
  function message(value: any, path: string) {
    if (!object(value)) return;
    for (const key of ['payload', 'headers']) if (Object.hasOwn(value, key)) value[key] = schema(value[key], `${path}/${key}`, true);
    if (Array.isArray(value.traits)) value.traits.forEach((item: any, index: number) => message(item, `${path}/traits/${index}`));
  }
  function channels(values: any, base: string) {
    if (!object(values)) return;
    for (const [key, channel] of Object.entries(values)) if (object(channel)) {
      for (const [name, value] of Object.entries(channel.messages || {})) message(value, `${base}/${escape(key)}/messages/${escape(name)}`);
      binding(channel.bindings, `${base}/${escape(key)}/bindings`);
    }
  }
  function binding(value: any, path: string) {
    if (!object(value?.ws)) return;
    for (const key of ['query', 'headers']) if (Object.hasOwn(value.ws, key)) value.ws[key] = schema(value.ws[key], `${path}/ws/${key}`);
  }
  for (const [key, value] of Object.entries(view.components?.channelBindings || {})) binding(value, `#/components/channelBindings/${escape(key)}`);
  channels(view.channels, '#/channels');
  channels(view.components?.channels, '#/components/channels');
  for (const key of ['messages', 'messageTraits']) for (const [name, value] of Object.entries(view.components?.[key] || {})) message(value, `#/components/${key}/${escape(name)}`);
  for (const [name, value] of Object.entries(view.components?.schemas || {})) view.components.schemas[name] = schema(value, `#/components/schemas/${escape(name)}`, true);
  moves.sort((a, b) => b[0].length - a[0].length);
  for (const value of references) {
    if (!value.$ref.startsWith('#/')) continue;
    const pointer = '#' + decodeURIComponent(value.$ref.slice(1));
    const move = moves.find(([from]) => pointer === from || pointer.startsWith(from + '/'));
    if (move) value.$ref = '#' + encodeURI(move[1].slice(1) + pointer.slice(move[0].length)).replaceAll('#', '%23');
  }
  return view;
}
