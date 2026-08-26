#!/usr/bin/env python3.12
# pages.py — FASE 3: HTML-generatoren voor detail/analyse/evidence/dossier.
# Server-side rendering vanuit data.json. Geen nieuwe data nodig.
import os, json, html, re

PUBLISH = r"C:/Users/camil.sahnoune/competitive-intel/publish"
DATA = os.path.join(PUBLISH, "data.json")

# REL = True bij statische build: alle links relatief maken (werkt onder GitHub Pages
# subdirectory EN lokaal). Zet op False voor server-side rendering (server.py op root /).
REL = False

def mklink(href):
    """Zet een server-route-link om in een relatief statisch-bestandspad (alleen als REL)."""
    if not REL:
        return href
    if not href or href.startswith(("http", "#", "mailto:")):
        return href
    if href == "/":
        return "index.html"
    if href == "/analyse":
        return "analyse.html"
    if href.startswith("/concurrent/"):
        cid = href[len("/concurrent/"):].strip("/")
        return f"concurrent-{cid}.html"
    if href.startswith("/evidence/"):
        rest = href[len("/evidence/"):].strip("/")
        cid, _, snap = rest.partition("/")
        return f"evidence-{cid}-{snap}.html"
    if href.startswith("/dossier/"):
        cid = href[len("/dossier/"):].strip("/")
        return f"dossier-{cid}.html"
    if href.startswith("/assets/"):
        return href[1:]  # assets/<x>
    if href.startswith("/raw/"):
        return href[1:]   # raw/<x>
    if href.startswith("/snapshots/"):
        return href[1:]   # snapshots/<x>
    return href

def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)

def esc(s):
    return html.escape(str(s or ""))

def placeholder(text):
    return f'<span class="placeholder">{text}</span>'

STYLE = """
:root{
  --pl-blue:#213e86;
  --pl-teal:#37b49e;
  --pl-teal-soft:#d7f0ec;
  --bg:#fafafa;
  --panel:#fff;
  --text:#212529;
  --muted:#7c7c7c;
  --line:#e3e8ef;
  --radius:18px;
}

*{box-sizing:border-box}

body{
  margin:0;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;
  background:var(--bg);
  color:var(--text);
  line-height:1.55;
}

header{
  background:#fff;
  border-bottom:1px solid var(--line);
  padding:14px 24px;
  display:flex;
  align-items:center;
  gap:14px;
}

header img{height:30px}
header .tag{margin-left:auto;color:var(--pl-teal);font-weight:800}

.wrap{
  max-width:1000px;
  margin:0 auto;
  padding:28px 22px 60px;
}

.card{
  background:var(--panel);
  border:1px solid var(--line);
  border-radius:var(--radius);
  padding:22px 26px;
  margin:18px 0;
  box-shadow:0 4px 18px rgba(33,62,134,.06);
}

h1{font-size:30px;margin:0 0 4px;color:var(--pl-blue)}
h2{font-size:20px;margin:26px 0 10px;color:var(--pl-blue)}

.factbadge{
  display:inline-block;
  font-size:10px;
  font-weight:800;
  letter-spacing:.5px;
  color:#16483f;
  background:var(--pl-teal-soft);
  border-radius:6px;
  padding:2px 7px;
  margin-right:6px;
  vertical-align:middle;
}

.row{font-size:14px;margin:8px 0}
.row b{color:var(--text)}

a{
  color:var(--pl-blue);
  text-decoration:none;
}

a:hover{
  text-decoration:underline;
}

.tags{
  display:flex;
  flex-wrap:wrap;
  gap:6px;
  margin:8px 0;
}

.tag{
  background:#f4f6f9;
  border:1px solid var(--line);
  border-radius:8px;
  padding:3px 10px;
  font-size:11.5px;
  color:var(--muted);
  font-weight:600;
}

.bar{
  width:120px;
  height:8px;
  background:var(--line);
  border-radius:99px;
  overflow:hidden;
  display:inline-block;
  vertical-align:middle;
}

.bar i{
  display:block;
  height:100%;
  background:var(--pl-teal);
}

.quote{
  font-style:italic;
  border-left:3px solid var(--pl-teal);
  padding-left:12px;
  margin:10px 0;
  color:var(--text);
}

table{
  width:100%;
  border-collapse:collapse;
  margin:12px 0;
  font-size:13px;
}

th,td{
  border:1px solid var(--line);
  padding:8px 10px;
  text-align:left;
  vertical-align:top;
}

th{
  background:var(--pl-teal-soft);
  color:#16483f;
}

.back{
  display:inline-block;
  margin:14px 0;
  color:var(--pl-teal);
  font-weight:700;
}

.placeholder{
  color:#9aa3b2;
  font-style:italic;
  font-size:13px;
}
"""

