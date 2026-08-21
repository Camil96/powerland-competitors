#!/usr/bin/env python3.12
"""Build-stap: genereer statische HTML-pagina's uit data.json (voor GitHub Pages).
Zet pages.REL=True zodat alle links relatief worden (werkt onder subdirectory EN lokaal).
Schrijft naar repo-root: analyse.html, concurrent-<id>.html, evidence-<id>-<snap>.html, dossier-<id>.html.
"""
import os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import pages

pages.REL = True  # relatieve links i.p.v. server-routes

def snap_name(ev):
    return (ev.get("snapshot") or "").split("/")[-1].replace(".md", "")

def main():
    d = pages.load()
    written = []
    for c in d["competitors"]:
        cid = c["id"]
        # detail
        p = os.path.join(BASE, f"concurrent-{cid}.html")
        open(p, "w", encoding="utf-8").write(pages.render_detail(c))
        written.append(p)
        # evidence (1 per evidence-item)
        for ev in c.get("evidence", []) or []:
            if not ev:
                continue
            sn = snap_name(ev)
            p = os.path.join(BASE, f"evidence-{cid}-{sn}.html")
            open(p, "w", encoding="utf-8").write(pages.render_evidence(c, ev))
            written.append(p)
        # dossier
        p = os.path.join(BASE, f"dossier-{cid}.html")
        open(p, "w", encoding="utf-8").write(pages.render_dossier(c))
        written.append(p)
    # analyse (1)
    p = os.path.join(BASE, "analyse.html")
    open(p, "w", encoding="utf-8").write(pages.render_analysis(d))
    written.append(p)
    print(f"gegenereerd: {len(written)} statische bestanden")
    for w in written:
        print("  ", os.path.basename(w))

if __name__ == "__main__":
    main()
