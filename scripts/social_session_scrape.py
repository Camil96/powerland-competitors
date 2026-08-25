#!/usr/bin/env python3.12
"""social_session_scrape.py — Fase 5.2: permanent-gratis socials-scraper.

Gebruikt CAMIL's eigen Firefox-profile (uleqsbna.default) met ingelogde
FB/IG/LinkedIn-sessie. Geen API-key, geen derde partij, geen maandbedrag.
Draait headless; stoort Camil niet (profile is apart van zijn hoofd-profile).

ToS-kanttekening (Camil geaccepteerd 2026-08-25): sessie-scraping schendt
FB/IG/LinkedIn voorwaarden; risico op account-beperking is de prijs van
"permanent gratis". Camil weegt dat af en aanvaardt het.

Gebruik: python social_session_scrape.py [--cid <id>]  (alle als geen cid)
"""
import os, sys, json, re, html, datetime, subprocess

VENV = r"C:/Users/camil.sahnoune/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
PUBLISH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PUBLISH, "data.json")
OUT = os.path.join(PUBLISH, "captures", "social")
FIREFOX_PROFILE = r"C:/Users/camil.sahnoune/AppData/Roaming/Mozilla/Firefox/Profiles/uleqsbna.default"

RUIS = ["respects your privacy", "cookie policy", "e-mailadres of telefoon",
        "nieuwe account aanmaken", "het gebruik van cookies", "alle reacties:",
        "vind ik leuk", "meer opmerkingen", "meer weergeven", "select accept",
        "reject to decline", "skip to main content", "sign in", "log in",
        "aanmelden", "wachtwoord", "log in", "accepteer"]

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    if os.path.exists(VENV):
        subprocess.run([VENV, os.path.abspath(__file__)] + sys.argv[1:], check=True)
        sys.exit(0)
    raise


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(s or "")).strip()


def extract_posts(page, max_posts=12):
    """Haal zichtbare tekstblokken (>=30 chars) van de geopende pagina."""
    try:
        txt = clean(page.inner_text("body"))[:9000]
    except Exception:
        return []
    parts = [clean(p) for p in re.split(r"(?<=[.!?])\s+|\\n", txt)]
    out, seen = [], set()
    for p in parts:
        if 30 <= len(p) <= 600 and p.lower() not in seen:
            if not any(r in p.lower() for r in RUIS):
                seen.add(p.lower())
                out.append(p)
        if len(out) >= max_posts:
            break
    return out


def scrape_channel(browser, url):
    try:
        page = browser.new_page()
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(3500)
        posts = extract_posts(page)
        page.close()
        return posts
    except Exception as e:
        return [f"__ERR__{str(e)[:80]}"]


def scrape_concurrent(cid, d):
    """Scrape FB/IG/LinkedIn voor 1 concurrent. Return dict."""
    comp = next(c for c in d["competitors"] if c["id"] == cid)
    channels = comp.get("social_channels", {})
    result = {"id": cid, "name": comp["name"], "channels": {}, "posts": [], "note": ""}
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True,
                                   firefox_user_data_dir=FIREFOX_PROFILE)
        for plat, info in channels.items():
            if plat not in ("facebook", "instagram", "linkedin"):
                continue
            url = info.get("url") if isinstance(info, dict) else info
            if not url:
                continue
            raw = scrape_channel(browser, url)
            real = [x for x in raw if not x.startswith("__ERR__")]
            result["channels"][plat] = {"url": url, "n_posts": len(real),
                                        "errors": [x for x in raw if x.startswith("__ERR__")]}
            for t in real:
                result["posts"].append({"platform": plat, "caption": t, "text": t})
        browser.close()
    if not result["posts"]:
        result["note"] = "geen posts (profile leeg / niet ingelogd / blocked)"
    return result


def main():
    d = json.load(open(DATA, encoding="utf-8"))
    # simpele --cid X parsing
    cids = []
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--cid" and i + 1 < len(sys.argv):
            cids.append(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    if not cids:
        cids = [c["id"] for c in d["competitors"]]
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    os.makedirs(OUT, exist_ok=True)
    for cid in cids:
        res = scrape_concurrent(cid, d)
        out = os.path.join(OUT, f"{cid}-{ts}.json")
        tmp = out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, out)
        print(f"  {cid}: {len(res['posts'])} posts | kanalen: {list(res['channels'].keys())}")
    print("social_session_scrape klaar")


if __name__ == "__main__":
    main()