def page(title, body):
    return f"""<!DOCTYPE html><html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — Powerland Concurrentie</title>
<link rel="icon" href="{mklink('/assets/favicon.png')}">
<style>{STYLE}</style></head><body>
<header><img src="{mklink('/assets/logo.svg')}" alt="Powerland"><b>Concurrentie-Intelligentie</b><span class="tag">Fight the average.</span></header>
<div class="wrap">{body}</div></body></html>"""

def channel_links(c):
    parts = []
    for k, v in (c.get("social_channels") or {}).items():
        if isinstance(v, dict) and v.get("url"):
            parts.append(f'<a href="{esc(v["url"])}" target="_blank" rel="noopener">{esc(k)}</a>')
    if parts:
        return " · ".join(parts)
    return "n.v.t."

def battlecard_text(bc, key):
    val = (bc or {}).get(key, "").strip()
    if val and val not in ("—", "n.v.t."):
        return esc(val)
    return placeholder("nog niet ingevuld")

def weaknesses_list(c):
    """weaknesses is een LIJST in data.json (geen string). Render als <li>-lijst."""
    items = c.get("weaknesses") or []
    if isinstance(items, str):
        items = [items]  # oude string-vorm afvangen
    if not items:
        return placeholder("nog niet ingevuld")
    return "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul>"

def render_detail(c):
    analysis = c.get("post_analysis") or {}
    battlecard = c.get("battlecard") or {}
    pct = int(c.get("overlap_score_powerland", 0) / 5 * 100)

    themes = analysis.get("themes", [])
    tone = analysis.get("tone", "")
    offers = analysis.get("offers", [])
    frequency = analysis.get("frequency", "")

    weaknesses_display = weaknesses_list(c)
    positioning = c.get("positioning", "").strip()
    positioning_display = positioning if positioning else "geen"
    positioning_display = esc(positioning_display)

    parts = []
    parts.append('<a class="back" href="{mklink(\'/\')}">← Terug naar overzicht</a>')
    parts.append(f"<h1>{esc(c['name'])}</h1>")

    parts.append('<div class="card">')
    parts.append(f"<div class='row'><b>Categorie:</b> {esc(c.get('category',''))}</div>")
    parts.append(f"<div class='row'><b>Overlap met Powerland:</b> <span class='bar'><i style='width:{pct}%'></i></span> {esc(c.get('overlap_score_powerland'))}/5</div>")
    parts.append(f"<div class='row'><b>Kanalen:</b> {channel_links(c)}</div>")
    parts.append(f"<div class='row'><b>Diensten:</b> {esc(', '.join(c.get('services',[])))}</div>")
    parts.append(f"<div class='row'><b>Doelgroep:</b> {esc(', '.join(c.get('target_audience',[])))}</div>")
    parts.append('</div>')

    parts.append('<h2>Wat posten ze? (ontleding)</h2>')
    parts.append('<div class="card">')
    parts.append(f"<div class='row'><span class='factbadge'>POSTS</span><b>Thema's:</b> {esc(', '.join(themes) or '—')}</div>")
    parts.append(f"<div class='row'><b>Toon:</b> {esc(tone or '—')}</div>")
    parts.append(f"<div class='row'><b>Aanbiedingen:</b> {esc(' | '.join(offers) or 'geen gevonden')}</div>")
    parts.append(f"<div class='row'><b>Frequentie:</b> {esc(frequency or '—')}</div>")
    parts.append('</div>')

    parts.append('<h2>Waar zij bloeden (zwaktes)</h2>')
    parts.append('<div class="card"><div class="row">')
    parts.append(weaknesses_display)
    parts.append('</div></div>')

    parts.append('<h2>Waarom wij (onze tegenzet)</h2>')
    parts.append('<div class="card">')
    parts.append(f"<div class='row'><b>Waar zij bloeden (zwaktes):</b> {battlecard_text(battlecard, 'their_weakness')}</div>")
    parts.append(f"<div class='row'><b>Waar wij winnen:</b> {battlecard_text(battlecard, 'our_play')}</div>")
    parts.append(f"<div class='row'><b>Vertrouwen:</b> {battlecard_text(battlecard, 'confidence')}</div>")
    parts.append('</div>')

    parts.append('<h2>Bewijs</h2>')
    parts.append('<div class="card">')
    # voorkom dubbele tekst: als positionering identiek is aan de eerste evidence-quote,
    # toon enkel de quote (niet ook de Positionering-regel)
    first_quote = (c.get("evidence") or [{}])[0].get("quote", "")
    if positioning_display and first_quote and positioning_display.strip() != first_quote.strip():
        parts.append(f"<div class='row'><span class='factbadge'>FEIT</span> <b>Positionering:</b> {positioning_display}</div>")
    parts.append(evidence_links(c))
    parts.append('</div>')

    return page(c["name"], "\n".join(parts))

