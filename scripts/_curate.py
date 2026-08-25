#!/usr/bin/env python3.12
"""T2.3 curatie: werk de feitelijke stations-tellers bij obv de 2026-08-25 snapshots.
Functioneel equivalent aan `refresh.py --one <id> --facts ...`, maar zonder
shell-quoting-ellende (de ronde haken in de services-tekst breken cmd.exe).
Doet ENKEL de feitelijke FACT_FIELDS-update, geen interpretatie."""
import json, os, datetime
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data.json")
REPORT = os.path.join(BASE, "refresh-report.md")

UPDATES = {
    "electra": {"services": [
        "Laadnetwerk-operator (774 stations beschikbaar, 64 in aanbouw)",
        "Electra-laadpas", "Electra+ abonnement",
        "App (routeplanner, Autocharge)", "Voor professionals (fleet / host een station)"]},
    "ionity": {"services": [
        "Europees snellaadnetwerk (887 locaties, 24 landen, 74 in aanbouw)",
        "Abonnementen IONITY Power 365 / Motion 365", "IONITY App",
        "IONITY Direct", "Partner program / Fleets"]},
}

d = json.load(open(DATA, encoding="utf-8"))
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
entries = []
for c in d["competitors"]:
    if c["id"] in UPDATES:
        changed = {}
        for field, new in UPDATES[c["id"]].items():
            old = c.get(field)
            if old != new:
                changed[field] = (old, new)
                c[field] = new
        if changed:
            c["_refreshed_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            entries.append({"id": c["id"], "name": c["name"], "changed": changed})
            print(f"[{c['id']}] {len(changed)} veld bijgewerkt: {', '.join(changed)}")

json.dump(d, open(DATA, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

out = [f"# Refresh-report — {now}", "", f"{len(entries)} concurrent(en) ververst (T2.3 curatie).", ""]
if not entries:
    out.append("Geen wijzigingen.")
for e in entries:
    out.append(f"## {e['name']} (`{e['id']}`)")
    for field, (old, new) in e["changed"].items():
        out.append(f"- **{field}**: `{old}` → `{new}`")
    out.append("")
open(REPORT, "w", encoding="utf-8").write("\n".join(out))
print("Rapport geschreven:", len(entries), "concurrent(en) met wijziging,", len(d["competitors"]), "totaal.")
