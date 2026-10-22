#!/usr/bin/env python3
"""PCEP LAN Sync Server — manual phone <-> laptop stats sync over home WiFi.

Design (Commander directive 2026-10-16):
  * MANUAL: the phone app hits Sync while both devices are on the SAME WiFi.
    The laptop sees the incoming request (logged here + logs/sync.log).
  * TWO-WAY: phone sends its record; server merges with ITS master using
    per-question HIGHEST-count wins + history/log dedupe — whichever side is
    behind gets added to.
  * BACKUP: BEFORE every merge, the current master is copied to
    sync_server/backups/pcep_stats_backup_<epoch>.json (rotation keeps the
    last 10) so a bad sync can never lose the record of record.
  * CORS: the phone app runs from file:// (origin "null") — every response
    carries Access-Control-Allow-Origin: * so Chrome accepts the fetch.

Endpoints:
  GET  /ping  -> {ok, version, questions}          (connectivity + summary)
  GET  /stats -> {ok, version, questions, answers, record}
             (PULL: a device fetches the merged record so BOTH devices show
              identical numbers and resume the SAME drill)
  POST /sync  <- raw stats JSON {seen,correct,wrong,flagged,history,log}
              -> {merged, direction, backup, questions}

Run (visible window, or via the PCEPSyncServer scheduled task):
  python pcep_sync_server.py [--port 8787] [--host 0.0.0.0]

NO port 80. NO secrets. LAN traffic only.
"""
import argparse
import json
import os
import shutil
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_VERSION = "2.5.1"
TRAINER_FILE = Path(__file__).resolve().parent / "PCEP_Trainer_v2.5.1.html"
RECORD_FILE = Path(__file__).with_name("sync_server") / "pcep_stats_master.json"
BACKUP_DIR = Path(__file__).with_name("sync_server") / "backups"
LOG_FILE = Path(__file__).with_name("sync_server") / "sync.log"
BACKUP_KEEP = 10
FIELDS = ("seen", "correct", "wrong", "flagged", "history", "log")


def blank():
    # NO seed here: a time-based seed would differ on every read, so the
    # "shared order" would never be stable. The seed is persisted once by
    # ensure_seed() and lives in the record file from then on.
    return {"seen": {}, "correct": {}, "wrong": {}, "flagged": {},
            "history": [], "log": []}