def evidence_links(competitor):
    ev_list = competitor.get("evidence", []) or []
    if not ev_list:
        return '<div class="row">geen bewijs geregistreerd</div>'

    parts = []
    cid = competitor["id"]
    for ev_item in ev_list:
        if not ev_item:
            continue
        snap_name = (ev_item.get("snapshot") or "").split("/")[-1].replace(".md", "")

        source_url = ev_item.get("source_url", "#")
        pointer = f'<a class="ev-link" href="{mklink("/evidence/"+cid+"/"+snap_name)}" target="_blank" rel="noopener">Bewijs bekijken →</a>'

        parts.append('<div class="quote">“' + esc(ev_item.get("quote", "")) + '”</div>')
        parts.append(
            f"<div class='row'><a href='{esc(source_url)}' target='_blank' rel='noopener'>{esc(source_url)}</a>"
            f" · {esc(ev_item.get('retrieved', ''))}</div>"
        )
        parts.append(f"<div class='row'>{pointer}</div>")

    return "\n".join(parts)

def render_analysis(data):
    comp = data["competitors"]
    n = len(comp)

    table_body = []
    weak_body = []
    for c in comp:
        analysis = c.get("post_analysis") or {}
        themes = analysis.get("themes", [])
        tone = analysis.get("tone", "")
        offers = analysis.get("offers", [])
        frequency = analysis.get("frequency", "")

        name = esc(c["name"])
        themes_cell = esc(", ".join(themes) if themes else "—")
        tone_cell = esc(tone or "—")
        offers_cell = esc(" | ".join(offers) if offers else "geen")
        freq_cell = esc(frequency or "—")

        table_body.append(
            f"<tr><td><b>{name}</b></td><td>{themes_cell}</td><td>{tone_cell}</td><td>{offers_cell}</td><td>{freq_cell}</td></tr>"
        )

        weaknesses = weaknesses_list(c)
        weak_cell = weaknesses
        weak_body.append(f"<tr><td><b>{name}</b></td><td>{weak_cell}</td></tr>")

    rows_str = "\n".join(table_body)
    weak_str = "\n".join(weak_body)

    parts = []
    parts.append('<a class="back" href="{mklink(\'/\')}">← Terug naar overzicht</a>')
    parts.append("<h1>Analyse-hoofdstukken</h1>")
    parts.append(f'<p class="row">Synthese over alle {n} concurrenten — patronen die je in één oogopslag ziet.</p>')
    parts.append("<h2>Wat posten ze? (thema / toon / aanbod / frequentie)</h2>")
    parts.append(f'<div class="card"><table><tr><th>Concurrent</th><th>Thema\'s</th><th>Toon</th><th>Aanbod</th><th>Frequentie</th></tr>{rows_str}</table></div>')
    parts.append("<h2>Waar bloeden ze? (zwaktes naast elkaar)</h2>")
    parts.append(f'<div class="card"><table><tr><th>Concurrent</th><th>Zwakte</th></tr>{weak_str}</table></div>')
    nav_overzicht = mklink("/")
    nav_eerste = mklink("/concurrent/" + comp[0]["id"])
    parts.append(f'<div class="nav"><a href="{nav_overzicht}">Overzicht</a> · <a href="{nav_eerste}">Eerste concurrent</a></div>')

    return page("Analyse", "\n".join(parts))

