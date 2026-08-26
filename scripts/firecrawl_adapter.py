#!/usr/bin/env python3.12
"""firecrawl_adapter.py — Fase 2 alternatief voor content_scan.py (keyless free tier).

Gebruikt Firecrawl's keyless free tier (geen API-key, geen account, rate-limited)
om concurrent-sites naar schone markdown te scrapen. Produceert dezelfde
output-shape als content_scan.py: content_raw/<id>/<ts>.json — zodat de rest
van de pipeline (run_monitor.ps1) ongewijzigd werkt.

KEYLESS: roept https://api.firecrawl.dev/v1/scrape ZONDER Authorization-header.
Werkt voor ~1000 credits/maand gratis. Rate-limited, dus niet voor mass-scrapes.

Gebruik: python firecrawl_adapter.py [--cid <id>]  (alle als geen cid)
"""
import os, sys, json, datetime, urllib.request, urllib.error

BASE = os.path.dirname(os.path.abspath(__file__))
PUBLISH = os.path.dirname(BASE)
OUT = os.path.join(PUBLISH, "content_raw")
DATA = os.path.join(PUBLISH, "data.json")

def _ts():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M")

def scrape(url):
    """Keyless Firecrawl scrape -> markdown string. Raist urllib (geen extra dep)."""
    req = urllib.request.Request(
        "https://api.firecrawl.dev/v1/scrape",
        data=json.dumps({"url": url, "formats": ["markdown"]}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            j = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:200]}"
    except Exception as e:
        return None, str(e)
    if not j.get("success"):
        return None, j.get("error", "unknown error")
    return j["data"].get("markdown", ""), None

def main():
    cid = sys.argv[sys.argv.index("--cid") + 1] if "--cid" in sys.argv else None
    d = json.load(open(DATA, encoding="utf-8"))
    targets = [c for c in d.get("competitors", []) if (cid is None or c.get("id") == cid)]
    os.makedirs(OUT, exist_ok=True)
    for c in targets:
        url = c.get("domain") or (c.get("social_channels", {}).get("website", {}) or {}).get("url")
        if not url:
            print(f"[{c['id']}] geen url, skip")
            continue
        md, err = scrape(url)
        if err:
            print(f"[{c['id']}] FAIL: {err}")
            continue
        path = os.path.join(OUT, f"{c['id']}-{_ts()}.json")
        json.dump({"id": c["id"], "url": url, "markdown": md, "source": "firecrawl-keyless"},
                  open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"[{c['id']}] OK: {len(md)} chars -> {path}")

if __name__ == "__main__":
    main()
