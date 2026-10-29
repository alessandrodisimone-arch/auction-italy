#!/usr/bin/env python3
"""Builds the static site into ./public from ./src, ./data and ./static.

Each page in src/<lang>/<slug>.html starts with a header block:
    <!--
    title: Page title
    description: Meta description
    -->
followed by the page's <main> content. Placeholders like {{EXAMPLES}} are
filled in from data/properties.json.
"""
import json
import re
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "public"
SITE_URL = "https://www.auction-italy.com"
WHATSAPP = "393319416164"
PHONE_DISPLAY = "+39 331 941 6164"

# Page slugs shared by both languages; "" is the home page.
PAGES = ["", "how-it-works", "available-auctions", "prices", "faq", "about-province-of-fermo", "contact"]

T = {
    "en": {
        "prefix": "",
        "nav": {"how-it-works": "How it works", "available-auctions": "Auction examples", "prices": "Prices",
                "faq": "FAQ", "about-province-of-fermo": "Province of Fermo", "contact": "Contact"},
        "tagline": "Court property auctions in Fermo, Marche",
        "cta": "Talk to us",
        "wa_text": "Hello, I would like more information about property auctions",
        "switch": "Italiano",
        "footer_about": "Legal and technical assistance for buyers at public real estate auctions of the Court of Fermo. We are not a real estate agency and we never handle clients' money.",
        "footer_disclaimer": "Auction procedures are managed exclusively by the competent judicial authorities. Property information comes from public sources: always check the official documents on astalegale.net.",
        "menu": "Menu",
        "cats": {"seaside": "Seaside", "countryside": "Countryside", "mountain": "Mountains", "historic": "Historic villages",
                 "modern": "Modern homes", "heritage": "Heritage homes", "fixer": "Fixer-uppers"},
        "bid": "Winning offer level", "value": "Court valuation", "below": "below valuation", "past": "Past auction",
        "all": "All",
    },
    "it": {
        "prefix": "/it",
        "nav": {"how-it-works": "Come funziona", "available-auctions": "Esempi di aste", "prices": "Prezzi",
                "faq": "Domande", "about-province-of-fermo": "Provincia di Fermo", "contact": "Contatti"},
        "tagline": "Aste immobiliari giudiziarie a Fermo, Marche",
        "cta": "Contattaci",
        "wa_text": "Ciao, vorrei maggiori informazioni sulle aste immobiliari",
        "switch": "English",
        "footer_about": "Assistenza legale e tecnica per chi vuole acquistare alle aste immobiliari del Tribunale di Fermo. Non siamo un'agenzia immobiliare e non gestiamo mai il denaro dei clienti.",
        "footer_disclaimer": "Le procedure d'asta sono gestite esclusivamente dalle autorità giudiziarie competenti. Le informazioni sugli immobili provengono da fonti pubbliche: verifica sempre i documenti ufficiali su astalegale.net.",
        "menu": "Menu",
        "cats": {"seaside": "Mare", "countryside": "Campagna", "mountain": "Montagna", "historic": "Borghi storici",
                 "modern": "Case moderne", "heritage": "Dimore di pregio", "fixer": "Da ristrutturare"},
        "bid": "Offerta in asta", "value": "Valore di perizia", "below": "sotto la perizia", "past": "Asta passata",
        "all": "Tutte",
    },
}


def url(lang, slug):
    base = T[lang]["prefix"]
    return f"{base}/{slug}/" if slug else (f"{base}/" if base else "/")


def wa_link(lang):
    from urllib.parse import quote
    return f"https://wa.me/{WHATSAPP}?text={quote(T[lang]['wa_text'])}"


def euro(n, lang):
    s = f"{round(n):,}"
    return "€ " + (s.replace(",", ".") if lang == "it" else s)


def property_card(p, lang):
    t = T[lang]
    discount = round((1 - p["bid"] / p["value"]) * 100)
    return f"""
    <article class="card" data-cat="{p['category']}">
      <div class="card-img">
        <img src="{p['image']}" alt="{escape(p['title'][lang])} – {escape(p['town'])}" loading="lazy" width="800" height="560">
        <span class="badge">{t['past']}</span>
      </div>
      <div class="card-body">
        <p class="card-kicker">{escape(p['town'])} · {t['cats'][p['category']]}</p>
        <h3>{escape(p['title'][lang])}</h3>
        <p class="card-size">{escape(p['size'])}</p>
        <p class="card-text">{escape(p['features'][lang])}</p>
        <dl class="card-prices">
          <div><dt>{t['value']}</dt><dd class="strike">{euro(p['value'], lang)}</dd></div>
          <div><dt>{t['bid']}</dt><dd>{euro(p['bid'], lang)}</dd></div>
        </dl>
        <p class="discount">−{discount}% {t['below']}</p>
      </div>
    </article>"""