def render_evidence(c, ev):
    cid = c["id"]

    snap_name = (ev.get("snapshot") or "").split("/")[-1].replace(".md", "")

    source_url = ev.get("source_url", "#")
    quote = ev.get("quote", "")
    snap = ev.get("snapshot", "")

    parts = []
    bl = mklink("/concurrent/" + cid)
    parts.append(f'<a class="back" href="{bl}">← Terug naar {esc(c["name"])}</a>')
    parts.append(f"<h1>Bewijs — {esc(c['name'])}</h1>")
    parts.append('<div class="card">')
    parts.append(
        f"<div class='row'><span class='factbadge'>FEIT</span> <b>Gevonden op:</b> "
        f"<a href='{esc(source_url)}' target='_blank' rel='noopener'>{esc(source_url)}</a></div>"
    )
    parts.append(f"<div class='row'><b>Datum:</b> {esc(ev.get('retrieved',''))}</div>")
    if quote:
        parts.append(f"<div class='quote'>“{esc(quote)}”</div>")
    else:
        parts.append('<div class="row"><span class="placeholder">geen quote opgeslagen</span></div>')
    if snap:
        parts.append(f"<div class='row'><a href='/{esc(snap)}' target='_blank' rel='noopener'>[origineel snapshot-bestand]</a></div>")
    parts.append('</div>')

    return page(f"Bewijs {c['name']}", "\n".join(parts))

def render_dossier(c):
    raw_dir = c.get("parent_brand", "powerland")
    md_path = os.path.join(PUBLISH, "raw", raw_dir, f"{c['id']}.md")

    if not os.path.exists(md_path):
        md_body = placeholder("dossier niet gevonden")
    else:
        md = open(md_path, encoding="utf-8").read()
        lines = []
        for raw in md.splitlines():
            cleaned = esc(raw)
            stripped = cleaned.strip()
            if raw.startswith("## "):
                lines.append(f"<h2>{cleaned[3:]}</h2>")
            elif raw.startswith("# "):
                lines.append(f"<h1>{cleaned[2:]}</h1>")
            elif raw.startswith("- "):
                lines.append(f"<div class='row'>• {cleaned[2:]}</div>")
            else:
                lines.append(f"<div class='row'>{stripped if stripped else '<br>'}</div>")
        md_body = "\n".join(lines)

    parts = []
    bl = mklink("/concurrent/" + c["id"])
    parts.append(f'<a class="back" href="{bl}">← Terug naar {esc(c["name"])}</a>')
    parts.append(f"<h1>Dossier — {esc(c['name'])}</h1>")
    parts.append(f'<div class="card">{md_body}</div>')
    return page(f"Dossier {c['name']}", "\n".join(parts))

if __name__ == "__main__":
    d = load()
    print("detail mr-solar:", len(render_detail(d["competitors"][4])))
    print("analyse:", len(render_analysis(d)))
    ev = d["competitors"][4].get("evidence", [{}])[0]
    print("evidence:", len(render_evidence(d["competitors"][4], ev)))
    print("dossier:", len(render_dossier(d["competitors"][4])))
