#!/usr/bin/env python3
"""Generate static per-property pages into property/ from listings-data.js.
Re-run after editing listings-data.js: python3 build-properties.py"""
import json, re, os

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, "property")
os.makedirs(OUT, exist_ok=True)

raw = open(os.path.join(SRC, "listings-data.js")).read()
entries = re.findall(
    r'\{ slug: "([^"]+)", img: "([^"]+)",\s+name: "([^"]+)",\s+suburb: "([^"]+)",\s+desc: "([^"]+)",\s+beds: (\d+), baths: (\d+), cars: (\d+), rent: (\d+),\s+status: "(\w+)" \}',
    raw)
assert len(entries) == 20, f"parsed {len(entries)} listings"

L = [dict(slug=s, img=i, name=n, suburb=su, desc=d, beds=int(b), baths=int(ba),
          cars=int(c), rent=int(r), status=st)
     for s, i, n, su, d, b, ba, c, r, st in entries]

# Style group per 1-based index (matches the generated imagery)
STYLE = {}
for ix in [1, 6, 7, 8, 9, 11]: STYLE[ix] = "modern"
for ix in [4, 5, 10, 12, 13]: STYLE[ix] = "contemporary"
for ix in [3, 14, 15, 16, 17]: STYLE[ix] = "character"
for ix in [2, 18, 19, 20]: STYLE[ix] = "designer"

FEATURES = {
    "modern": ["Ducted air conditioning", "Open-plan living and dining", "Stone benchtops", "Walk-in pantry",
               "Alfresco entertaining area", "Built-in wardrobes", "Remote double garage", "Fully fenced yard", "NBN ready"],
    "contemporary": ["Split-system air conditioning", "Open-plan living", "Dishwasher", "Built-in wardrobes",
                     "Covered outdoor area", "Low-maintenance gardens", "Remote garage", "Fully fenced yard", "Separate laundry"],
    "character": ["Timber floors throughout", "Wide veranda", "Ceiling fans", "Character details",
                  "Established gardens", "Air conditioning to living areas", "Garden shed", "Fully fenced yard", "Indoor-outdoor flow"],
    "designer": ["In-ground swimming pool", "Floor-to-ceiling glass", "Designer lighting", "Stone benchtops",
                 "Butler's pantry", "Outdoor entertaining terrace", "Ducted air conditioning", "Landscaped surrounds", "Remote double garage"],
}

ABOUT = {
    "modern": ("Set across a smart, light-filled floor plan, {name} delivers the kind of move-in-ready modern living "
               "that families in {suburb} consistently shortlist first. {desc}",
               "The heart of the home is an open-plan kitchen, living and dining zone that flows directly to the "
               "alfresco area, with the kitchen featuring stone benchtops, quality appliances and generous storage. "
               "Bedrooms are positioned for privacy, with the master enjoying its own ensuite and walk-in robe.",
               "With ducted air conditioning, a remote double garage and a fully fenced yard, this is comfortable, "
               "low-fuss living in one of the corridor's most in-demand pockets."),
    "contemporary": ("{name} offers easy single-level living with a clean contemporary facade and a practical, "
                     "family-friendly layout. {desc}",
                     "Inside, the open-plan living zone connects to a functional kitchen with dishwasher and ample "
                     "bench space, while all bedrooms include built-in wardrobes. A covered outdoor area overlooks "
                     "the low-maintenance yard, ideal for weekend entertaining.",
                     "Positioned close to schools, transport and shopping, it is a home that simply works, for "
                     "couples and families alike."),
    "character": ("Full of warmth and street appeal, {name} brings classic Queensland character together with the "
                  "comforts tenants expect today. {desc}",
                  "Timber floors, ceiling fans and a wide veranda set the tone, while the updated interior keeps "
                  "daily living easy. The established gardens give the property a settled, leafy outlook that is "
                  "increasingly hard to find in the growth corridor.",
                  "Homes with this much character rarely stay available for long, and inspections are recommended early."),
    "designer": ("{name} is a statement home, an architect-influenced residence that stands apart from anything "
                 "else currently available in {suburb}. {desc}",
                 "Floor-to-ceiling glass draws light deep into the living zones, while the designer kitchen with "
                 "stone benchtops and butler's pantry anchors an entertainer's floor plan. Outside, the terrace and "
                 "in-ground pool create a true resort feel for summer.",
                 "With ducted air conditioning, designer lighting and premium finishes throughout, this is executive "
                 "living at its most polished."),
}

