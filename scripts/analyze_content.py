#!/usr/bin/env python3.12
"""analyze_content.py — Optie 2 stap 2: ontleed content_raw tot diepte-velden.

Splitst website-text in items (secties/paragrafen) en analyseert elk op:
hook, length, emoji, cta, theme, tone, format. Schrijft naar data.json
content_analysis. Merge met bestaande post_analysis (overschrijft niet).

Geen socials hier (Optie 1). Geen vision (markeer enkel image-signaal indien aanwezig).
"""
import os, sys, json, re
from collections import Counter

PUBLISH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PUBLISH, "data.json")
CR = os.path.join(PUBLISH, "content_raw")

THEMES = {
    "prijs/aanbod": ["korting", "actie", "%", "voordeel", "gratis", "tarief", "prijs", "offerte"],
    "duurzaamheid": ["duurzaam", "groen", "co2", "ecologisch", "klimaat", "zonne", "milieu", "energie"],
    "klantverhaal": ["klant", "case", "project", "realisatie", "ervaring", "tevreden", "review", "referentie"],
    "techniek": ["laadpaal", "ev-", "batterij", "omvormer", "installatie", "technisch", "capaciteit", "kwh", "laden", "zonnepaneel"],
    "service": ["onderhoud", "support", "service", "garantie", "helpdesk", "beheer", "monitoring"],
    "event": ["event", "beurs", "seminar", "webinar", "open dag", "workshop"],
}
CTA_WORDS = ["contacteer", "vraag", "offerte", "bel", "mail", "ontdek", "bekijk", "meer info",
             "schrijf", "plan", "afspraak", "nu", "vraag hier", "download"]
EMOJI_RE = re.compile(r"[\U0001F000-\U0001FAFF\U00002600-\U000027BF]")


def split_items(text):
    """Split website-text in items op zin/regel-grenzen, filter kort/ruis."""
    RUIS = ["cookie", "privacy", "accepteer", "we gebruiken", "menu", "search",
            "nieuwsbrief", "schakel", "skip", "toegankelijk", "overslaan", "naar de inhoud",
            "surfgedrag", "gegevens", "partners voor social", "main navigation",
            "home", "over ons", "vacatures", "blog", "contact", "découvrez nos offres",
            "notre famille", "totaaloplossingen", "download de app", "scan om", "eerste maand",
            "gratis met code", "our locations may be", "busier during", "holidays"]
    parts = re.split(r"(?<=[.!?])\s+|\n", text)
    out, seen = [], set()
    for p in parts:
        p = re.sub(r"\s+", " ", p).strip()
        if len(p) < 40 or len(p) > 400:
            continue
        pl = p.lower()
        # normaliseer accents/quotes zodat ruis-matches robuust zijn
        pln = pl.replace("’", "'").replace("'", "'")
        # exacte ruis-zinnen (navigatie/vacatures/cookies) altijd blokkeren
        EXACT_RUIS = ["decouvrez nos offres", "notre grande famille", "totaaloplossingen",
                      "overslaan en naar de inhoud", "main navigation", "surfgedrag",
                      "partners pour", "our locations may be busier"]
        if any(r in pln for r in EXACT_RUIS):
            continue
        hits = sum(1 for r in RUIS if r in pln)
        if hits >= 2:
            continue
        if any(pl.startswith(n) for n in ["home", "over ons", "contact", "blog", "vacatures", "menu"]):
            continue
        if pl in seen:
            continue
        seen.add(pl)
        out.append(p)
    return out[:40]


def detect_themes(items):
    cnt = Counter()
    for t in items:
        tl = t.lower()
        for th, words in THEMES.items():
            if any(w in tl for w in words):
                cnt[th] += 1
    return [th for th, _ in cnt.most_common(3)]


def detect_tone(items):
    fam = sum(len(re.findall(r"\b(je|jij|wij|ons|jullie)\b", t.lower())) for t in items)
    form = sum(len(re.findall(r"\b(klant|onderneming|de klant|uw|bedrijf)\b", t.lower())) for t in items)
    total = fam + form
    if total == 0:
        return "neutraal"
    pct = round(100 * fam / total)
    return f"{pct}% familiaar" if pct >= 50 else f"{100 - pct}% formeel"


def detect_cta(items):
    out = []
    for t in items:
        if any(w in t.lower() for w in CTA_WORDS):
            out.append("vraag/contact" if any(x in t.lower() for x in ["contacteer", "vraag", "offerte", "bel", "mail", "afspraak"]) else "ontdek/bekijk")
    return list(dict.fromkeys(out))[:3]


def main():
    d = json.load(open(DATA, encoding="utf-8"))
    for c in d["competitors"]:
        cid = c["id"]
        files = sorted([f for f in os.listdir(CR) if f.startswith(cid) and f.endswith(".json")]) if os.path.isdir(CR) else []
        if not files:
            c["content_analysis"] = {"items": [], "themes": [], "tone": "onbekend", "formats": [], "cta_types": [], "n_items": 0}
            continue
        rec = json.load(open(os.path.join(CR, files[-1]), encoding="utf-8"))
        items_text = split_items(rec.get("website_text", ""))
        full = " ".join(items_text)
        items = []
        for t in items_text:
            emojis = EMOJI_RE.findall(t)
            items.append({
                "text": t,
                "length": len(t.split()),
                "hook": t[:60],
                "emoji_count": len(emojis),
                "cta": "ja" if any(w in t.lower() for w in CTA_WORDS) else "nee",
                "theme": next((th for th, words in THEMES.items() if any(w in t.lower() for w in words)), "algemeen"),
            })
        analysis = {
            "items": items,
            "themes": detect_themes(items_text),
            "tone": detect_tone(items_text),
            "formats": ["website-tekst"],
            "cta_types": detect_cta(items_text),
            "n_items": len(items),
            "source": "website" if not rec.get("feed_items") else "website+feed",
        }
        c["content_analysis"] = analysis
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, DATA)
    print(f"content_analysis bijgewerkt voor {len(d['competitors'])} concurrenten")


if __name__ == "__main__":
    main()
