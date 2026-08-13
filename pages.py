#!/usr/bin/env python3.12
# pages.py — FASE 3: HTML-generatoren voor detail/analyse/evidence/dossier.
# Server-side rendering vanuit data.json. Geen nieuwe data nodig.
import os, json, html, re

PUBLISH = r"C:/Users/camil.sahnoune/competitive-intel/publish"
DATA = os.path.join(PUBLISH, "data.json")

def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)

def esc(s):
    return html.escape(str(s or ""))

def page(title, body):
    return f"""<!DOCTYPE html><html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — Powerland Concurrentie</title>
<link rel="icon" href="assets/favicon.png">
<style>
:root{{--pl-blue:#213e86;--pl-teal:#37b49e;--pl-teal-soft:#d7f0ec;--bg:#fafafa;--panel:#fff;--text:#212529;--muted:#7c7c7c;--line:#e3e8ef;--radius:18px}}
*{{box-sizing:border-box}}body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;background:var(--bg);color:var(--text);line-height:1.55}}
header{{background:#fff;border-bottom:1px solid var(--line);padding:14px 24px;display:flex;align-items:center;gap:14px}}
header img{{height:30px}}header .tag{{margin-left:auto;color:var(--pl-teal);font-weight:800}}
.wrap{{max-width:1000px;margin:0 auto;padding:28px 22px 60px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:22px 26px;margin:18px 0;box-shadow:0 4px 18px rgba(33,62,134,.06)}}
h1{{font-size:30px;margin:0 0 4px;color:var(--pl-blue)}}h2{{font-size:20px;margin:26px 0 10px;color:var(--pl-blue)}}
.factbadge{{display:inline-block;font-size:10px;font-weight:800;letter-spacing:.5px;color:#16483f;background:var(--pl-teal-soft);border-radius:6px;padding:2px 7px;margin-right:6px;vertical-align:middle}}
.row{{font-size:14px;margin:8px 0}}.row b{{color:var(--text)}}
a{{color:var(--pl-blue);text-decoration:none}}a:hover{{text-decoration:underline}}
.tags{{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}}.tag{{background:#f4f6f9;border:1px solid var(--line);border-radius:8px;padding:3px 10px;font-size:11.5px;color:var(--muted);font-weight:600}}
.bar{{width:120px;height:8px;background:var(--line);border-radius:99px;overflow:hidden;display:inline-block;vertical-align:middle}}
.bar i{{display:block;height:100%;background:var(--pl-teal)}}
.quote{{font-style:italic;border-left:3px solid var(--pl-teal);padding-left:12px;margin:10px 0;color:var(--text)}}
table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:13px}}
th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}}
th{{background:var(--pl-teal-soft);color:#16483f}}
.back{{display:inline-block;margin:14px 0;color:var(--pl-teal);font-weight:700}}
</style></head><body>
<header><img src="assets/logo.svg" alt="Powerland"><b>Concurrentie-Intelligentie</b><span class="tag">Fight the average.</span></header>
<div class="wrap">{body}</div></body></html>"""

def channel_links(c):
    out = []
    for k, v in (c.get("social_channels") or {}).items():
        if isinstance(v, dict) and v.get("url"):
            out.append(f'<a href="{esc(v["url"])}" target="_blank" rel="noopener">{esc(k)}</a>')
    return " · ".join(out) or "n.v.t."

def render_detail(c):
    pa = c.get("post_analysis") or {}
    weak = c.get("weaknesses") or ""
    bc = c.get("battlecard") or {}
    pct = int(c.get("overlap_score_powerland", 0) / 5 * 100)
    body = f"""
    <a class="back" href="/">← Terug naar overzicht</a>
    <h1>{esc(c['name'])}</h1>
    <div class="card">
      <div class="row"><b>Categorie:</b> {esc(c.get('category',''))}</div>
      <div class="row"><b>Overlap met Powerland:</b> <span class="bar"><i style="width:{pct}%"></i></span> {esc(c.get('overlap_score_powerland'))}/5</div>
      <div class="row"><b>Kanalen:</b> {channel_links(c)}</div>
      <div class="row"><b>Diensten:</b> {esc(', '.join(c.get('services',[])))}</div>
      <div class="row"><b>Doelgroep:</b> {esc(', '.join(c.get('target_audience',[])))}</div>
    </div>
    <h2>Wat posten ze? (ontleding)</h2>
    <div class="card">
      <div class="row"><span class="factbadge">POSTS</span><b>Thema's:</b> {esc(', '.join(pa.get('themes',[])) or '—')}</div>
      <div class="row"><b>Toon:</b> {esc(pa.get('tone','—'))}</div>
      <div class="row"><b>Aanbiedingen:</b> {esc(' | '.join(pa.get('offers',[])) or 'geen gevonden')}</div>
      <div class="row"><b>Frequentie:</b> {esc(pa.get('frequency','—'))}</div>
    </div>
    <h2>Waar zij bloeden (zwaktes)</h2>
    <div class="card"><div class="row">{esc(weak if isinstance(weak,str) else chr(10).join('• '+x for x in weak))}</div></div>
    <h2>Waarom wij (onze tegenzet)</h2>
    <div class="card">
      <div class="row"><b>Hun zwakte → ons spel:</b> {esc(bc.get('their_weakness','—'))}</div>
      <div class="row"><b>Ons spel:</b> {esc(bc.get('our_play','—'))}</div>
      <div class="row"><b>Confidence:</b> {esc(bc.get('confidence','—'))}</div>
    </div>
    <h2>Bewijs</h2>
    <div class="card">
      <div class="row"><span class="factbadge">FEIT</span> <b>Positionering:</b> {esc(c.get('positioning',''))}</div>
      {evidence_links(c)}
    </div>
    """
    return page(c["name"], body)

