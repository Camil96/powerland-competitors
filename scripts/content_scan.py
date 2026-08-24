#!/usr/bin/env python3.12
"""content_scan.py — Optie 2: website + RSS/nieuwsroom capture ZONDER sessie.

Haalt per concurrent de publieke website-tekst + RSS/Atom feed-items binnen en
schrijft naar content_raw/<id>/<YYYYMMDD-HHMM>.json. Geen login nodig.

Verschil met posts_scan.py: die scrape socials via jouw browser-sessie (Optie 1).
Deze weg gebruikt ENKEL publieke website + feed — robuust, gratis, geen storen.
"""
import os, sys, json, re, html, datetime, subprocess
import xml.etree.ElementTree as ET

VENV = r"C:/Users/camil.sahnoune/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
PUBLISH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PUBLISH, "data.json")
OUT = os.path.join(PUBLISH, "content_raw")

# self re-exec onder venv als playwright ontbreekt (zie powerland_capture patroon)
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    if os.path.exists(VENV):
        subprocess.run([VENV, os.path.abspath(__file__)], check=True)
        sys.exit(0)
    raise

DEFAULT_FEEDS = ["/feed/", "/rss/", "/atom.xml", "/feed.xml", "/blog/feed/", "/news/feed/"]


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(s or "")).strip()


def extract_feed_url(page):
    """Zoek RSS/Atom link in <head>, anders probeer standaard paden."""
    try:
        href = page.eval_on_selector(
            'link[type="application/rss+xml"], link[type="application/atom+xml"]',
            "el => el.getAttribute('href')")
        if href:
            return href if href.startswith("http") else None, href
    except Exception:
        pass
    return None, None


def parse_feed(body_text):
    """Parse RSS of Atom; geef lijst van {title, date, summary, link}."""
    items = []
    try:
        root = ET.fromstring(body_text)
    except Exception:
        return items
    # RSS
    for it in root.iter("item"):
        items.append({
            "title": (it.findtext("title") or "").strip(),
            "date": (it.findtext("pubDate") or "").strip(),
            "summary": clean((it.findtext("description") or "")[:400]),
            "link": (it.findtext("link") or "").strip(),
        })
    # Atom
    ns = "{http://www.w3.org/2005/Atom}"
    for e in root.iter(ns + "entry"):
        items.append({
            "title": (e.findtext(ns + "title") or "").strip(),
            "date": (e.findtext(ns + "updated") or e.findtext(ns + "published") or "").strip(),
            "summary": clean((e.findtext(ns + "summary") or "")[:400]),
            "link": (e.find(ns + "link").get("href") if e.find(ns + "link") is not None else ""),
        })
    return items


def main():
    d = json.load(open(DATA, encoding="utf-8"))
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    os.makedirs(OUT, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for c in d["competitors"]:
            cid = c["id"]
            domain = c.get("domain")
            if not domain:
                continue
            rec = {"id": cid, "domain": domain, "website_text": "", "feed_url": None, "feed_items": []}
            try:
                page = browser.new_page()
                page.goto(domain, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(2500)
                # website-text
                try:
                    rec["website_text"] = clean(page.inner_text("body"))[:9000]
                except Exception:
                    pass
                # feed-detectie
                abs_url, rel = extract_feed_url(page)
                candidates = []
                if abs_url:
                    candidates.append(abs_url)
                if rel:
                    from urllib.parse import urljoin
                    candidates.append(urljoin(domain, rel))
                from urllib.parse import urlparse
                base = f"{urlparse(domain).scheme}://{urlparse(domain).netloc}"
                candidates += [base + f for f in DEFAULT_FEEDS]
                for cand in candidates:
                    try:
                        rb = page.goto(cand, timeout=15000, wait_until="domcontentloaded")
                        if rb and rb.status < 400:
                            txt = page.content()
                            items = parse_feed(txt)
                            if items:
                                rec["feed_url"] = cand
                                rec["feed_items"] = items
                                break
                    except Exception:
                        continue
                page.close()
            except Exception as e:
                rec["error"] = str(e)[:160]

            out = os.path.join(OUT, f"{cid}-{ts}.json")
            tmp = out + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(rec, f, indent=2, ensure_ascii=False)
                f.flush(); os.fsync(f.fileno())
            os.replace(tmp, out)
            print(f"  {cid}: website {len(rec['website_text'])} chars | feed-items {len(rec['feed_items'])}")
        browser.close()
    print("content_scan klaar")


if __name__ == "__main__":
    main()
