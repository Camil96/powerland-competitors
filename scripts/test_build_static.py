# test_build_static.py — statische build: bestanden bestaan + geen root-slash-links
import os, sys, subprocess
BASE = r"C:/Users/camil.sahnoune/competitive-intel/publish"
sys.path.insert(0, BASE)

# 1. run de build
r = subprocess.run(["python", "build_static.py"], cwd=BASE, capture_output=True, text=True)
assert r.returncode == 0, f"build faalde: {r.stderr}"

# 2. verwachte bestanden bestaan
import json
d = json.load(open(os.path.join(BASE, "data.json"), encoding="utf-8"))
expected = ["analyse.html"]
for c in d["competitors"]:
    expected.append(f"concurrent-{c['id']}.html")
    expected.append(f"dossier-{c['id']}.html")
    for ev in c.get("evidence", []) or []:
        if ev:
            sn = (ev.get("snapshot") or "").split("/")[-1].replace(".md", "")
            expected.append(f"evidence-{c['id']}-{sn}.html")

missing = [f for f in expected if not os.path.exists(os.path.join(BASE, f))]
assert not missing, f"ontbrekende bestanden: {missing}"

# 3. GEEN root-slash-links in de gegenereerde HTML (die breken op GitHub Pages subdirectory)
bad = []
for f in expected:
    body = open(os.path.join(BASE, f), encoding="utf-8").read()
    # een root-link is href="/... of src="/... (behalve externe)
    for m in __import__("re").finditer(r'(?:href|src)="(/[^"]*)"', body):
        bad.append((f, m.group(1)))
assert not bad, f"root-slash-links gevonden (breken live): {bad[:5]}"

print(f"OK: {len(expected)} bestanden gegenereerd, geen root-slash-links")
