#!/usr/bin/env python3.12
"""strategy_synth.py — Optie 2 stap 3: van content_analysis -> per-concurrent dossier.

Genereert content_raw/strategy/<id>.md met: ritme, formaten, tone-of-voice,
thema-rotatie, visuele signalen, whitespace voor Powerland. Puur uit data.json
content_analysis (geen verzinning). Schrijft ook een korte samenvatting terug naar
data.json content_strategy (voor dashboard).
"""
import os, sys, json
from collections import Counter

PUBLISH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PUBLISH, "data.json")
SD = os.path.join(PUBLISH, "content_raw", "strategy")

WHITESPACE_HINTS = {
    "prijs/aanbod": "Concurrent speelt openlijk op prijs/acties — Powerland kan differentiëren op waarde/zonder kortingswedloop.",
    "duurzaamheid": "Duurzaamheid centraal — Powerland moet scherper op concrete CO2-impact of lokale verankering.",
    "klantverhaal": "Werkt met klantcases — Powerland kan eigen referenties zichtbaarder maken.",
    "techniek": "Technisch/productspecifiek — Powerland kan op toegankelijkheid/begrijpelijkheid winnen.",
    "service": "Service/onderhoud als hoeksteen — Powerland kan proactief beheer-monitoring uitlichten.",
    "event": "Inzet op events — Powerland kan digitaal/webinar-spoor oppakken.",
}


def synth(c):
    ca = c.get("content_analysis", {})
    items = ca.get("items", [])
    themes = ca.get("themes", [])
    tone = ca.get("tone", "onbekend")
    cta = ca.get("cta_types", [])
    n = ca.get("n_items", 0)

    # theama-rotatie (frequentie per thema over items)
    tc = Counter(it.get("theme", "algemeen") for it in items)
    rotation = ", ".join(f"{th} ({cnt})" for th, cnt in tc.most_common())

    # whitespace: neem hint van het dominante thema (excl. algemeen)
    dom = next((t for t in themes if t in WHITESPACE_HINTS), None)
    whitespace = WHITESPACE_HINTS.get(dom, "Zie concurrent-specifieke thema's hierboven.")

    md = f"""# Contentstrategie — {c['name']}

> Gegenereerd uit website-analyse (Optie 2: geen socials, geen login). Bron: {c.get('domain','')}

## 1. Overzicht
- Aantal geanalyseerde content-items: **{n}**
- Belangrijkste thema's: **{', '.join(themes) if themes else 'geen duidelijk patroon'}**
- Tone-of-voice: **{tone}**
- Call-to-action-stijl: **{', '.join(cta) if cta else 'geen expliciete CTA'}**

## 2. Thema-rotatie
{tc.most_common(6) and chr(10).join(f"- {th}: {cnt} items" for th, cnt in tc.most_common(6)) or "- geen items"}

## 3. Tone-of-voice
{tone}. {('De concurrent spreekt eerder de lezer direct aan (je/jij/ons).' if 'familiaar' in tone else 'De toon is zakelijk/formeel.')}

## 4. Call-to-action-patronen
{chr(10).join(f'- {x}' for x in cta) if cta else '- Geen consistente CTA gevonden in de geanalyseerde tekst.'}

## 5. Visuele signalen
- Emoji-gebruik in tekst: {'ja' if any(it.get('emoji_count',0)>0 for it in items) else 'nee/minimaal'}
- Opvallend: website-gedreven content, geen socials- of image-diepte beschikbaar in deze (login-vrije) capture.

## 6. Whitespace voor Powerland
{whitespace}

## 7. Aanbeveling
Focus Powerland op het gat bij '{dom or 'de dominante thema'}' door het scherper / anders in te vullen dan {c['name']}.
"""
    return md, {
        "n_items": n, "themes": themes, "tone": tone, "cta_types": cta,
        "rotation": rotation, "whitespace": whitespace,
    }


def main():
    d = json.load(open(DATA, encoding="utf-8"))
    os.makedirs(SD, exist_ok=True)
    for c in d["competitors"]:
        md, summary = synth(c)
        with open(os.path.join(SD, f"{c['id']}.md"), "w", encoding="utf-8") as f:
            f.write(md)
        c["content_strategy"] = summary
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, DATA)
    print(f"{len(d['competitors'])} strategie-dossiers geschreven naar content_raw/strategy/")


if __name__ == "__main__":
    main()
