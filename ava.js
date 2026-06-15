// Ava  on-site real estate chat widget.
(function () {
 document.body.insertAdjacentHTML("beforeend", `
 <button class="ava-launch" id="ava-launch" type="button" aria-label="Chat with Ava">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
   <path d="M21 11.5a8.38 8.38 0 0 1-9 8.4 8.5 8.5 0 0 1-3.4-.7L3 21l1.8-5.6A8.38 8.38 0 0 1 3.6 11.5a8.5 8.5 0 0 1 8.7-8.4 8.5 8.5 0 0 1 8.7 8.4z"/>
   <circle cx="8.4" cy="11.5" r="0.5" fill="currentColor"/>
   <circle cx="12" cy="11.5" r="0.5" fill="currentColor"/>
   <circle cx="15.6" cy="11.5" r="0.5" fill="currentColor"/>
  </svg>
 </button>
 <div class="ava-panel" id="ava-panel" hidden>
  <header class="ava-head">
   <span class="ava-avatar">A</span>
   <div>
    <strong>Ava</strong>
    <span>AI real estate assistant</span>
   </div>
   <button class="ava-restart" id="ava-restart" type="button" aria-label="Restart chat" title="Start over">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/></svg>
   </button>
   <button class="ava-close" id="ava-close" type="button" aria-label="Close chat">&times;</button>
  </header>
  <div class="ava-msgs" id="ava-msgs"></div>
  <form class="ava-input" id="ava-form">
   <input type="text" id="ava-text" placeholder="Ask a question or get something calculated..." autocomplete="off" maxlength="500" />
   <button class="ava-send" type="submit" aria-label="Send">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4z"/></svg>
   </button>
  </form>
  <span class="ava-disclaimer">Ava is an AI assistant. General information only, not financial or legal advice.</span>
 </div>`);

 const launch = document.getElementById("ava-launch");
 const panel = document.getElementById("ava-panel");
 const msgs = document.getElementById("ava-msgs");
 const form = document.getElementById("ava-form");
 const input = document.getElementById("ava-text");
 const history = [];
 let busy = false;

 const INTRO = `<div class="ava-msg bot">Hi, I'm Ava. Ask me anything about Australian real estate, or I can work out loan repayments and what you might be able to borrow.</div>
   <div class="ava-chips" id="ava-chips">
    <button type="button">Calculate my repayments</button>
    <button type="button">What could I borrow?</button>
    <button type="button">QLD rent increase rules</button>
   </div>`;

 function reset() {
  history.length = 0;
  busy = false;
  msgs.innerHTML = INTRO;
  msgs.querySelectorAll(".ava-chips button").forEach((b) =>
   b.addEventListener("click", () => send(b.textContent)));
  input.value = "";
  input.focus();
 }

 function toggle(open) {
  if (open) {
   panel.hidden = false;
   requestAnimationFrame(() => panel.classList.add("open"));
   launch.classList.add("hide");
   input.focus();
  } else {
   panel.classList.remove("open");
   setTimeout(() => { panel.hidden = true; }, 250);
   launch.classList.remove("hide");
  }
 }
 launch.addEventListener("click", () => toggle(true));
 document.getElementById("ava-close").addEventListener("click", () => toggle(false));

 function add(role, text) {
  const div = document.createElement("div");
  div.className = "ava-msg " + (role === "user" ? "user" : "bot");
  div.textContent = text;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
 }

 async function send(text) {
  if (busy || !text.trim()) return;
  busy = true;
  const chips = document.getElementById("ava-chips");
  if (chips) chips.remove();
  add("user", text);
  history.push({ role: "user", content: text });
  input.value = "";
  const typing = document.createElement("div");
  typing.className = "ava-msg bot ava-typing";
  typing.innerHTML = "<i></i><i></i><i></i>";
  msgs.appendChild(typing);
  msgs.scrollTop = msgs.scrollHeight;
  try {
   const res = await fetch("/api/pgc/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages: history.slice(-16) }),
   });
   const out = await res.json();
   typing.remove();
   if (!res.ok || !out.ok) throw new Error(out.error || res.status);
   add("bot", out.reply);
   history.push({ role: "assistant", content: out.reply });
  } catch (err) {
   typing.remove();
   add("bot", "Sorry, I had trouble answering just now. Please try again in a moment.");
  }
  busy = false;
 }

 form.addEventListener("submit", (e) => { e.preventDefault(); send(input.value); });
 document.getElementById("ava-restart").addEventListener("click", reset);
 reset();
})();
