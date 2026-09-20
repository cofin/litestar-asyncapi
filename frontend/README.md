# Packaged documentation UI

The default renderer uses AsyncAPI React 3.2.1 with React 18.3.1. Scalar 1.69.2 is selectable through `DocsConfig(renderer="scalar")`; its Agent and default remote fonts are disabled. Scalar currently omits positional tuple schemas, zero-length bounds and boolean payload schemas. Its page links to the complete canonical JSON document and displays this limitation.

React receives a disposable rendering view: recognized Draft07 MultiFormat payload/header/component schemas are unwrapped, boolean schemas become equivalent object schemas, and references into unwrapped schemas follow their new positions. Schema examples, defaults and other literal data remain unchanged. Before parsing, reference-like literal keys and schema property names are reversibly protected from the upstream generic resolver. They are restored through the public parsed document API before React renders, including recursive graphs. Downloads retain the original document. The WebSocket playground remains the separate legacy entry until its upstream replacement is validated.

Build tooling requires Node 22.12 or newer in the Node 22 release line:

```sh
npm ci
npx playwright install chromium
make js-build
make js-test
make browser-test
make build
```

Python consumers do not need Node. Release builds package `assets/ui/manifest.json`, all hashed chunks and styles, and Vite's `THIRD-PARTY-LICENSES.md`. `make build` verifies their inclusion in the wheel and sdist. Static assets are served by the native Litestar static router.

Browser tests block external requests and exercise generated 3.0.0/3.1.0 documents, mounted/custom routes, hostile metadata and readable failure states. Set `ASYNCAPI_BROWSER_SERVER` to a command serving an installed wheel on port 8917 to run the same tests against a distribution outside the source checkout.
