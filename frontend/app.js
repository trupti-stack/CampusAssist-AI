const state = { token: "", history: [], busy: false };
const $ = (id) => document.getElementById(id);
const messages = $("messages");
const questionInput = $("question");
const sendButton = $("send-button");

function showError(message) {
  const box = $("chat-error");
  box.textContent = message;
  box.hidden = false;
}
function clearError() { $("chat-error").hidden = true; }
function appendMessage(role, text, extra = "") {
  const row = document.createElement("div");
  row.className = `message ${role === "user" ? "user-message" : "assistant-message"}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "YOU" : "CA";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (extra) bubble.classList.add(extra);
  const title = document.createElement("strong");
  title.textContent = role === "user" ? "You" : "CampusAssist AI";
  const body = document.createElement("p");
  body.textContent = text;
  bubble.append(title, body);
  row.append(avatar, bubble);
  messages.append(row);
  messages.scrollTop = messages.scrollHeight;
  return row;
}
async function checkHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("not healthy");
    $("health-dot").className = "status-dot ok";
    $("health-text").textContent = "Service operational";
  } catch {
    $("health-dot").className = "status-dot bad";
    $("health-text").textContent = "Service unavailable";
  }
}
function setBusy(busy) {
  state.busy = busy;
  sendButton.disabled = busy;
  sendButton.querySelector("span:first-child").textContent = busy ? "Sending…" : "Send";
}
async function sendQuestion(question) {
  const cleaned = question.trim();
  if (!cleaned || state.busy) return;
  clearError();
  if (!state.token) {
    showError("Enter your demo access token in the panel on the right before sending a question.");
    return;
  }
  appendMessage("user", cleaned);
  const previousHistory = state.history.slice(-8);
  state.history.push({ role: "user", content: cleaned });
  questionInput.value = "";
  $("char-count").textContent = "0 / 1500";
  const typing = appendMessage("assistant", "CampusAssist is preparing a response…", "typing");
  setBusy(true);
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${state.token}` },
      body: JSON.stringify({ question: cleaned, history: previousHistory }),
    });
    const data = await response.json().catch(() => ({}));
    typing.remove();
    if (!response.ok) {
      const errorText = data.message || `Request failed (${response.status}).`;
      showError(errorText + (data.request_id ? ` Request ID: ${data.request_id}` : ""));
      state.history.pop();
      return;
    }
    appendMessage("assistant", data.answer || "No answer was returned.");
    state.history.push({ role: "assistant", content: data.answer || "" });
  } catch (error) {
    typing.remove();
    showError("Could not connect to the backend. Check that the FastAPI server is running.");
    state.history.pop();
  } finally {
    setBusy(false);
    questionInput.focus();
  }
}

$("chat-form").addEventListener("submit", (event) => {
  event.preventDefault();
  sendQuestion(questionInput.value);
});
questionInput.addEventListener("input", () => {
  $("char-count").textContent = `${questionInput.value.length} / 1500`;
});
$("clear-chat").addEventListener("click", () => {
  state.history = [];
  messages.innerHTML = "";
  appendMessage("assistant", "Chat cleared. What would you like help with?");
  clearError();
});
$("save-token").addEventListener("click", () => {
  state.token = $("access-token").value.trim();
  $("token-status").textContent = state.token ? "Token is available in this page session." : "No token entered.";
});
$("weather-button").addEventListener("click", async () => {
  const result = $("weather-result");
  if (!state.token) { result.textContent = "Enter your demo access token first."; return; }
  const latitude = Number($("latitude").value);
  const longitude = Number($("longitude").value);
  if (!Number.isFinite(latitude) || latitude < -90 || latitude > 90 || !Number.isFinite(longitude) || longitude < -180 || longitude > 180) {
    result.textContent = "Enter valid latitude and longitude values."; return;
  }
  result.textContent = "Fetching current conditions…";
  try {
    const response = await fetch(`/external-data?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}`, {
      headers: { "Authorization": `Bearer ${state.token}` },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.message || `Weather request failed (${response.status}).`);
    result.innerHTML = `<strong>${escapeHtml(String(data.temperature_c ?? "—"))} °C</strong> · Feels like ${escapeHtml(String(data.apparent_temperature_c ?? "—"))} °C<br>Humidity: ${escapeHtml(String(data.relative_humidity_percent ?? "—"))}% · Wind: ${escapeHtml(String(data.wind_speed_kmh ?? "—"))} km/h<br><span>Observed: ${escapeHtml(String(data.observed_at ?? "unknown"))} (${escapeHtml(String(data.timezone ?? "local time"))})</span>`;
  } catch (error) {
    result.textContent = error.message || "Unable to retrieve weather data.";
  }
});
function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
}
document.querySelectorAll(".suggestion").forEach((button) => {
  button.addEventListener("click", () => {
    questionInput.value = button.dataset.question || "";
    questionInput.dispatchEvent(new Event("input"));
    questionInput.focus();
  });
});
checkHealth();