def load_record():
    if RECORD_FILE.exists():
        try:
            obj = json.loads(RECORD_FILE.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                return obj
        except (OSError, json.JSONDecodeError) as e:
            log(f"WARN: master unreadable ({e}) — using blank; NOT deleting file")
    return blank()


def ensure_seed():
    """The server OWNS the shared drill seed. Persist one on first run so every
    device that pulls receives the same shuffle order."""
    rec = load_record()
    if not rec.get("seed"):
        now = int(time.time() * 1000)
        rec["seed"] = {"value": now % 2147483647, "savedAt": now}
        try:
            backup_record()          # same doctrine as every other write
            save_record(rec)
            log(f"seed established: {rec['seed']['value']}")
        except OSError as e:
            log(f"WARN: could not persist seed ({e})")
    return rec


def save_record(obj):
    RECORD_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = RECORD_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(tmp, RECORD_FILE)


def backup_record():
    """Copy the CURRENT master aside BEFORE overwriting. Rotation keeps 10."""
    if not RECORD_FILE.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    dest = BACKUP_DIR / f"pcep_stats_backup_{time.time_ns()}.json"  # ns => unique even within one second
    shutil.copy2(RECORD_FILE, dest)
    old = sorted(BACKUP_DIR.glob("pcep_stats_backup_*.json"))[:-BACKUP_KEEP]
    for f in old:
        try:
            f.unlink()
        except OSError:
            pass
    return str(dest.name)


def pick_counts(a, b):
    out = dict(a or {})
    for k, v in (b or {}).items():
        try:
            out[k] = max(int(out.get(k) or 0), int(v or 0))
        except (TypeError, ValueError):
            continue
    return out


def dedupe_list(a, b):
    out, seen = [], set()
    for item in (list(a) if isinstance(a, list) else []) + (list(b) if isinstance(b, list) else []):
        key = json.dumps(item, sort_keys=True, default=str)
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def merge_drill(a, b):
    """In-progress drill state is ONE session, not an accumulation — so it is
    last-writer-wins by savedAt (never a union, which would corrupt order)."""
    def ts(r):
        if isinstance(r, dict) and isinstance(r.get("savedAt"), (int, float)):
            return int(r.get("savedAt") or 0)
        return -1
    return b if ts(b) >= ts(a) else a


def merge_stats(server, phone):
    m = {}
    for f in ("seen", "correct", "wrong", "flagged"):
        m[f] = pick_counts(server.get(f), phone.get(f))
    for f in ("history", "log"):
        m[f] = dedupe_list(server.get(f), phone.get(f))
    m["drill"] = merge_drill(server.get("drill"), phone.get("drill"))
    # The SEED is canonical on the server: the server's copy wins, so every
    # device shuffles into the SAME order. EXCEPTION: a device that started a
    # NEW run mints a seed marked reason="run" - that fresh order must
    # propagate to the peer, so it wins when it is newer. A seed marked
    # "adopt" (a fresh device that had none) never overrides the server.
    srv_seed = server.get("seed")
    ph_seed = phone.get("seed")
    if (ph_seed and ph_seed.get("reason") == "run"
            and ph_seed.get("savedAt", -1) > (srv_seed or {}).get("savedAt", -1)):
        m["seed"] = ph_seed
    else:
        m["seed"] = srv_seed or ph_seed
    return m


def side_size(rec):
    return sum(int(v or 0) for v in (rec.get("seen") or {}).values())


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


class Handler(BaseHTTPRequestHandler):
    server_version = "PCEPSync/2.5.1"

    def _cors(self, ctype="application/json"):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Access-Control-Request-Private-Network")
        # Chrome sends a Private-Network-Access preflight (OPTIONS with
        # Access-Control-Request-Private-Network: true) when a content:// or
        # file:// page fetches a LAN IP. Without this response header the
        # browser rejects the fetch as "Failed to fetch" BEFORE any real
        # request is sent — sync from the Drive/file copy needs it (2026-10-18).
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def _send(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        log(f"OPTIONS {self.path} from {self.client_address[0]} | origin={self.headers.get('Origin')} | "
            f"ACRM={self.headers.get('Access-Control-Request-Method')} | "
            f"ACRH={self.headers.get('Access-Control-Request-Headers')} | "
            f"ACRPN={self.headers.get('Access-Control-Request-Private-Network')}")
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/ping":
            log(f"GET /ping from {self.client_address[0]} | origin={self.headers.get('Origin')}")
        elif path != "/" and path not in ("/index.html", "/trainer"):
            log(f"GET {path} from {self.client_address[0]} (unknown) | origin={self.headers.get('Origin')}")
        if path in ("/", "/index.html", "/trainer"):
            # Serve the trainer itself: opening http://HOST:8787/ makes the page
            # SAME-ORIGIN with /ping and /sync — mobile Chrome's local-network
            # access gate does not apply to same-origin requests (fix for
            # content:// / file:// fetch failures, 2026-10-18).
            try:
                data = TRAINER_FILE.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except OSError as e:
                self._send({"ok": False, "error": f"trainer unavailable: {e}"}, 500)
            return
        if path == "/ping":
            rec = load_record()
            self._send({"ok": True, "version": APP_VERSION,
                        "questions": len(rec.get("seen") or {}),
                        "answers": side_size(rec)})
        elif path == "/stats":
            # PULL route: a device asks for the laptop's merged record so BOTH
            # sides show identical numbers without a manual button press.
            rec = load_record()
            self._send({"ok": True, "version": APP_VERSION,
                        "questions": len(rec.get("seen") or {}),
                        "answers": side_size(rec),
                        "record": rec})
        else:
            self._send({"ok": False, "error": "unknown path"}, 404)

    def do_POST(self):
        if self.path.split("?")[0] != "/sync":
            self._send({"ok": False, "error": "unknown path"}, 404)
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            phone = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
            if not isinstance(phone, dict):
                raise ValueError("payload not an object")
        except (ValueError, json.JSONDecodeError) as e:
            log(f"REJECTED sync from {self.client_address[0]}: bad payload ({e})")
            self._send({"ok": False, "error": f"bad payload: {e}"}, 400)
            return

        client_ip = self.client_address[0]
        server_rec = load_record()
        s_n, p_n = side_size(server_rec), side_size(phone)
        backup = backup_record()  # <-- ONE version of record kept, ALWAYS, BEFORE write
        merged = merge_stats(server_rec, phone)
        save_record(merged)
        if s_n == p_n:
            direction = "records were already equal — confirmed identical"
        elif p_n > s_n:
            direction = f"phone was ahead ({p_n} > {s_n} answers) — laptop updated"
        else:
            direction = f"laptop was ahead ({s_n} > {p_n} answers) — phone updated"
        log(f"SYNC from {client_ip}: {p_n} phone answers vs {s_n} laptop answers "
            f"-> {direction} | backup: {backup or 'none (first sync)'} | "
            f"record now {side_size(merged)} answers / {len(merged.get('seen') or {})} questions")
        self._send({"ok": True, "merged": merged, "direction": direction,
                    "backup": backup,
                    "questions": len(merged.get("seen") or {}),
                    "answers": side_size(merged)})

    def log_message(self, fmt, *args):  # silence default stderr access log
        pass


def main():
    ap = argparse.ArgumentParser(description="PCEP LAN sync server (manual WiFi sync)")
    ap.add_argument("--port", type=int, default=8787, help="listen port (default 8787, NEVER 80)")
    ap.add_argument("--host", default="0.0.0.0", help="bind address (0.0.0.0 = whole LAN)")
    args = ap.parse_args()

    log(f"PCEP LAN Sync Server v{APP_VERSION} starting on {args.host}:{args.port}")
    log(f"master: {RECORD_FILE}")
    log(f"backup dir: {BACKUP_DIR} (keeps last {BACKUP_KEEP})")
    log(f"phone app: hit 📶 Sync while on the SAME WiFi as this laptop")
    ensure_seed()
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        log("stopped by user (Ctrl+C)")
        srv.server_close()


if __name__ == "__main__":
    main()
