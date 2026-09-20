import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Parser } from '@asyncapi/parser';
import specs from '@asyncapi/specs';
import Ajv from 'ajv';

const fixtureDirectory = fileURLToPath(new URL('../src/tests/fixtures/asyncapi/', import.meta.url));
const validators = new Map();
for (const version of ['3.0.0', '3.1.0']) {
  // The official bundle embeds its Draft07 meta-schema; avoid registering a second copy.
  const ajv = new Ajv({ strict: false, allErrors: true, validateFormats: false, meta: false, validateSchema: false });
  validators.set(version, ajv.compile(specs.schemas[version]));
}

const objectMaps = new Set([
  'channels', 'operations', 'servers', 'messages', 'parameters', 'schemas', 'messageTraits',
  'operationTraits', 'securitySchemes', 'correlationIds', 'replies', 'replyAddresses',
  'serverVariables', 'properties', 'patternProperties', 'definitions', '$defs', 'variables', 'dependencies', 'dependentSchemas',
]);
const literalFields = new Set(['examples', 'example', 'const', 'default', 'enum']);

function parserInput(value, location = [], inMap = false, literal = false) {
  if (!value || typeof value !== 'object') return value;
  if (Array.isArray(value)) return value.map((child, index) => parserInput(child, location.concat(index), false, literal));
  const result = Object.create(null);
  for (const [key, child] of Object.entries(value)) {
    // Spectral resolves literal $ref keys too. The original is schema-validated unchanged;
    // only the parser's disposable view hides these data keys from its generic resolver.
    if (key === '$ref' && literal) continue;
    if (!inMap && key === '$ref' && (typeof child !== 'string' || !child.startsWith('#'))) {
      throw new Error(`${location.concat(key).join('/')}: external-reference: Only document-local references are allowed`);
    }
    result[key] = parserInput(child, location.concat(key), !inMap && objectMaps.has(key), literal || (!inMap && (literalFields.has(key) || key.startsWith('x-'))));
  }
  return result;
}

async function validate(input, label) {
  const validator = validators.get(input.asyncapi);
  if (!validator) throw new Error(`${label}: unsupported-version: ${input.asyncapi}`);
  const errors = [];
  if (!validator(input)) {
    for (const error of validator.errors) errors.push(`${label}${error.instancePath}: official-schema/${error.keyword}: ${error.message}`);
  }
  const parseable = parserInput(input, [label]);
  const { document, diagnostics } = await new Parser().parse(parseable);
  for (const diagnostic of diagnostics) {
    if (diagnostic.severity === 0) errors.push(`${label}/${diagnostic.path.join('/')}: ${diagnostic.code}: ${diagnostic.message}`);
  }
  if (!document) errors.push(`${label}: parser-document: Parser returned no document`);
  if (errors.length) throw new Error(errors.join('\n'));
}

async function rejection(document, name, mutate, expected) {
  const invalid = structuredClone(document);
  mutate(invalid);
  await assert.rejects(() => validate(invalid, name), expected);
  console.log(`Rejected isolated mutation: ${name}`);
}

async function verifyGate(document) {
  await rejection(document, 'operationId', value => { value.operations.listen.operationId = 'invalid'; }, /operationId|additional properties/);
  await rejection(document, 'dangling reference', value => { value.operations.listen.channel.$ref = '#/channels/missing'; }, /unresolved-ref|does not exist|not exist|Invalid reference/);
  await rejection(document, 'message membership', value => { value.operations.listen.messages = [{ $ref: '#/channels/replies/messages/reply' }]; }, /channel.*message|message.*channel/i);
  await rejection(document, 'example shape', value => { value.channels.events.messages.text.examples = ['invalid']; }, /examples.*|must be object/);
  for (const reference of ['https://example.invalid/schema.json', 'http://example.invalid/schema.json', 'file:///etc/passwd', './other.json', '//example.invalid/schema.json']) {
    await rejection(document, `external reference ${reference}`, value => { value.operations.listen.channel.$ref = reference; }, /external-reference/);
  }
  await rejection(document, 'channel named examples', value => { value.channels.examples = { $ref: 'file:///etc/passwd' }; }, /external-reference/);
  await rejection(document, 'property named default', value => { value.channels.events.messages.text.payload.properties.default = { $ref: 'https://example.invalid/schema' }; }, /external-reference/);
  const namedReference = structuredClone(document);
  namedReference.channels.events.messages.text.payload.properties.$ref = { type: 'string' };
  assert.equal(validators.get(document.asyncapi)(namedReference), true);
  await assert.rejects(() => validate(namedReference, 'upstream property named $ref discrepancy'), /uncaught-error:.*path.startsWith is not a function/);
  console.log('Known parser limitation: valid property named $ref triggers upstream normalization error');
  const payload = document.channels.events.messages.tuple.payload;
  const validatePayload = new Ajv({ strict: false }).compile(payload);
  assert.equal(validatePayload(['message', 1]), true);
  for (const invalid of [[1, 'message'], ['message'], ['message', 1, 2]]) assert.equal(validatePayload(invalid), false);
  console.log('Draft07 tuple instances: valid order accepted; swapped types and both incorrect lengths rejected');
}

try {
  const requested = process.argv.slice(2);
  const files = requested.length ? requested : (await readdir(fixtureDirectory)).filter(name => name.endsWith('.json')).sort().map(name => path.join(fixtureDirectory, name));
  for (const file of files) {
    const document = JSON.parse(await readFile(file, 'utf8'));
    await validate(document, file);
    console.log(`Validated: ${file}`);
    if (!requested.length && path.basename(file).startsWith('websocket-')) await verifyGate(document);
    if (!requested.length && path.basename(file).startsWith('boolean-')) {
      await rejection(document, 'upstream direct-boolean discrepancy', value => { value.channels.never.messages.never.payload = false; }, /official-schema/);
    }
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
