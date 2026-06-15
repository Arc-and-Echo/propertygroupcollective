// Shared listings renderer + filter + lightbox.
// Used by index.html (featured mode: first 6 until a filter is applied)
// and listings.html (all mode: full catalogue).
(function () {
 const grid = document.getElementById("listing-grid");
 if (!grid || !window.LISTINGS) return;
 const mode = grid.dataset.mode || "all";
 const FEATURED_COUNT = 8;

 const state = { status: "all", suburb: "all" };

 const icon = (k) => `<svg class="meta-ic"><use href="#i-${k}"/></svg>`;

 function cardHTML(l, i, featured) {
  const statusCls = l.status === "leased" ? "listing-status leased" : "listing-status";
  const statusTxt = l.status === "leased" ? "Leased" : "For Rent";
  return `<article class="listing${featured ? " featured" : ""}" style="animation-delay:${Math.min(i * 60, 420)}ms" data-tilt>
   <div class="listing-media">
    <img src="${l.img}" alt="${l.name}, ${l.suburb}" loading="lazy" decoding="async" />
    <span class="${statusCls}">${statusTxt}</span>
   </div>
   <div class="listing-body">
    <h3>${l.name}</h3>
    <span class="listing-suburb">${l.suburb}</span>
    <p class="listing-desc">${l.desc}</p>
    <div class="listing-meta">
     <span>${icon("bed")}${l.beds} Bed</span><span>${icon("bath")}${l.baths} Bath</span><span>${icon("car")}${l.cars} Car</span>
    </div>
    <span class="listing-rent">$${l.rent} <em>per week</em></span>
   </div>
  </article>`;
 }

 let visible = [];
 function render() {
  const filtered = window.LISTINGS.filter((l) =>
   (state.status === "all" || l.status === state.status) &&
   (state.suburb === "all" || l.suburb === state.suburb));
  const unfiltered = state.status === "all" && state.suburb === "all";
  visible = (mode === "featured" && unfiltered)
   ? filtered.slice(0, FEATURED_COUNT)
   : filtered;
  grid.innerHTML = visible.length
   ? visible.map((l, i) => cardHTML(l, i, mode === "featured" && unfiltered && i === 0)).join("")
   : `<p class="no-results">No properties match that filter right now. Try another suburb or status.</p>`;
  bindTilt();
 }

 // Filter bar
 document.querySelectorAll(".f-pill").forEach((b) => {
  b.addEventListener("click", () => {
   document.querySelectorAll(".f-pill").forEach((x) => x.classList.toggle("active", x === b));
   state.status = b.dataset.status;
   render();
  });
 });
 const suburbSel = document.getElementById("f-suburb");
 if (suburbSel) suburbSel.addEventListener("change", () => {
  state.suburb = suburbSel.value;
  render();
 });

 // Card tilt (mirrors the site-wide data-tilt behaviour for dynamic cards)
 function bindTilt() {
  if (window.matchMedia("(hover: none)").matches) return;
  grid.querySelectorAll("[data-tilt]").forEach((el) => {
   const imgs = [...el.querySelectorAll("img")];
   let er = null, queued = false, last = null;
   el.addEventListener("mouseenter", () => { er = el.getBoundingClientRect(); });
   el.addEventListener("mousemove", (e) => {
    last = e;
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => {
     queued = false;
     if (!er) er = el.getBoundingClientRect();
     const x = (last.clientX - er.left) / er.width - 0.5;
     const y = (last.clientY - er.top) / er.height - 0.5;
     el.style.transform = `perspective(900px) rotateY(${x * 6}deg) rotateX(${-y * 5}deg)`;
     imgs.forEach((img) => { img.style.transform = `scale(1.07) translate(${-x * 10}px, ${-y * 10}px)`; });
    });
   });
   el.addEventListener("mouseleave", () => {
    er = null;
    el.style.transform = "perspective(900px) rotateY(0) rotateX(0)";
    imgs.forEach((img) => { img.style.transform = "scale(1.02) translate(0, 0)"; });
   });
  });
 }

 // Lightbox (delegated; works across re-renders)
 const lb = document.getElementById("lightbox");
 if (lb) {
  const img = document.getElementById("lb-img");
  const f = {
   title: document.getElementById("lb-title"),
   suburb: document.getElementById("lb-suburb"),
   desc: document.getElementById("lb-desc"),
   meta: document.getElementById("lb-meta"),
   rent: document.getElementById("lb-rent"),
   status: document.getElementById("lb-status"),
  };
  let idx = -1;

  function fill(i) {
   idx = (i + visible.length) % visible.length;
   const l = visible[idx];
   img.src = l.img;
   img.alt = `${l.name}, ${l.suburb}`;
   f.title.textContent = l.name;
   f.suburb.textContent = l.suburb;
   f.desc.textContent = l.desc;
   f.meta.innerHTML = `<span>${icon("bed")}${l.beds} Bed</span><span>${icon("bath")}${l.baths} Bath</span><span>${icon("car")}${l.cars} Car</span>`;
   f.rent.innerHTML = `$${l.rent} <em>per week</em>`;
   f.status.textContent = l.status === "leased" ? "Leased" : "For Rent";
   f.status.className = l.status === "leased" ? "listing-status leased" : "listing-status";
  }
  function openAt(i) {
   fill(i);
   lb.hidden = false;
   requestAnimationFrame(() => lb.classList.add("open"));
   document.body.style.overflow = "hidden";
   if (window.__lenis) window.__lenis.stop();
  }
  function close() {
   lb.classList.remove("open");
   setTimeout(() => { lb.hidden = true; }, 250);
   document.body.style.overflow = "";
   if (window.__lenis) window.__lenis.start();
   idx = -1;
  }

  // Cards navigate to their dedicated property page.
  grid.addEventListener("click", (e) => {
   const card = e.target.closest(".listing");
   if (!card) return;
   const i = [...grid.querySelectorAll(".listing")].indexOf(card);
   if (visible[i] && visible[i].slug) {
    window.location.href = "/property/" + visible[i].slug + ".html";
   }
  });
  lb.querySelector(".lb-close").addEventListener("click", close);
  lb.querySelector(".lb-prev").addEventListener("click", () => fill(idx - 1));
  lb.querySelector(".lb-next").addEventListener("click", () => fill(idx + 1));
  lb.addEventListener("click", (e) => { if (e.target === lb) close(); });
  document.addEventListener("keydown", (e) => {
   if (idx < 0) return;
   if (e.key === "Escape") close();
   if (e.key === "ArrowLeft") fill(idx - 1);
   if (e.key === "ArrowRight") fill(idx + 1);
  });
 }

 render();
})();
