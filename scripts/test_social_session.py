# test_social_session.py — sessie-scraper moet posts opleveren uit het Firefox-profile
import os, sys, subprocess, json, glob
BASE = r"C:/Users/camil.sahnoune/competitive-intel/publish"
sys.path.insert(0, BASE)
from scripts.social_session_scrape import scrape_concurrent  # importeerbaar = bestaat

# draai op 1 test-concurrent (reeload) — heeft FB/IG/LinkedIn in channels
r = subprocess.run(["python", "scripts/social_session_scrape.py", "--cid", "reeload"],
                   cwd=BASE, capture_output=True, text=True)
assert r.returncode == 0, f"scraper faalde: {r.stderr[:300]}"

# er moet een captures/social/reeload-<ts>.json liggen met >=1 post
files = sorted(glob.glob(os.path.join(BASE, "captures", "social", "reeload-*.json")))
assert files, "geen capture-bestand voor reeload"
obj = json.load(open(files[-1], encoding="utf-8"))
posts = obj.get("posts", [])
assert len(posts) >= 1, f"geen posts gevonden (profile waarschijnlijk leeg): {obj.get('note','')}"
# elke post minstens caption of tekst
for p in posts:
    assert p.get("caption") or p.get("text"), "post zonder caption/tekst"
print(f"OK: {len(posts)} social-posts gescraped voor reeload (permanent gratis via sessie)")
