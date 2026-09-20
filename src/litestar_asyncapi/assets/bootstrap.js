(async () => {
  window.addEventListener("pageshow", event => {
    if (event.persisted) window.location.reload();
  });
  const status = document.getElementById("asyncapi-status");
  try {
    const config = JSON.parse(document.getElementById("asyncapi-config").textContent);
    const response = await fetch(config.schemaUrl, { credentials: "same-origin" });
    if (!response.ok) throw new Error("Schema request failed");
    const schema = await response.json();
    status.textContent = "";
    if (!schema || !["3.0.0", "3.1.0"].includes(schema.asyncapi) || !schema.info) throw new Error("Invalid document");
    const renderer = await import(config.entryUrl);
    const dispose = await renderer.render(schema, config.options);
    if (typeof dispose === "function") window.addEventListener("pagehide", dispose, { once: true });
  } catch {
    status.setAttribute("role", "alert");
    status.textContent = "Documentation could not be loaded. Use the schema download link or check access and browser content security settings.";
  }
})();
