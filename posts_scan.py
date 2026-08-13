#!/usr/bin/env python3.12
# posts_scan.py — FASE 2 stap 1: haal laatste berichten per concurrent per kanaal.
# Gratis (Playwright). Leest channels.json, schrijft posts_raw.json.
# Geblokkeerde kanalen (403/timeout) -> "niet beschikbaar", niet liegen.
import os, json, re, html, datetime
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

VENV = r"C:/Users/camil.sahnoune/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
PUBLISH = r"C:/Users/camil.sahnoune/competitive-intel/publish"
CH = os.path.join(PUBLISH, "channels.json")
OUT = os.path.join(PUBLISH, "posts_raw.json")
MAX_POSTS = 10

def clean(s):
    return re.sub(r"\s+", " ", html.unescape(s or "")).strip()

def extract_blocks(browser, url, wait=3000):
    """Haal zichtbare tekstblokken (>= 30 tekens) van een pagina."""
    try:
        page = browser.new_page()
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(wait)
        txt = clean(page.inner_text("body"))[:9000]
        page.close()
    except Exception as e:
        return None, str(e)
    # splits in zinnen/regels, filter korte
    parts = [clean(p) for p in re.split(r"(?<=[.!?])\s+|\n", txt)]
    posts = [p for p in parts if 30 <= len(p) <= 300]
    seen, out = set(), []
    for p in posts:
        if p.lower() not in seen:
            seen.add(p.lower())
            out.append(p)
        if len(out) >= MAX_POSTS:
            break
    return out, None

def main():
    ch = json.load(open(CH, encoding="utf-8"))
    result = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for cid, block in ch.items():
            print(f"  scan posts {cid}...")
            channels = block.get("channels", {})
            posts = []
            for plat, urls in channels.items():
                url = urls[0] if urls else None
                if not url:
                    continue
                out, err = extract_blocks(browser, url)
                if err:
                    posts.append({"kanaal": plat, "status": "niet beschikbaar", "reden": err[:80]})
                    continue
                if not out:
                    posts.append({"kanaal": plat, "status": "geen berichten gevonden"})
                    continue
                for t in out:
                    posts.append({"kanaal": plat, "tekst": t, "type": "tekst"})
            result[cid] = {"website": block.get("website"), "posts": posts}
        browser.close()
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT)
    print(f"posts_raw.json geschreven: {len(result)} concurrent(en)")

if __name__ == "__main__":
    main()
