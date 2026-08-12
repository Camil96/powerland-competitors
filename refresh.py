#!/usr/bin/env python3.12
"""
refresh.py — Concurrentie-dashboard ververser (Powerland / Vandotec).

Senior-engineer ontwerp:
- Leest de concurrent-lijst uit data.json (enige bron van waarheid).
- Ververst per concurrent de FEITELIJKE velden (diensten, kanalen, doelgroep,
  positionering, social_channels) door de site opnieuw te lezen.
- Doe een DIFF: enkel gewijzigde velden worden gelogd + in data.json geschreven.
- Schrijft altijd een refresh-report.md met wat er veranderde.
- INTERPRETATIEVE velden (zwaktes, overlap_score, whitespace, pillars, recommendation)
  worden NOOIT automatisch aangepast — dat blijft strategisch oordeel van de mens.

Deze file is de ORCHESTRATOR. De effectieve site-lezing gebeurt door de agent
(browser tool) omdat B2B-sites JS-heavy zijn en bot-walls hebben bij zoekmachines.
De agent roept per concurrent:
    python refresh.py --one <id> --facts '<json>'
waarbij <json> de vers geziene feitelijke velden bevat. refresh.py doet de diff
tegen data.json, schrijft raw/<brand>/<id>.md bij, en update data.json + report.

Gebruik:
    python refresh.py --one reeload --facts '{"services":[...],"positioning":"...","social_channels":{"website":true}}'
    python refresh.py --report          # toon enkel het huidige refresh-report
    python refresh.py --list            # toon concurrenten + laatste verversing
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data.json")
RAW = os.path.join(BASE, "raw")
REPORT = os.path.join(BASE, "refresh-report.md")

# Velden die automatisch ververst mogen worden (FEIT, geen interpretatie)
FACT_FIELDS = ["services", "target_audience", "social_channels", "positioning", "sectors", "domain"]


def load():
    try:
        with open(DATA, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[warn] data.json kon niet geladen worden: {e}", file=sys.stderr)
        sys.exit(1)


def _atomic_write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)  # atomair


def save(d):
    # serialiseer eerst in memory zodat een dump-fout geen half bestand schrijft
    text = json.dumps(d, indent=2, ensure_ascii=False)
    _atomic_write(DATA, text)


def raw_path(competitor):
    brand = competitor.get("parent_brand", "powerland")
    # sanitize: geen subdir-traversal via parent_brand
    brand = os.path.basename(brand)
    pid = os.path.basename(str(competitor["id"]))
    return os.path.join(RAW, brand, f"{pid}.md")


def write_raw(competitor, facts, changed):
    p = raw_path(competitor)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# {competitor['name']} — concurrent van Powerland (BE)", ""]
    lines.append(f"**Domein:** {competitor.get('domain','')}  ")
    lines.append(f"**Laatst ververst:** {now}  ")
    lines.append(f"**Categorie:** {competitor.get('category','')}  ")
    lines.append("")
    lines.append("## Diensten")
    for s in facts.get("services", []):
        lines.append(f"- {s}")
    lines.append("")
    lines.append("## Doelgroep")
    for t in facts.get("target_audience", []):
        lines.append(f"- {t}")
    lines.append("")
    lines.append("## Kanalen / sociale aanwezigheid")
    for k, v in (facts.get("social_channels") or {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Positionering (citeerbaar uit site)")
    lines.append(f"> {facts.get('positioning','')}")
    lines.append("")
    if changed:
        lines.append("## Wat veranderde t.o.v. vorige verversing")
        for field, (old, new) in changed.items():
            lines.append(f"- **{field}**: `{old}` → `{new}`")
        lines.append("")
    _atomic_write(p, "\n".join(lines))


def render_report(d, entries):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = [f"# Refresh-report — {now}", "",
           f"{len(entries)} concurrent(en) ververst.", ""]
    if not entries:
        out.append("Geen wijzigingen vastgesteld. Alle feitelijke velden overeenkomstig de site.")
    for e in entries:
        out.append(f"## {e['name']} (`{e['id']}`)")
        if e["changed"]:
            for field, (old, new) in e["changed"].items():
                out.append(f"- **{field}**: `{old}` → `{new}`")
        else:
            out.append("- geen wijziging")
        out.append("")
    _atomic_write(REPORT, "\n".join(out))


def cmd_one(args):
    d = load()
    comp = next((c for c in d["competitors"] if c["id"] == args.one), None)
    if not comp:
        print(f"ERROR: geen concurrent met id '{args.one}'", file=sys.stderr)
        sys.exit(2)
    try:
        facts = json.loads(args.facts)
    except Exception as ex:
        print(f"ERROR: --facts is geen geldige JSON: {ex}", file=sys.stderr)
        sys.exit(2)

    changed = {}
    for field in FACT_FIELDS:
        if field not in facts:
            continue
        old = comp.get(field)
        new = facts[field]
        if old != new:
            changed[field] = (old, new)
            comp[field] = new

    if changed:
        comp["_refreshed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        # houd de diff bij voor het sessie-rapport (--run-all)
        comp["_pending_changes"] = {k: [str(o), str(n)] for k, (o, n) in changed.items()}
        write_raw(comp, comp, changed)
        save(d)
        print(f"[{comp['id']}] {len(changed)} veld(en) bijgewerkt: {', '.join(changed)}")
    else:
        print(f"[{comp['id']}] geen wijziging t.o.v. data.json")
    return comp, changed


def cmd_run_all():
    """Schrijf één samenvattend rapport over de hele verversingssessie.

    Veronderstelt dat de agent per concurrent `refresh.py --one <id> --facts ...`
    aanriep; elke --one bewaarde zijn diff in `_pending_changes` in data.json.
    --run-all leest die diffs, rendert één rapport, en maakt `_pending_changes`
    daarna schoon zodat de volgende sessie weer leeg start.
    """
    d = load()
    entries = []
    touched = 0
    for c in d["competitors"]:
        pc = c.get("_pending_changes")
        if pc:
            # reconstrueer (old, new) tuples voor render_report
            changed = {k: (o, n) for k, (o, n) in pc.items()}
            entries.append({"id": c["id"], "name": c["name"], "changed": changed})
            touched += 1
            del c["_pending_changes"]
    render_report(d, entries)
    save(d)
    print(f"Rapport geschreven: {touched} concurrent(en) met wijziging, {len(d['competitors'])} totaal.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--one", help="ververs één concurrent op id")
    ap.add_argument("--facts", help="JSON met feitelijke velden gezien op de site")
    ap.add_argument("--list", action="store_true", help="toon concurrenten + laatste verversing")
    ap.add_argument("--report", action="store_true", help="toon refresh-report")
    ap.add_argument("--run-all", action="store_true",
                    help="schrijf één samenvattend rapport na een verversingssessie")
    args = ap.parse_args()

    if args.list:
        d = load()
        for c in d["competitors"]:
            print(f"{c['id']:12s} {c.get('category','?'):8s} laatst={c.get('_refreshed_at','nooit')}")
        return
    if args.report:
        if os.path.exists(REPORT):
            print(open(REPORT, encoding="utf-8").read())
        else:
            print("nog geen refresh-report")
        return
    if args.one:
        # --one schrijft GEEN rapport (zodat een volledige sessie niet overschreven
        # wordt); het rapport komt via --run-all aan het eind van de sessie.
        cmd_one(args)
        return
    if args.run_all:
        cmd_run_all()
        return
    ap.print_help()


if __name__ == "__main__":
    main()
