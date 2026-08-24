# test_analyze_content.py — analyze_content moet per concurrent diepte-velden opleveren
import os, sys, subprocess, json, glob
BASE = r"C:/Users/camil.sahnoune/competitive-intel/publish"
sys.path.insert(0, BASE)

# 1. run de analyse
r = subprocess.run(["python", "scripts/analyze_content.py"], cwd=BASE, capture_output=True, text=True)
assert r.returncode == 0, f"analyze_content faalde: {r.stderr[:300]}"

# 2. per concurrent: content_analysis in data.json met diepte-velden
d = json.load(open(os.path.join(BASE, "data.json"), encoding="utf-8"))
REQUIRED = ["items", "themes", "tone", "formats", "cta_types"]
for c in d["competitors"]:
    ca = c.get("content_analysis")
    assert ca, f"{c['id']}: geen content_analysis"
    for k in REQUIRED:
        assert k in ca, f"{c['id']}: ontbrekend veld {k}"
    # items moeten diepte-velden hebben + GEEN cookie/menu-ruis
    RUIS_CHECK = ["cookie", "surfgedrag", "overslaan en naar", "main navigation",
                  "totaaloplossingen", "decouvrez nos offres", "our locations may be",
                  "emploi", "agrandir notre"]
    assert len(ca["items"]) > 0, f"{c['id']}: geen items"
    for it in ca["items"][:5]:
        for fld in ("text", "length", "hook", "cta", "theme"):
            assert fld in it, f"{c['id']}: item mist {fld}"
        il = it["text"].lower()
        assert not any(r in il for r in RUIS_CHECK), f"{c['id']}: item bevat ruis: {it['text'][:50]}"

print(f"OK: {len(d['competitors'])} concurrenten geanalyseerd, diepte-velden aanwezig")