def render_examples(props, lang, limit=None):
    items = sorted(props, key=lambda p: p["bid"] / p["value"])
    if limit:
        items = items[:limit]
    return '<div class="cards">' + "".join(property_card(p, lang) for p in items) + "</div>"


def render_filters(props, lang):
    t = T[lang]
    cats = [c for c in t["cats"] if any(p["category"] == c for p in props)]
    btns = [f'<button type="button" class="chip is-active" data-filter="all">{t["all"]}</button>']
    btns += [f'<button type="button" class="chip" data-filter="{c}">{t["cats"][c]}</button>' for c in cats]
    return '<div class="chips" role="toolbar">' + "".join(btns) + "</div>"


def parse_page(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--(.*?)-->", text, re.S)
    meta = {}
    for line in m.group(1).strip().splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def layout(lang, slug, meta, body):
    t = T[lang]
    other = "it" if lang == "en" else "en"
    nav = "".join(
        f'<a href="{url(lang, s)}"{" aria-current=\"page\"" if s == slug else ""}>{label}</a>'
        for s, label in t["nav"].items()
    )
    canonical = SITE_URL + url(lang, slug)
    schema = {
        "@context": "https://schema.org",
        "@type": "LegalService",
        "name": "Auction Italy",
        "url": SITE_URL + "/",
        "telephone": PHONE_DISPLAY.replace(" ", ""),
        "areaServed": {"@type": "AdministrativeArea", "name": "Provincia di Fermo, Marche, Italia"},
        "availableLanguage": ["it", "en"],
        "description": T[lang]["footer_about"],
    }
    year = "2026"
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(meta['title'])}</title>
{'<meta name="robots" content="noindex">' if slug == "thanks" else ""}
<meta name="description" content="{escape(meta['description'])}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{SITE_URL + url('en', slug)}">
<link rel="alternate" hreflang="it" href="{SITE_URL + url('it', slug)}">
<link rel="alternate" hreflang="x-default" href="{SITE_URL + url('en', slug)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(meta['title'])}">
<meta property="og:description" content="{escape(meta['description'])}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="{'it_IT' if lang == 'it' else 'en_GB'}">
<link rel="icon" href="/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{url(lang, '')}">
      <img src="/img/logo.svg" alt="" width="36" height="36">
      <span><strong>Auction Italy</strong><small>{t['tagline']}</small></span>
    </a>
    <button class="menu-toggle" aria-expanded="false" aria-controls="nav">{t['menu']}</button>
    <nav id="nav" class="nav">
      {nav}
      <a class="lang" href="{url(other, slug)}" hreflang="{other}" lang="{other}">{t['switch']}</a>
      <a class="btn btn-small" href="{url(lang, 'contact')}">{t['cta']}</a>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <p class="brand-foot">Auction Italy</p>
      <p>{t['footer_about']}</p>
    </div>
    <div>
      <p class="foot-title">{t['nav']['contact']}</p>
      <p><a href="{wa_link(lang)}">WhatsApp {PHONE_DISPLAY}</a></p>
      <p><a href="{url(lang, 'contact')}">{t['cta']}</a></p>
    </div>
    <div>
      <p class="foot-title">Menu</p>
      {"".join(f'<p><a href="{url(lang, s)}">{label}</a></p>' for s, label in t['nav'].items())}
    </div>
  </div>
  <div class="wrap foot-bottom">
    <p>{t['footer_disclaimer']}</p>
    <p>© {year} Auction Italy</p>
  </div>
</footer>
<a class="wa-float" href="{wa_link(lang)}" aria-label="WhatsApp">
  <svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2c0 1.3.9 2.5 1 2.7.1.2 1.8 2.8 4.4 3.9 1.6.7 2.3.8 3.1.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2l-.6-.3Z"/></svg>
</a>
<script src="/js/site.js" defer></script>
</body>
</html>
"""


def main():
    props = json.loads((ROOT / "data/properties.json").read_text(encoding="utf-8"))
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    sitemap = []
    for lang in ("en", "it"):
        for slug in PAGES + ["thanks"]:
            meta, body = parse_page(ROOT / "src" / lang / f"{slug or 'index'}.html")
            body = (body.replace("{{EXAMPLES_TOP}}", render_examples(props, lang, 3))
                        .replace("{{EXAMPLES}}", render_examples(props, lang))
                        .replace("{{FILTERS}}", render_filters(props, lang))
                        .replace("{{WHATSAPP}}", wa_link(lang))
                        .replace("{{PHONE}}", PHONE_DISPLAY))
            dest = OUT / url(lang, slug).lstrip("/") / "index.html"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(layout(lang, slug, meta, body), encoding="utf-8")
            if slug != "thanks":
                sitemap.append(SITE_URL + url(lang, slug))
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in sitemap) + "</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(sitemap)} pages into {OUT}")


if __name__ == "__main__":
    main()
