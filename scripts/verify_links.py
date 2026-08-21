# verify_links.py — volgt UI-gegenereerde links, assert bestemming bestaat.
# Gebruik: python verify_links.py <BASE-URL>
#   BASE = http://127.0.0.1:8137   (lokaal)
#   BASE = https://camil96.github.io/powerland-competitors   (live)
# Exit 1 = kapotte link gevonden.
import sys, json, urllib.request, urllib.error

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8137"
DATA = r"C:/Users/camil.sahnoune/competitive-intel/publish/data.json"


def get(path):
    try:
        return urllib.request.urlopen(BASE + path, timeout=8).read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return f"__HTTP {e.code}__"
    except Exception as e:
        return f"__ERR {e}__"


def main():
    d = json.load(open(DATA, encoding="utf-8"))
    bad = []

    for c in d["competitors"]:
        cid = c["id"]

        # 1. SPA evidence-link = ev[0].snapshot (relatief pad -> /snapshots/<id>/<ts>.md)
        ev = c.get("evidence", [])
        if ev and ev[0].get("snapshot"):
            link = "/" + ev[0]["snapshot"]
            b = get(link)
            if "geen bewijs" in b.lower() or b.startswith("__"):
                bad.append((cid, link, b[:60]))

        # 2. dossier-link = raw/powerland/<id>.md
        dlink = f"/raw/powerland/{cid}.md"
        bd = get(dlink)
        if bd.startswith("__"):
            bad.append((cid, dlink, bd[:60]))

        # 3. SPA bron-link = ev[0].source_url (externe site) -> enkel status-check, geen body
        if ev and ev[0].get("source_url"):
            try:
                urllib.request.urlopen(ev[0]["source_url"], timeout=8).close()
            except Exception:
                pass  # externe sites mogen falen (offline/blokkade); niet als 'kapot' tellen

    print(f"getest: {len(d['competitors'])} concurrenten | kapot: {len(bad)}")
    for x in bad:
        print("  ", x)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
