# test_content_scan.py — content_scan moet per concurrent website-text + feed opleveren (zonder sessie)
import os, sys, subprocess, json
BASE = r"C:/Users/camil.sahnoune/competitive-intel/publish"
sys.path.insert(0, BASE)

# 1. run de scan
r = subprocess.run(["python", "scripts/content_scan.py"], cwd=BASE, capture_output=True, text=True)
assert r.returncode == 0, f"content_scan faalde: {r.stderr[:300]}"

# 2. output-map bestaat met per-concurrent JSON
cr = os.path.join(BASE, "content_raw")
assert os.path.isdir(cr), "content_raw/ map ontbreekt"

d = json.load(open(os.path.join(BASE, "data.json"), encoding="utf-8"))
for c in d["competitors"]:
    cid = c["id"]
    files = [f for f in os.listdir(cr) if f.startswith(cid) and f.endswith(".json")] if os.path.isdir(cr) else []
    assert files, f"geen content_raw voor {cid}"
    latest = sorted(files)[-1]
    obj = json.load(open(os.path.join(cr, latest), encoding="utf-8"))
    # website_text moet er zijn (publieke site, geen sessie)
    assert len(obj.get("website_text", "")) >= 200, f"{cid}: website_text te kort/leeg"
    # feed_items mag leeg zijn, maar moet een lijst zijn; feed_url mag None of URL
    assert isinstance(obj.get("feed_items", []), list), f"{cid}: feed_items geen lijst"
    fu = obj.get("feed_url")
    assert fu is None or fu.startswith("http"), f"{cid}: feed_url ongeldig: {fu}"

print(f"OK: {len(d['competitors'])} concurrenten gescand, website-text + feed structuur aanwezig")