SUBURB = {
    "North Lakes": "North Lakes is the flagship master-planned community of the Moreton Bay corridor, anchored by Westfield North Lakes, Lake Eden and a full complement of schools, medical facilities and dining. Direct access to the Bruce Highway puts the Brisbane CBD within commuting reach, and rental demand here is consistently among the strongest in the region.",
    "Mango Hill": "Mango Hill blends a village feel with serious convenience, two train stations on the Redcliffe Peninsula line, leafy parks, and the North Lakes retail precinct on its doorstep. It is a favourite with professional couples and young families commuting to Brisbane.",
    "Griffin": "Griffin sits quietly beside the Pine River, offering newer homes, riverside walking trails and quick access to both the Bruce Highway and Kallangur station. Its mix of value and location keeps tenant demand strong.",
    "Murrumba Downs": "Murrumba Downs is one of the corridor's established favourites, leafy streets, its own train station, and large blocks within minutes of North Lakes amenities. Families tend to stay long-term here, which makes for stable tenancies.",
    "Kallangur": "Kallangur delivers genuine convenience, rail to Brisbane, the Bruce Highway nearby, and everyday shopping on Anzac Avenue, at a price point that keeps rental demand reliably high across the year.",
    "Dakabin": "Dakabin is one of the fastest-growing pockets of the corridor, with new estates, its own train station and the Westfield precinct minutes away. Near-new homes here attract quality long-term tenants.",
    "Narangba": "Narangba offers a leafy, semi-acreage feel with highly regarded schools and a strong community identity, while keeping rail and highway connections close. It suits tenants looking for space without losing convenience.",
}

SPRITE = '''<svg style="display:none" aria-hidden="true"><defs>
<symbol id="i-bed" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 7v10" /><path d="M2 14h20v3" /><path d="M22 14v-1a4 4 0 0 0-4-4h-8v5" /><circle cx="6" cy="11.5" r="1.6" /></symbol>
<symbol id="i-bath" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h18v2a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4z" /><path d="M6 12V6.5A2.5 2.5 0 0 1 8.5 4 2.5 2.5 0 0 1 11 6.5" /><path d="M6 20l-1 1.5" /><path d="M18 20l1 1.5" /></symbol>
<symbol id="i-car" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 17H3a1 1 0 0 1-1-1v-3.5L4.2 7.8A2 2 0 0 1 6 6.7h12a2 2 0 0 1 1.8 1.1L22 12.5V16a1 1 0 0 1-1 1h-1" /><path d="M2.5 12.5h19" /><circle cx="7.5" cy="17" r="1.8" /><circle cx="16.5" cy="17" r="1.8" /></symbol>
</defs></svg>'''


def similar(me, idx):
    """3 similar: same suburb first, then same style, then neighbours."""
    pool = [(j, o) for j, o in enumerate(L) if j != idx]
    pool.sort(key=lambda t: (t[1]["suburb"] != me["suburb"],
                             STYLE[t[0] + 1] != STYLE[idx + 1]))
    return [o for _, o in pool[:3]]


