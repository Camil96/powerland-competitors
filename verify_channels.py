#!/usr/bin/env python3.12
# verify_channels.py — FASE 1 stap 2: filter ruis + controleer elke URL op 200.
import json, os, urllib.request, ssl
from urllib.parse import urlparse

PUBLISH = r"C:/Users/camil.sahnoune/competitive-intel/publish"
C = json.load(open(os.path.join(PUBLISH, "channels.json"), encoding="utf-8"))
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE

# ruis-patronen die geen echte bedrijfspagina zijn
RUIS = ["/legal/", "/policy", "/privacy", "/terms", "/help", "/login", "/settings"]

def is_ruis(u):
    path = urlparse(u).path.lower()
    return any(r in path for r in RUIS)

def clean_link(u):
    # strip /about, query, trailing slash voor een nette bedrijf-URL
    p = urlparse(u)
    path = p.path.split("/about")[0].rstrip("/")
    return f"{p.scheme}://{p.netloc}{path}" if path else u

problems = []
cleaned = {}
for cid, block in C.items():
    ch = block.get("channels", {})
    newch = {}
    for plat, urls in ch.items():
        kept = []
        for u in urls:
            if is_ruis(u):
                print(f"  [ruis verwijderd] {cid}/{plat}: {u}")
                continue
            cu = clean_link(u)
            # verificatie
            try:
                req = urllib.request.Request(cu, method="HEAD",
                                             headers={"User-Agent": "Mozilla/5.0"})
                r = urllib.request.urlopen(req, timeout=15, context=ctx)
                if r.status >= 400:
                    problems.append(f"{cid}/{plat}: {cu} -> HTTP {r.status}")
            except Exception as e:
                # 403 = bot-wall, niet per se dood; markeer als twijfel
                msg = str(e)
                if "403" in msg or "Forbidden" in msg:
                    print(f"  [bot-wall 403, waarschijnlijk OK] {cid}/{plat}: {cu}")
                else:
                    problems.append(f"{cid}/{plat}: {cu} -> {msg}")
            kept.append(cu)
        if kept:
            newch[plat] = sorted(set(kept))
    cleaned[cid] = {"website": block.get("website"), "channels": newch}

# schrijf terug (atomic)
OUT = os.path.join(PUBLISH, "channels.json")
tmp = OUT + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2, ensure_ascii=False)
    f.flush(); os.fsync(f.fileno())
os.replace(tmp, OUT)

print("\nPROBLEMEN (echte dode links):" if problems else "\nGEEN ECHTE DODE LINKS")
for p in problems:
    print("  ", p)
print(f"\nchannels.json bijgewerkt: {len(cleaned)} concurrent(en), ruis gefilterd.")
