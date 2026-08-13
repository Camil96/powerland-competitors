#!/usr/bin/env python3.12
# apply_channels.py — FASE 1 stap 3: schrijf geverifieerde kanalen naar data.json social_channels.
import json, os
PUBLISH = r"C:/Users/camil.sahnoune/competitive-intel/publish"
C = json.load(open(os.path.join(PUBLISH, "channels.json"), encoding="utf-8"))
D = json.load(open(os.path.join(PUBLISH, "data.json"), encoding="utf-8"))
for c in D["competitors"]:
    cid = c["id"]
    ch = C.get(cid, {}).get("channels", {})
    out = {}
    if c.get("domain"):
        out["website"] = {"present": True, "url": c["domain"]}
    for plat, urls in ch.items():
        out[plat] = {"present": True, "url": urls[0]} if urls else {"present": False}
    c["social_channels"] = out
tmp = os.path.join(PUBLISH, "data.json.tmp")
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(D, f, indent=2, ensure_ascii=False)
    f.flush(); os.fsync(f.fileno())
os.replace(tmp, os.path.join(PUBLISH, "data.json"))
print("data.json social_channels bijgewerkt voor", len(D["competitors"]), "concurrenten")
