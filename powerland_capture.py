#!/usr/bin/env python3.12
"""
powerland_capture.py — Niet-destructieve concurrentie-monitor (Powerland).

Wat het doet:
- Leest elke concurrent-site headless (Playwright) uit data.json.
- Schrijft een timestamped snapshot naar publish/snapshots/<id>/<YYYYMMDD-HHMM>.md.
- Difft tegen de vorige snapshot en rapporteert welke sites VERANDERDEN.
- Raakt data.json / raw/*.md NOOIT aan (geen "raden" — eerder gemelde garantie).

Bij een wijziging: het rapport zegt "curateer dit met de hand" — de agent toont
de diff en past pas na expliciete goedkeuring toe via refresh.py --one.

Selft-re-exec: als playwright niet importbaar is onder de scheduler z'n python,
herstart het zichzelf onder de Hermes-venv.

Niet afhankelijk van hermes cron (geen agent-hang). Draait via Windows Taakplanner
(MAANDAG 06:00) of manueel: python powerland_capture.py
"""
import sys, os, subprocess, json, re, html, datetime

VENV = r"C:/Users/camil.sahnoune/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
PUBLISH = os.path.dirname(os.path.abspath(__file__))

# --- self re-exec onder venv als playwright ontbreekt ---
try:
    import playwright  # noqa
except ImportError:
    if os.path.exists(VENV):
        subprocess.run([VENV, os.path.abspath(__file__)], check=True)
        sys.exit(0)
    raise

from playwright.sync_api import sync_playwright

DATA = os.path.join(PUBLISH, "data.json")
SNAP_DIR = os.path.join(PUBLISH, "snapshots")
REPORT = os.path.join(PUBLISH, "capture-report.txt")


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(s or "")).strip()


def extract(doc):
    """Haal title + meta-description + body-text uit een gerenderde pagina."""
    title = ""
    desc = ""
    body = ""
    try:
        title = clean(doc.query_selector("title").inner_text()) if doc.query_selector("title") else ""
    except Exception:
        pass
    try:
        m = doc.query_selector('meta[name="description"]')
        if m:
            desc = clean(m.get_attribute("content"))
    except Exception:
        pass
    try:
        body = clean(doc.inner_text("body"))[:6000]
    except Exception:
        pass
    return title, desc, body


def latest_snapshot(cid):
    d = os.path.join(SNAP_DIR, cid)
    if not os.path.isdir(d):
        return None
    files = [f for f in os.listdir(d) if f.endswith(".md") and f != "LATEST.md"]
    if not files:
        return None
    files.sort()
    return os.path.join(d, files[-1])


def main():
    d = json.load(open(DATA, encoding="utf-8"))
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    changed, failed = [], []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for c in d["competitors"]:
            cid = c["id"]
            domain = c.get("domain")
            if not domain:
                failed.append((cid, "geen domain in data.json"))
                continue
            try:
                page = browser.new_page()
                page.goto(domain, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(2500)
                title, desc, body = extract(page)
                page.close()
            except Exception as e:
                failed.append((cid, str(e)[:120]))
                continue

            text = f"# {c['name']} — snapshot {ts}\n\n**Domein:** {domain}\n**Titel:** {title}\n**Beschrijving:** {desc}\n\n## Body (eerste 6000 tekens)\n\n{body}\n"
            out_dir = os.path.join(SNAP_DIR, cid)
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"{ts}.md")
            tmp = out_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(text)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, out_path)
            # LATEST.md bijhouden (voor snelle diff)
            with open(os.path.join(out_dir, "LATEST.md"), "w", encoding="utf-8") as f:
                f.write(text)

            prev = latest_snapshot_before(out_dir, out_path)
            if prev:
                old = open(prev, encoding="utf-8").read()
                if _body_changed(old, text):
                    changed.append(cid)
        browser.close()

    lines = [f"# Capture-report — {now}", "",
             f"Totaal: {len(d['competitors'])} | veranderd: {len(changed)} | gefaald: {len(failed)}", ""]
    if changed:
        lines.append("**Veranderd (curateer met de hand via refresh.py --one):**")
        for cid in changed:
            lines.append(f"- {cid}")
        lines.append("")
    if failed:
        lines.append("**Gefaald:**")
        for cid, err in failed:
            lines.append(f"- {cid}: {err}")
        lines.append("")
    if not changed and not failed:
        lines.append("Geen wijzigingen vastgesteld t.o.v. vorige snapshots. Alle sites gelijk.")
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Totaal: {len(d['competitors'])} | veranderd: {len(changed)} | gefaald: {len(failed)}")
    for cid in changed:
        print(f"  VERANDERD: {cid}")
    for cid, err in failed:
        print(f"  GEFAALD:  {cid} ({err})")


def latest_snapshot_before(out_dir, current_path):
    files = [os.path.join(out_dir, f) for f in os.listdir(out_dir)
             if f.endswith(".md") and f != "LATEST.md" and os.path.join(out_dir, f) != current_path]
    if not files:
        return None
    files.sort()
    return files[-1]


def _body_changed(old, new):
    # vergelijk enkel de body-sectie (overslaan van timestamp in header)
    def body_of(t):
        return t.split("## Body", 1)[-1] if "## Body" in t else t
    return body_of(old).strip() != body_of(new).strip()


if __name__ == "__main__":
    main()
