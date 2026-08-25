#!/usr/bin/env python3.12
"""social_api.py — Fase 5.1 POC: ScrapeCreators wrapper (GRATIS 100-credit tier).

Leest SCRAPECREATORS_API_KEY uit env. Roept de posts-endpoints per platform
en schrijft atomic JSON naar captures/social/<id>/<ts>.json.

Data-shape per post (exact wat de user vraagt, volgens competitor-social-research skill):
  caption, posted_at, metrics {likes,comments,shares}, images[], url, platform

GEEN key nodig om dit bestand te importeren — fetch() faalt netjes zonder key
(zodat test_scrape_poc.py in de TDD-cyclus FAIL zonder key, PASS ermee).
"""
import os, sys, json, time, datetime
try:
    import requests
except ImportError:
    requests = None

BASE = os.path.dirname(os.path.abspath(__file__))
PUBLISH = os.path.dirname(BASE)
OUT = os.path.join(PUBLISH, "captures", "social")

ENDPOINTS = {
    "linkedin":  "/v1/linkedin/company/posts",
    "instagram": "/v1/instagram/user/posts",
    "facebook":  "/v1/facebook/profile/posts",
}

def _ts():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M")

def fetch(cid, platform, limit=12):
    """Haal posts voor <cid> op <platform>. Returneert lijst van post-dicts.
    Faalt met RuntimeError zonder key of bij HTTP-fout."""
    key = os.environ.get("SCRAPECREATORS_API_KEY")
    if not key:
        raise RuntimeError("SCRAPECREATORS_API_KEY niet gezet")
    if requests is None:
        raise RuntimeError("requests niet geinstalleerd in venv")
    if platform not in ENDPOINTS:
        raise ValueError(f"onbekend platform: {platform}")
    # username/handle uit data.json halen indien beschikbaar
    handle = cid
    try:
        d = json.load(open(os.path.join(PUBLISH, "data.json"), encoding="utf-8"))
        for c in d.get("competitors", []):
            if c.get("id") == cid:
                sc = c.get("social_channels", {})
                if platform in sc and isinstance(sc[platform], dict):
                    handle = sc[platform].get("url") or cid
    except Exception:
        pass
    url = f"https://api.scrapecreators.com{ENDPOINTS[platform]}"
    params = {"url": handle, "limit": limit} if platform != "linkedin" else {"username": handle, "limit": limit}
    r = requests.get(url, headers={"x-api-key": key}, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    posts = data.get("posts", data) if isinstance(data, dict) else data
    out = []
    for p in posts[:limit]:
        out.append({
            "platform": platform,
            "caption": (p.get("caption") or p.get("text") or "").strip(),
            "posted_at": p.get("posted_at") or p.get("timestamp") or p.get("date"),
            "metrics": {
                "likes": p.get("likes") or p.get("like_count"),
                "comments": p.get("comments") or p.get("comment_count"),
                "shares": p.get("shares") or p.get("share_count"),
            },
            "images": p.get("images", []) or [],
            "url": p.get("url") or p.get("post_url"),
        })
    # atomic write
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{cid}-{platform}-{_ts()}.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"cid": cid, "platform": platform, "posts": out}, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)
    return out

if __name__ == "__main__":
    cid = sys.argv[1] if len(sys.argv) > 1 else "reeload"
    plat = sys.argv[2] if len(sys.argv) > 2 else "linkedin"
    try:
        res = fetch(cid, plat)
        print(f"{len(res)} posts geschreven voor {cid}/{plat}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
