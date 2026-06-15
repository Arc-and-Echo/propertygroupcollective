// Shared CTA modals: rental appraisal + property manager callback.
// Injects the modal markup and wires triggers on any page that loads it.
// Triggers: [data-modal="appraisal"] / [data-modal="manager"], plus the
// legacy hud/outro buttons on the homepage.
(function () {
 const MARKUP = `
 <div class="modal-overlay" id="modal-appraisal" hidden>
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="appraisal-title">
   <button class="modal-close" type="button" aria-label="Close">&times;</button>
   <span class="kicker">FREE RENTAL APPRAISAL</span>
   <h3 id="appraisal-title">What could your property earn?</h3>
   <p class="modal-lede">Tell us about your property and a senior property manager will prepare an appraisal backed by current comparable rentals in your suburb, within one business day.</p>
   <form class="modal-form" data-type="appraisal">
    <input type="text" name="name" placeholder="Your name" required />
    <div class="form-row">
     <input type="tel" name="phone" placeholder="Phone" required />
     <input type="email" name="email" placeholder="Email" required />
    </div>
    <input type="text" name="property" placeholder="Property address and suburb" required />
    <select name="bedrooms">
     <option value="" selected disabled>Bedrooms</option>
     <option>2</option><option>3</option><option>4</option><option>5+</option>
    </select>
    <input type="text" name="website" class="hp-field" tabindex="-1" autocomplete="off" aria-hidden="true" />
    <button class="btn-primary" type="submit">Request My Appraisal</button>
    <p class="form-done" hidden>Thank you. Your request has been received and we will reply within one business day.</p>
    <p class="form-error" hidden>Something went wrong sending your request. Please try again or call us directly.</p>
   </form>
  </div>
 </div>

 <div class="modal-overlay" id="modal-manager" hidden>
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="manager-title">
   <button class="modal-close" type="button" aria-label="Close">&times;</button>
   <div class="manager-card">
    <img src="/images/olivia.jpg?v=3" alt="Olivia Bennett, Senior Property Manager" />
    <div class="manager-meta">
     <span class="kicker">YOUR PROPERTY MANAGER</span>
     <h3 id="manager-title">Olivia Bennett</h3>
     <span class="manager-role">Senior Property Manager</span>
     <p class="manager-quote">"Every owner gets my direct line. Tell me when suits and I will call you, usually the same day."</p>
    </div>
   </div>
   <form class="modal-form" data-type="callback">
    <input type="text" name="name" placeholder="Your name" required />
    <input type="tel" name="phone" placeholder="Best number to call you" required />
    <select name="preferredTime">
     <option value="" selected disabled>Preferred time</option>
     <option>Morning (9am to 12pm)</option>
     <option>Afternoon (12pm to 5pm)</option>
     <option>Early evening (5pm to 7pm)</option>
    </select>
    <input type="text" name="website" class="hp-field" tabindex="-1" autocomplete="off" aria-hidden="true" />
    <button class="btn-primary" type="submit">Request a Callback</button>
    <p class="form-done" hidden>Thank you. Olivia will call you at your preferred time.</p>
    <p class="form-error" hidden>Something went wrong sending your request. Please try again or call us directly.</p>
   </form>
  </div>
 </div>`;

 document.body.insertAdjacentHTML("beforeend", MARKUP);

 const overlays = {
  appraisal: document.getElementById("modal-appraisal"),
  manager: document.getElementById("modal-manager"),
 };
 let open = null;

 function show(which) {
  const ov = overlays[which];
  if (!ov) return;
  // Close the hamburger menu if it is open underneath
  const mb = document.getElementById("menu-btn");
  if (mb && mb.classList.contains("open")) mb.click();
  ov.hidden = false;
  requestAnimationFrame(() => ov.classList.add("open"));
  document.body.style.overflow = "hidden";
  if (window.__lenis) window.__lenis.stop();
  open = ov;
 }
 function hide() {
  if (!open) return;
  const ov = open;
  ov.classList.remove("open");
  setTimeout(() => { ov.hidden = true; }, 250);
  document.body.style.overflow = "";
  if (window.__lenis) window.__lenis.start();
  open = null;
 }

 // Explicit triggers + legacy homepage selectors
 document.querySelectorAll(
  '[data-modal="appraisal"], .hud-cta, .btn-primary[href^="mailto"]'
 ).forEach((el) => {
  el.addEventListener("click", (e) => { e.preventDefault(); show("appraisal"); });
 });
 document.querySelectorAll(
  '[data-modal="manager"], .btn-ghost[href^="tel"]'
 ).forEach((el) => {
  el.addEventListener("click", (e) => { e.preventDefault(); show("manager"); });
 });

 document.querySelectorAll(".modal-close").forEach((b) =>
  b.addEventListener("click", hide));
 Object.values(overlays).forEach((ov) =>
  ov && ov.addEventListener("click", (e) => { if (e.target === ov) hide(); }));
 document.addEventListener("keydown", (e) => { if (e.key === "Escape") hide(); });

 // Back-to-top button: appears after a screen of scrolling
 document.body.insertAdjacentHTML("beforeend",
  `<button class="to-top" type="button" aria-label="Back to top">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5" /><path d="M5 12l7-7 7 7" /></svg>
   </button>`);
 const toTop = document.querySelector(".to-top");
 let topQueued = false;
 window.addEventListener("scroll", () => {
  if (topQueued) return;
  topQueued = true;
  requestAnimationFrame(() => {
   topQueued = false;
   toTop.classList.toggle("show", window.scrollY > window.innerHeight);
  });
 }, { passive: true });
 toTop.addEventListener("click", () => {
  if (window.__lenis) window.__lenis.scrollTo(0, { duration: 1.2 });
  else window.scrollTo({ top: 0, behavior: "smooth" });
 });

 // Submit to the form backend
 document.querySelectorAll(".modal-form").forEach((form) => {
  form.addEventListener("submit", async (e) => {
   e.preventDefault();
   const done = form.querySelector(".form-done");
   const fail = form.querySelector(".form-error");
   const btn = form.querySelector("button[type=submit]");
   done.hidden = true; fail.hidden = true;
   btn.disabled = true; btn.textContent = "Sending...";
   const payload = Object.fromEntries(new FormData(form).entries());
   payload.type = form.dataset.type;
   try {
    const res = await fetch("/api/pgc/enquiry", {
     method: "POST",
     headers: { "Content-Type": "application/json" },
     body: JSON.stringify(payload),
    });
    const out = await res.json();
    if (!res.ok || !out.ok) throw new Error(out.error || res.status);
    done.hidden = false;
    form.querySelectorAll("input, select").forEach((f) => { f.value = ""; });
    btn.textContent = "Sent";
   } catch (err) {
    fail.hidden = false;
    btn.disabled = false;
    btn.textContent = form.dataset.type === "appraisal" ? "Request My Appraisal" : "Request a Callback";
   }
  });
 });
})();
