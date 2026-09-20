(async () => {
  const status = document.getElementById("asyncapi-status");
  try {
    const config = JSON.parse(document.getElementById("asyncapi-config").textContent);
    const response = await fetch(config.schemaUrl, { credentials: "same-origin" });
    if (!response.ok) throw new Error("Schema request failed");
    const schema = await response.json();
    status.textContent = "";
    if (config.entry === "playground") {
      await new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = config.entryUrl;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
      });
      window.asyncapiPlayground(schema, config);
    } else {
      AsyncApiStandalone.render({ schema, config: config.options }, document.getElementById("asyncapi"));
    }
  } catch {
    status.setAttribute("role", "alert");
    status.textContent = "Documentation could not be loaded. Use the schema download link or check access and browser content security settings.";
  }
})();
