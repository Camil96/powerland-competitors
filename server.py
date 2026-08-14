#!/usr/bin/env python3.12
"""Lokale dashboard-server voor concurrentie-intelligentie (Powerland/Vandotec).
Stdlib-only. Geen externe packages. Draai: python3.12 server.py
"""
import json
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from pages import render_detail, render_analysis, render_evidence, render_dossier
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data.json")
HTML = os.path.join(BASE, "index.html")
RAW = os.path.join(BASE, "raw")
PORT = 8137
_lock = threading.Lock()


def load_data():
    try:
        with open(DATA, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        # corrupt/ontbrekend -> geef lege structuur terug i.p.v. 500
        print(f"[warn] data.json kon niet geladen worden: {e}")
        return {"competitors": [], "brands": {}, "analysis": {}}


def save_data(d):
    tmp = DATA + ".tmp"
    with _lock, open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, DATA)  # atomair: geen halve writes


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, b"")

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/" or u.path == "/dashboard":
            if os.path.exists(HTML):
                with open(HTML, "rb") as f:
                    self._send(200, f.read(), "text/html")
            else:
                self._send(200, b"<h1>dashboard.html nog niet gebouwd</h1><p>Start de scrape, dan bouw ik het.</p>", "text/html")
        elif u.path == "/data.json":
            self._send(200, json.dumps(load_data(), ensure_ascii=False))
        elif u.path == "/analyse":
            self._send(200, render_analysis(load_data()), "text/html")
        elif u.path.startswith("/concurrent/"):
            cid = u.path[len("/concurrent/"):].strip("/")
            if not re.fullmatch(r"[a-z0-9-]+", cid):
                self._send(404, b"bad id")
            else:
                c = next((x for x in load_data()["competitors"] if x["id"] == cid), None)
                self._send(200, render_detail(c) if c else "<h1>niet gevonden</h1>", "text/html")
        elif u.path.startswith("/dossier/"):
            cid = u.path[len("/dossier/"):].strip("/")
            if not re.fullmatch(r"[a-z0-9-]+", cid):
                self._send(404, b"bad id")
            else:
                c = next((x for x in load_data()["competitors"] if x["id"] == cid), None)
                self._send(200, render_dossier(c) if c else "<h1>niet gevonden</h1>", "text/html")
        elif u.path.startswith("/evidence/"):
            # /evidence/<id>/<snapshot-bestandsnaam-zonder-ext>
            # matcht op het snapshot-pad uit de evidence-entry (bijv. snapshots/reeload/20260811-1159)
            parts = u.path[len("/evidence/"):].split("/")
            if len(parts) != 2 or not re.fullmatch(r"[a-z0-9-]+", parts[0]) or not re.fullmatch(r"[0-9_-]+", parts[1]):
                self._send(404, b"bad id")
            else:
                d = load_data()
                c = next((x for x in d["competitors"] if x["id"] == parts[0]), None)
                if not c:
                    self._send(404, b"niet gevonden")
                else:
                    want = f"{parts[0]}/{parts[1]}"  # id/naam zoals in snapshot-veld
                    ev = next((e for e in c.get("evidence", []) if (e.get("snapshot") or "").replace("snapshots/","").replace(".md","").replace("\\","/") == want), None)
                    self._send(200, render_evidence(c, ev) if ev else "<h1>geen bewijs</h1>", "text/html")
        elif u.path.startswith("/raw/") or u.path.startswith("/snapshots/"):
            name = u.path[len("/raw/"):]
            # veilig pad: alleen bestandsnaam, geen traversaal
            name = os.path.basename(name)
            for sub in ("powerland", "vandotec"):
                p = os.path.join(RAW, sub, name)
                if os.path.exists(p):
                    with open(p, "rb") as f:
                        return self._send(200, f.read(), "text/markdown")
            self._send(404, b"not found")
        elif u.path == "/api/competitors":
            self._send(200, json.dumps(load_data().get("competitors", []), ensure_ascii=False))
        elif u.path.startswith("/assets/"):
            name = os.path.basename(u.path)
            p = os.path.join(BASE, "assets", name)
            if os.path.exists(p):
                ctype = "image/svg+xml" if name.endswith(".svg") else ("image/png" if name.endswith(".png") else "application/octet-stream")
                with open(p, "rb") as f:
                    return self._send(200, f.read(), ctype)
            self._send(404, b"not found")
        else:
            self._send(404, b"unknown route")

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/api/competitor":
            try:
                length = int(self.headers.get("Content-Length", 0))
            except ValueError:
                return self._send(400, json.dumps({"error": "bad Content-Length"}))
            if length <= 0 or length > 1_000_000:  # cap 1MB
                return self._send(400, json.dumps({"error": "Content-Length out of range"}))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                new = json.loads(raw)
            except Exception as e:
                return self._send(400, json.dumps({"error": str(e)}))
            if not isinstance(new, dict):
                return self._send(400, json.dumps({"error": "body must be a JSON object"}))
            data = load_data()
            cid = new.get("id") or str(new.get("name", "")).lower().replace(" ", "-")
            if not cid:
                return self._send(400, json.dumps({"error": "id or name required"}))
            new["id"] = cid
            data["competitors"] = [c for c in data["competitors"] if c.get("id") != cid]
            data["competitors"].append(new)
            save_data(data)
            return self._send(201, json.dumps({"ok": True, "id": cid, "total": len(data["competitors"])}))
        self._send(404, b"unknown route")

    def log_message(self, *a):
        pass  # stil


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Dashboard server: http://127.0.0.1:{PORT}/")
    print(f"Data: {DATA}")
    srv.serve_forever()
