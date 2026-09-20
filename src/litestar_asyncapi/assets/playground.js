window.asyncapiPlayground = function(schema, config) {
              const channels = schema.channels || {};
              const enableValidation = config.options.enableValidation;

              function escapeHtml(unsafe) {
                return unsafe
                  .replace(/&/g, "&amp;")
                  .replace(/</g, "&lt;")
                  .replace(/>/g, "&gt;")
                  .replace(/"/g, "&quot;")
                  .replace(/'/g, "&#039;");
              }

              // DOM elements
              const channelSelect = document.getElementById("channel-select");
              const channelInfo = document.getElementById("channel-info");
              const statusIndicator = document.getElementById("status");
              const messageInput = document.getElementById("message-input");
              const validationError = document.getElementById("validation-error");
              const logEl = document.getElementById("log");
              const filterSelect = document.getElementById("filter-select");

              // State
              let ws = null;
              let messageHistory = [];

              // Populate channel selector
              Object.keys(channels).forEach(path => {
                const opt = document.createElement("option");
                opt.value = path;
                opt.textContent = path;
                channelSelect.appendChild(opt);
              });

              // Update channel info when selection changes
              channelSelect.addEventListener("change", () => {
                const path = channelSelect.value;
                if (path && channels[path]) {
                  const ch = channels[path];
                  let info = `<strong>Path:</strong> ${escapeHtml(path)}`;
                  if (ch.description) {
                    info += `<br><strong>Description:</strong> ${escapeHtml(ch.description)}`;
                  }
                  if (ch.messages) {
                    info += `<br><strong>Messages:</strong> ${escapeHtml(Object.keys(ch.messages).join(", "))}`;
                  }
                  channelInfo.innerHTML = info;
                  channelInfo.style.display = "block";
                } else {
                  channelInfo.style.display = "none";
                }
              });

              // Status updates
              function setStatus(status) {
                statusIndicator.className = "status " + status;
              }

              // Logging
              function log(message, type = "info") {
                const time = new Date().toLocaleTimeString();
                const entry = { time, message, type };
                messageHistory.push(entry);
                renderLog();
              }

              function renderLog() {
                const filter = filterSelect.value;
                logEl.innerHTML = "";
                messageHistory.forEach(entry => {
                  if (filter === "all" || filter === entry.type || (filter === "sent" && entry.type === "sent") || (filter === "received" && entry.type === "received")) {
                    const line = document.createElement("div");
                    line.className = entry.type;
                    line.innerHTML = `<span class="timestamp">${escapeHtml(entry.time)}</span>${escapeHtml(entry.message)}`;
                    logEl.appendChild(line);
                  }
                });
                logEl.scrollTop = logEl.scrollHeight;
              }

              filterSelect.addEventListener("change", renderLog);

              // Validation
              function validateJson(text) {
                if (!enableValidation) return { valid: true };
                try {
                  JSON.parse(text);
                  return { valid: true };
                } catch (e) {
                  return { valid: false, error: e.message };
                }
              }

              messageInput.addEventListener("input", () => {
                const result = validateJson(messageInput.value);
                validationError.textContent = result.valid ? "" : result.error;
              });

              // WebSocket connection
              const server = Object.values(schema.servers || {}).find(value =>
                ["ws", "wss"].includes(value.protocol) && typeof value.host === "string" && !value.host.includes("{")
              );
              const connectButton = document.getElementById("connect-btn");
              if (!server) {
                connectButton.disabled = true;
                document.getElementById("asyncapi-status").textContent = "Configure an explicit ws/wss server to connect. Documentation remains available.";
              }
              function wsUrl(key) {
                if (!server) throw new Error("Configure an explicit ws/wss server to connect.");
                const address = channels[key].address || key;
                if (address.includes("{")) throw new Error("Resolve channel parameters before connecting.");
                return `${server.protocol}://${server.host}${server.pathname || ""}/${address.replace(/^\//, "")}`;
              }

              document.getElementById("connect-btn").addEventListener("click", () => {
                const path = channelSelect.value;
                if (!path) {
                  log("Please select a channel first", "error");
                  return;
                }
                if (ws && ws.readyState <= 1) {
                  log("Already connected or connecting", "info");
                  return;
                }

                setStatus("connecting");
                log(`Connecting to ${path}...`, "info");

                try {
                  ws = new WebSocket(wsUrl(path));
                } catch (error) {
                  setStatus("disconnected");
                  log(error.message, "error");
                  return;
                }
                ws.onopen = () => {
                  setStatus("connected");
                  log(`Connected to ${path}`, "info");
                };
                ws.onmessage = (e) => {
                  log(`${e.data}`, "received");
                };
                ws.onclose = () => {
                  setStatus("disconnected");
                  log("Disconnected", "info");
                  ws = null;
                };
                ws.onerror = () => {
                  log("WebSocket error", "error");
                };
              });

              document.getElementById("disconnect-btn").addEventListener("click", () => {
                if (ws) {
                  ws.close();
                }
              });

              // Send message
              document.getElementById("send-btn").addEventListener("click", () => {
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                  log("Not connected", "error");
                  return;
                }
                const text = messageInput.value.trim();
                const result = validateJson(text);
                if (!result.valid) {
                  log("Invalid JSON: " + result.error, "error");
                  return;
                }
                ws.send(text);
                log(text, "sent");
              });

              document.getElementById("clear-input-btn").addEventListener("click", () => {
                messageInput.value = '{"type": "message", "data": ""}';
                validationError.textContent = "";
              });

              document.getElementById("clear-log-btn").addEventListener("click", () => {
                messageHistory = [];
                renderLog();
              });

              document.getElementById("export-btn").addEventListener("click", () => {
                const data = JSON.stringify(messageHistory, null, 2);
                const blob = new Blob([data], { type: "application/json" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "websocket-history.json";
                a.click();
                URL.revokeObjectURL(url);
              });

};
