#!/usr/bin/env python3.12
# channel_scan.py — FASE 1: inventariseer alle kanaal-URLs per concurrent.
# Gratis (Playwright, geen API). Leest data.json, schrijft channels.json.
import sys, os, json, subprocess
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

VENV = r"C:/Users/camil.sahnoune/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
PUBLISH = r"C:/Users/camil.sahnoune/competitive-intel/publish"
OUT = os.path.join(PUBLISH, "channels.json")

# welke platformen herkennen we aan de host
PLATFORMS = {
    "facebook.com": "facebook", "fb.com": "facebook",
    "linkedin.com": "linkedin",
    "instagram.com": "instagram",
    "youtube.com": "youtube", "youtu.be": "youtube",
    "tiktok.com": "tiktok",
    "twitter.com": "twitter", "x.com": "twitter",
    "trustpilot.com": "trustpilot",
    "apps.apple.com": "appstore", "play.google.com": "playstore",
}

def classify(url):
    host = urlparse(url).netloc.lower().replace("www.", "")
    for key, name in PLATFORMS.items():
        if host == key or host.endswith("." + key):
            return name
    return None

def extract_links(browser, domain):
    found = {}  # platform -> set(urls)
    pages_to_try = [domain, domain.rstrip("/") + "/contact", domain.rstrip("/") + "/over-ons",
                    domain.rstrip("/") + "/nl/contact", domain.rstrip("/") + "/nl/over-ons"]
    seen_pages = set()
    for url in pages_to_try:
        if url in seen_pages:
            continue
        seen_pages.add(url)
        try:
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(2500)
            links = page.eval_on_selector_all(
                "a[href]", "els => els.map(e => e.href)")
            page.close()
        except Exception as e:
            print(f"    (pagina {url} mislukt: {e})")
            continue
        for href in links:
            try:
                u = urlparse(href)
            except Exception:
                continue
            if not u.scheme.startswith("http"):
                continue
            if u.netloc.lower().replace("www.", "") == urlparse(domain).netloc.lower().replace("www.", ""):
                continue  # interne link, overslaan
            plat = classify(href)
            if plat:
                found.setdefault(plat, set()).add(href.split("?")[0].rstrip("/"))
    return found

def main():
    with open(os.path.join(PUBLISH, "data.json"), encoding="utf-8") as f:
        data = json.load(f)
    result = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for c in data["competitors"]:
            cid = c["id"]
            domain = c.get("domain", "")
            if not domain:
                result[cid] = {"error": "geen domain in data.json"}
                continue
            print(f"  scan {cid} ({domain})...")
            try:
                links = extract_links(browser, domain)
            except Exception as e:
                result[cid] = {"error": str(e)}
                continue
            result[cid] = {
                "website": domain,
                "channels": {k: sorted(v) for k, v in links.items()},
            }
        browser.close()
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT)
    print(f"channels.json geschreven: {len(result)} concurrent(en)")

if __name__ == "__main__":
    main()