def card(o):
    status_cls = "listing-status leased" if o["status"] == "leased" else "listing-status"
    status_txt = "Leased" if o["status"] == "leased" else "For Rent"
    return f'''<a class="listing sim-card" href="/property/{o['slug']}.html">
      <div class="listing-media"><img src="/{o['img']}" alt="{o['name']}, {o['suburb']}" loading="lazy" decoding="async" /><span class="{status_cls}">{status_txt}</span></div>
      <div class="listing-body"><h3>{o['name']}</h3><span class="listing-suburb">{o['suburb']}</span>
      <div class="listing-meta"><span><svg class="meta-ic"><use href="#i-bed"/></svg>{o['beds']} Bed</span><span><svg class="meta-ic"><use href="#i-bath"/></svg>{o['baths']} Bath</span><span><svg class="meta-ic"><use href="#i-car"/></svg>{o['cars']} Car</span></div>
      <span class="listing-rent">${o['rent']} <em>per week</em></span></div></a>'''


for idx, p in enumerate(L):
    style = STYLE[idx + 1]
    paras = "\n      ".join(f"<p>{t.format(**p)}</p>" for t in ABOUT[style])
    feats = "\n        ".join(f"<li>{f}</li>" for f in FEATURES[style])
    bond = p["rent"] * 4
    available = "Leased, register your interest for similar homes" if p["status"] == "leased" else "Available now"
    status_txt = "Leased" if p["status"] == "leased" else "For Rent"
    status_cls = "listing-status leased" if p["status"] == "leased" else "listing-status"
    img_abs = "/" + p["img"]
    url = f"https://northlakespropertymanagement.com/property/{p['slug']}.html"
    sims = "\n      ".join(card(o) for o in similar(p, idx))

    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "ItemPage",
        "mainEntity": {
            "@type": "Accommodation",
            "name": f"{p['name']}, {p['suburb']}",
            "description": p["desc"],
            "image": f"https://northlakespropertymanagement.com/{p['img'].split('?')[0]}",
            "numberOfBedrooms": p["beds"],
            "numberOfBathroomsTotal": p["baths"],
            "address": {"@type": "PostalAddress", "addressLocality": p["suburb"], "addressRegion": "QLD", "addressCountry": "AU"},
            "offers": {"@type": "Offer", "price": p["rent"], "priceCurrency": "AUD",
                       "availability": "https://schema.org/InStock" if p["status"] == "rent" else "https://schema.org/SoldOut",
                       "priceSpecification": {"@type": "UnitPriceSpecification", "price": p["rent"], "priceCurrency": "AUD", "unitText": "WEEK"}},
        },
        "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://northlakespropertymanagement.com/"},
            {"@type": "ListItem", "position": 2, "name": "All Listings", "item": "https://northlakespropertymanagement.com/listings.html"},
            {"@type": "ListItem", "position": 3, "name": f"{p['name']}, {p['suburb']}", "item": url},
        ]},
    }, indent=2)

    html = f'''<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{p['name']}, {p['suburb']} | ${p['rent']} per week | North Lakes Property Management</title>
  <meta name="description" content="{p['desc']} {p['beds']} bed, {p['baths']} bath, {p['cars']} car in {p['suburb']} QLD. ${p['rent']} per week." />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{url}" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg?v=1" />
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png?v=1" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="North Lakes Property Management" />
  <meta property="og:title" content="{p['name']}, {p['suburb']} | ${p['rent']} per week" />
  <meta property="og:description" content="{p['desc']}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="https://northlakespropertymanagement.com/{p['img'].split('?')[0]}" />
  <meta property="og:locale" content="en_AU" />
  <meta name="twitter:card" content="summary_large_image" />
  <script type="application/ld+json">
{schema}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/styles.css?v=38" />
</head>
<body class="subpage property-page">

  {SPRITE}

  <nav class="hud solid">
    <a class="hud-brand" href="/">NORTH LAKES<span class="dim">/</span>PROPERTY MANAGEMENT</a>
    <span class="hud-mid">{p['suburb'].upper()}</span>
    <span class="hud-right">
      <a class="hud-cta" href="/#appraisal">GET AN APPRAISAL</a>
      <button class="menu-btn" id="menu-btn" type="button" aria-label="Open menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </span>
  </nav>

  <div class="menu-overlay" id="menu" hidden>
    <button class="menu-x" type="button" aria-label="Close menu">&times;</button>
    <nav class="menu-nav" aria-label="Sections">
      <a href="/"><i>01</i>Home</a>
      <a href="/#services"><i>02</i>Landlord Services</a>
      <a href="/#market"><i>03</i>Market Intelligence</a>
      <a href="/#listings"><i>04</i>Featured Listings</a>
      <a href="/#experience"><i>05</i>Owner Experience</a>
      <a href="/listings.html"><i>06</i>All Listings</a>
      <a href="/login.html"><i>07</i>Owner Portal</a>
      <a href="/#appraisal" data-modal="appraisal"><i>08</i>Get an Appraisal</a>
    </nav>
  </div>

  <main class="prop-wrap">
    <nav class="crumbs" aria-label="Breadcrumb">
      <a href="/">Home</a><i>/</i><a href="/listings.html">All Listings</a><i>/</i><span>{p['name']}, {p['suburb']}</span>
    </nav>

    <div class="prop-hero">
      <img src="{img_abs}" alt="{p['name']}, {p['suburb']}" fetchpriority="high" />
      <span class="{status_cls}">{status_txt}</span>
    </div>

    <header class="prop-head">
      <div>
        <h1>{p['name']}</h1>
        <span class="listing-suburb">{p['suburb']}, QLD</span>
        <div class="listing-meta">
          <span><svg class="meta-ic"><use href="#i-bed"/></svg>{p['beds']} Bed</span>
          <span><svg class="meta-ic"><use href="#i-bath"/></svg>{p['baths']} Bath</span>
          <span><svg class="meta-ic"><use href="#i-car"/></svg>{p['cars']} Car</span>
        </div>
      </div>
      <div class="prop-price">
        <span class="listing-rent">${p['rent']} <em>per week</em></span>
        <span class="prop-bond">Bond ${bond:,}</span>
      </div>
    </header>

    <div class="prop-grid">
      <div class="prop-main">
        <section class="prop-about">
          <h2>About this property</h2>
          {paras}
        </section>

        <section class="prop-features">
          <h2>Property features</h2>
          <ul class="feature-grid">
        {feats}
          </ul>
        </section>

        <section class="prop-info">
          <h2>Property information</h2>
          <dl class="info-table">
            <div><dt>Rent</dt><dd>${p['rent']} per week</dd></div>
            <div><dt>Bond</dt><dd>${bond:,} (4 weeks rent)</dd></div>
            <div><dt>Availability</dt><dd>{available}</dd></div>
            <div><dt>Property type</dt><dd>House</dd></div>
            <div><dt>Preferred lease</dt><dd>12 months</dd></div>
            <div><dt>Pets</dt><dd>Considered on application</dd></div>
          </dl>
        </section>

        <section class="prop-suburb">
          <h2>Living in {p['suburb']}</h2>
          <p>{SUBURB[p['suburb']]}</p>
        </section>
      </div>

      <aside class="prop-aside">
        <div class="enquiry-card">
          <span class="kicker">ENQUIRE</span>
          <h3>{'Register your interest' if p['status'] == 'leased' else 'Arrange an inspection'}</h3>
          <form class="modal-form" id="prop-enquiry">
            <input type="text" name="name" placeholder="Your name" required />
            <input type="tel" name="phone" placeholder="Phone" required />
            <input type="email" name="email" placeholder="Email" required />
            <textarea name="message" placeholder="Message (optional)" rows="3"></textarea>
            <input type="text" name="website" class="hp-field" tabindex="-1" autocomplete="off" aria-hidden="true" />
            <button class="btn-primary" type="submit">Send Enquiry</button>
            <p class="form-done" hidden>Thank you. We will be in touch about this property shortly.</p>
            <p class="form-error" hidden>Something went wrong. Please try again or call us directly.</p>
          </form>
        </div>
        <div class="agent-mini">
          <img src="/images/olivia.jpg?v=3" alt="Olivia Bennett, Senior Property Manager" />
          <div>
            <strong>Olivia Bennett</strong>
            <span>Senior Property Manager</span>
            <button class="btn-ghost agent-call" type="button" data-modal="manager">Request a Callback</button>
          </div>
        </div>
      </aside>
    </div>

    <section class="prop-similar">
      <h2>Similar properties</h2>
      <div class="listing-grid sim-grid">
      {sims}
      </div>
    </section>
  </main>

  <section class="outro">
    <span class="kicker">LANDLORDS</span>
    <h2>Own an investment property in {p['suburb']}?</h2>
    <p>Get a free, data-backed rental appraisal and see what your property could earn under premium management.</p>
    <div class="cta-row">
      <a class="btn-primary" href="/#appraisal" data-modal="appraisal">Get a Rental Appraisal</a>
      <a class="btn-ghost" href="/#appraisal" data-modal="manager">Speak With a Property Manager</a>
    </div>
    <footer class="footer">
      <span>North Lakes Property Management · North Lakes QLD 4509</span>
      <span>Property management across North Lakes, Mango Hill, Griffin, Murrumba Downs, Kallangur, Dakabin and Narangba.</span>
      <span>© 2026 North Lakes Property Management. All rights reserved.</span>
    </footer>
  </section>

  <script src="/modals.js?v=6"></script>
  <script src="/ava.js?v=5"></script>
  <script>
    // Hamburger menu (links navigate to the main pages).
    (function () {{
      const btn = document.getElementById("menu-btn");
      const menu = document.getElementById("menu");
      if (!btn || !menu) return;
      let isOpen = false;
      function setOpen(v) {{
        isOpen = v;
        btn.classList.toggle("open", v);
        btn.setAttribute("aria-expanded", String(v));
        if (v) {{
          menu.hidden = false;
          requestAnimationFrame(() => menu.classList.add("open"));
          document.body.style.overflow = "hidden";
        }} else {{
          menu.classList.remove("open");
          setTimeout(() => {{ menu.hidden = true; }}, 350);
          document.body.style.overflow = "";
        }}
      }}
      btn.addEventListener("click", () => setOpen(!isOpen));
      menu.querySelector(".menu-x").addEventListener("click", () => setOpen(false));
      menu.addEventListener("click", (e) => {{ if (e.target === menu) setOpen(false); }});
      document.addEventListener("keydown", (e) => {{
        if (e.key === "Escape" && isOpen) setOpen(false);
      }});
    }})();
  </script>
  <script>
    // Property enquiry posts to the form backend with the property attached.
    document.getElementById("prop-enquiry").addEventListener("submit", async (e) => {{
      e.preventDefault();
      const form = e.target;
      const done = form.querySelector(".form-done");
      const fail = form.querySelector(".form-error");
      const btn = form.querySelector("button[type=submit]");
      done.hidden = true; fail.hidden = true;
      btn.disabled = true; btn.textContent = "Sending...";
      const payload = Object.fromEntries(new FormData(form).entries());
      payload.type = "property";
      payload.property = "{p['name']}, {p['suburb']}";
      try {{
        const res = await fetch("/api/nlpm/enquiry", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify(payload),
        }});
        const out = await res.json();
        if (!res.ok || !out.ok) throw new Error(out.error || res.status);
        done.hidden = false;
        form.querySelectorAll("input, textarea").forEach((f) => {{ f.value = ""; }});
        btn.textContent = "Sent";
      }} catch (err) {{
        fail.hidden = false;
        btn.disabled = false;
        btn.textContent = "Send Enquiry";
      }}
    }});
  </script>
</body>
</html>
'''
    open(os.path.join(OUT, p["slug"] + ".html"), "w").write(html)

print(f"generated {len(L)} property pages in property/")
