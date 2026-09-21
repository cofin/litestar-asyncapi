import { defineConfig } from 'vite';
import { nodePolyfills } from 'vite-plugin-node-polyfills';

export default defineConfig({
  base: './',
  plugins: [nodePolyfills({ include: ['buffer', 'util', 'stream', 'events', 'path', 'process'] })],
  build: {
    outDir: 'src/litestar_asyncapi/assets/ui',
    emptyOutDir: true,
    manifest: 'manifest.json',
    license: { fileName: 'THIRD-PARTY-LICENSES.md' },
    rolldownOptions: { preserveEntrySignatures: 'strict', input: { react: 'tools/frontend/react.ts', scalar: 'tools/frontend/scalar.ts' } },
  },
});
