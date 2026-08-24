# test_strategy_synth.py — strategy_synth moet per concurrent een dossier schrijven
import os, sys, subprocess, json, glob
BASE = r"C:/Users/camil.sahnoune/competitive-intel/publish"
sys.path.insert(0, BASE)

# 1. run
r = subprocess.run(["python", "scripts/strategy_synth.py"], cwd=BASE, capture_output=True, text=True)
assert r.returncode == 0, f"strategy_synth faalde: {r.stderr[:300]}"

# 2. per concurrent een .md met >=5 secties
d = json.load(open(os.path.join(BASE, "data.json"), encoding="utf-8"))
SD = os.path.join(BASE, "content_raw", "strategy")
for c in d["competitors"]:
    p = os.path.join(SD, f"{c['id']}.md")
    assert os.path.isfile(p), f"geen strategie-dossier voor {c['id']}"
    body = open(p, encoding="utf-8").read()
    sects = body.count("##")
    assert sects >= 5, f"{c['id']}: slechts {sects} secties (<5)"

print(f"OK: {len(d['competitors'])} strategie-dossiers geschreven, >=5 secties elk")