def evidence_links(c):
    ev = c.get("evidence") or []
    if not ev:
        return '<div class="row">geen bewijs geregistreerd</div>'
    out = []
    for e in ev:
        cid = c["id"]
        datum = re.sub(r"[^0-9_]", "", e.get("retrieved", "").replace(" ", "_").replace(":", ""))
        out.append(f'<div class="quote">“{esc(e.get("quote",""))}”</div>'
                   f'<div class="row"><a href="{esc(e.get("source_url","#"))}" target="_blank" rel="noopener">{esc(e.get("source_url",""))}</a> · {esc(e.get("retrieved",""))}</div>'
                   f'<div class="row"><a href="/evidence/{cid}/{esc(datum)}">[bewijspagina]</a></div>')
    return "\n".join(out)

def render_analysis(d):
    comps = d["competitors"]
    rows = ""
    for c in comps:
        pa = c.get("post_analysis") or {}
        rows += (f"<tr><td><b>{esc(c['name'])}</b></td>"
                 f"<td>{esc(', '.join(pa.get('themes',[]) or ['—']))}</td>"
                 f"<td>{esc(pa.get('tone','—'))}</td>"
                 f"<td>{esc(' | '.join(pa.get('offers',[]) or ['geen']))}</td>"
                 f"<td>{esc(pa.get('frequency','—'))}</td></tr>")
    weak_rows = ""
    for c in comps:
        weak = c.get("weaknesses") or ""
        weak_rows += f"<tr><td><b>{esc(c['name'])}</b></td><td>{esc(weak if isinstance(weak,str) else '; '.join(weak))}</td></tr>"
    body = f"""
    <a class="back" href="/">← Terug naar overzicht</a>
    <h1>Analyse-hoofdstukken</h1>
    <p class="row">Synthese over alle {len(comps)} concurrenten — patronen die je in één oogopslag ziet.</p>
    <h2>Wat posten ze? (thema / toon / aanbod / frequentie)</h2>
    <div class="card"><table><tr><th>Concurrent</th><th>Thema's</th><th>Toon</th><th>Aanbod</th><th>Frequentie</th></tr>{rows}</table></div>
    <h2>Waar bloeden ze? (zwaktes naast elkaar)</h2>
    <div class="card"><table><tr><th>Concurrent</th><th>Zwakte</th></tr>{weak_rows}</table></div>
    <div class="nav"><a href="/">Overzicht</a><a href="/concurrent/{esc(comps[0]['id'])}">Eerste concurrent</a></div>
    """
    return page("Analyse", body)

def render_evidence(c, ev):
    cid = c["id"]
    datum = re.sub(r"[^0-9_]", "", ev.get("retrieved", "").replace(" ", "_").replace(":", ""))
    snap = ev.get("snapshot", "")
    body = f"""
    <a class="back" href="/concurrent/{cid}">← Terug naar {esc(c['name'])}</a>
    <h1>Bewijs — {esc(c['name'])}</h1>
    <div class="card">
      <div class="row"><span class="factbadge">FEIT</span> <b>Gevonden op:</b> <a href="{esc(ev.get('source_url','#'))}" target="_blank" rel="noopener">{esc(ev.get('source_url',''))}</a></div>
      <div class="row"><b>Datum:</b> {esc(ev.get('retrieved',''))}</div>
      <div class="quote">“{esc(ev.get('quote',''))}”</div>
      {f'<div class="row"><a href="/{esc(snap)}" target="_blank" rel="noopener">[origineel snapshot-bestand]</a></div>' if snap else ''}
    </div>
    """
    return page(f"Bewijs {c['name']}", body)

def render_dossier(c):
    raw_path = os.path.join(PUBLISH, "raw", c.get("parent_brand", "powerland"), f"{c['id']}.md")
    if os.path.exists(raw_path):
        md = open(raw_path, encoding="utf-8").read()
        lines = []
        for ln in md.splitlines():
            ln = esc(ln)
            if ln.startswith("## "):
                lines.append(f"<h2>{ln[3:]}</h2>")
            elif ln.startswith("# "):
                lines.append(f"<h1>{ln[2:]}</h1>")
            elif ln.startswith("- "):
                lines.append(f"<div class='row'>• {ln[2:]}</div>")
            else:
                lines.append(f"<div class='row'>{ln}</div>" if ln.strip() else "<br>")
        body = "\n".join(lines)
    else:
        body = "<div class='row'>dossier niet gevonden</div>"
    return page(f"Dossier {c['name']}", f'<a class="back" href="/concurrent/{c["id"]}">← Terug naar {esc(c["name"])}</a><h1>Dossier — {esc(c["name"])}</h1><div class="card">{body}</div>')

if __name__ == "__main__":
    d = load()
    print("detail mr-solar:", len(render_detail(d["competitors"][4])))
    print("analyse:", len(render_analysis(d)))
    ev = d["competitors"][4].get("evidence", [{}])[0]
    print("evidence:", len(render_evidence(d["competitors"][4], ev)))
    print("dossier:", len(render_dossier(d["competitors"][4])))
