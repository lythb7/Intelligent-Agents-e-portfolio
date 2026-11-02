// Minimal client. All logic that matters lives on the server; this file only
// renders what the dialogue agent returns and posts what the student types.
const messages = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("message");
const tracePanel = document.getElementById("trace-panel");
const traceBox = document.getElementById("trace");
document.getElementById("show-trace").addEventListener("change", (e) => {
  tracePanel.classList.toggle("hidden", !e.target.checked);
});

function bubble(role, text) {
  const div = document.createElement("div");
  div.className = `bubble ${role}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

function renderCard(card) {
  const wrap = document.createElement("div");
  wrap.className = "card";
  if (card.type === "timetable") {
    const table = document.createElement("table");
    table.innerHTML = "<thead><tr><th>Day</th><th>Time</th><th>Module</th><th>Session</th><th>Where</th></tr></thead>";
    const body = document.createElement("tbody");
    for (const e of card.events) {
      const tr = document.createElement("tr");
      for (const cell of [e.weekday_name, `${e.start_time}–${e.end_time}`, `${e.module_code} ${e.title}`, e.kind, e.location]) {
        const td = document.createElement("td"); td.textContent = cell; tr.appendChild(td);
      }
      body.appendChild(tr);
    }
    table.appendChild(body); wrap.appendChild(table);
  } else if (card.type === "assignments") {
    const list = document.createElement("ol");
    for (const a of card.items) {
      const li = document.createElement("li");
      li.textContent = `${a.title} (${a.module_code}) — due ${a.deadline_display} `;
      const link = document.createElement("a");
      link.href = a.url; link.textContent = "Download brief"; link.className = "button-link";
      li.appendChild(link); list.appendChild(li);
    }
    wrap.appendChild(list);
  } else if (card.type === "document") {
    const link = document.createElement("a");
    link.href = card.url; link.textContent = card.label; link.className = "button-link";
    wrap.appendChild(link);
  }
  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  bubble("user", text);
  input.value = "";
  const pending = bubble("bot pending", "…");
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Requested-With": "UniBot" },
      body: JSON.stringify({ message: text }),
    });
    if (res.status === 401) { window.location = "/login"; return; }
    const data = await res.json();
    pending.remove();
    bubble("bot", data.text);
    (data.cards || []).forEach(renderCard);
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = `intent: ${data.intent} · decided by: ${data.intent_source}`;
    messages.appendChild(meta);
    traceBox.textContent = (data.trace || []).map((m) =>
      `(${m.performative}\n  :sender ${m.sender}\n  :receiver ${m.receiver}\n  :conversation ${m.conversation_id}\n  :reply-with ${m.reply_with}` +
      (m.in_reply_to ? `\n  :in-reply-to ${m.in_reply_to}` : "") +
      `\n  :content ${JSON.stringify(m.content, null, 2).replace(/\n/g, "\n    ")})`).join("\n\n") || "(no inter-agent messages this turn)";
    if (data.ended) { input.disabled = true; input.placeholder = "Conversation ended. Sign out or refresh to start again."; }
  } catch (err) {
    pending.remove();
    bubble("bot error", "The server could not be reached. Please try again.");
  }
});

bubble("bot", "Hello! I'm UniBot. Ask me about your timetable, your transcript, or your active assignments.");
