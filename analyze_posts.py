#!/usr/bin/env python3.12
# analyze_posts.py — FASE 2 stap 2: ontleed posts_raw.json op 4 assen.
# Thema's, toon, aanbiedingen, frequentie. Filtert ruis (cookie/login).
# Schrijft naar data.json per concurrent: posts + post_analysis.
import os, json, re
from collections import Counter
from datetime import datetime

PUBLISH = r"C:/Users/camil.sahnoune/competitive-intel/publish"
RAW = os.path.join(PUBLISH, "posts_raw.json")
DATA = os.path.join(PUBLISH, "data.json")

# ruis die geen echt bericht is
RUIS = ["respects your privacy", "cookie policy", "e-mailadres of telefoon",
        "nieuwe account aanmaken", "het gebruik van cookies", "alle reacties:",
        "vind ik leuk", "meer opmerkingen", "meer weergeven van",
        "download the", "top-notch", "searching for a",
        "select accept to consent", "reject to decline", "skip to main content",
        "linkedin top content", "we gebruiken cookies", "veiligere ervaring",
        "update your choices", "accept reject", "meta-produ", "sign in",
        "log in", "aanmelden", "wachtwoord"]

# thema-trefwoorden
THEMES = {
    "prijs/aanbod": ["korting", "actie", "%", "voordeel", "gratis", "tarief", "prijs"],
    "duurzaamheid": ["duurzaam", "groen", "co2", "ecologisch", "klimaat", "zonne", "milieu"],
    "klantverhaal": ["klant", "case", "project", "realisatie", "ervaring", "tevreden", "feedb", "review"],
    "techniek": ["laadpaal", "ev-", "batterij", "omvormer", "installatie", "technisch", "capaciteit", "kwh", "laden"],
    "service": ["onderhoud", "support", "service", "garantie", "helpdesk", "beheer"],
    "event": ["event", "beurs", "seminar", "webinar", "open dag", "workshop"],
}
OFFER_WORDS = ["korting", "actie", "%", "gratis", "voordeel", "aanbieding", "promo"]

def is_ruis(t):
    tl = t.lower()
    return any(r in tl for r in RUIS) or len(t) < 35

def detect_themes(posts):
    cnt = Counter()
    for t in posts:
        tl = t.lower()
        for theme, words in THEMES.items():
            if any(w in tl for w in words):
                cnt[theme] += 1
    return [th for th, _ in cnt.most_common(3)]

def detect_tone(posts):
    # familiaar als 'je/jij/ons' veel voorkomt t.o.v. formeel 'klant/onderneming/de klant'
    fam = sum(len(re.findall(r"\b(je|jij|wij|ons|jullie)\b", t.lower())) for t in posts)
    form = sum(len(re.findall(r"\b(klant|onderneming|de klant|uw|bedrijf)\b", t.lower())) for t in posts)
    total = fam + form
    if total == 0:
        return "neutraal"
    pct = round(100 * fam / total)
    return f"{pct}% familiaar" if pct >= 50 else f"{100-pct}% formeel"

def detect_offers(posts):
    out = []
    for t in posts:
        if any(w in t.lower() for w in OFFER_WORDS):
            out.append(t[:80])
    return out[:5]

def detect_frequency(posts):
    # grove schatting: aantal berichten als proxy (geen datums beschikbaar uit scrape)
    n = len(posts)
    if n == 0:
        return "geen berichten"
    if n >= 20:
        return "zeer actief (20+ berichten gescand)"
    if n >= 10:
        return "actief (~10-20 berichten)"
    return f"beperkt actief ({n} berichten)"

def main():
    raw = json.load(open(RAW, encoding="utf-8"))
    d = json.load(open(DATA, encoding="utf-8"))
    for c in d["competitors"]:
        cid = c["id"]
        block = raw.get(cid, {})
        real_posts = [x["tekst"] for x in block.get("posts", []) if x.get("tekst") and not is_ruis(x["tekst"])]
        real_posts = real_posts[:30]  # cap voor performance, na ruis-filter
        analysis = {
            "themes": detect_themes(real_posts),
            "tone": detect_tone(real_posts),
            "offers": detect_offers(real_posts),
            "frequency": detect_frequency(real_posts),
            "scanned_channels": [x["kanaal"] for x in block.get("posts", [])],
            "n_real_posts": len(real_posts),
        }
        c["posts"] = [{"kanaal": "mix", "tekst": t} for t in real_posts]
        c["post_analysis"] = analysis
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, DATA)
    print(f"data.json post_analysis bijgewerkt voor {len(d['competitors'])} concurrenten")

if __name__ == "__main__":
    main()
