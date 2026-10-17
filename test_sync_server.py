"""Unit tests for pcep_sync_server — merge semantics + backup-of-record logic.
Offline, no sockets: exercises the exact functions the HTTP handler calls.
Run: python test_sync_server.py
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pcep_sync_server as srv  # noqa: E402

FAILED = []


def check(name, cond):
    print(("PASS - " if cond else "FAIL - ") + name)
    if not cond:
        FAILED.append(name)


# Redirect all storage into a temp dir (never touch a live record)
tmp = Path(tempfile.mkdtemp(prefix="pcep_sync_test_"))
srv.RECORD_FILE = tmp / "master.json"
srv.BACKUP_DIR = tmp / "backups"
srv.LOG_FILE = tmp / "sync.log"

# 1) merge: per-question HIGHEST count wins (whichever device is behind gets added to)
m = srv.merge_stats({"seen": {"a": 1, "b": 3}}, {"seen": {"a": 5, "c": 1}})
check("merge: per-question max wins", m["seen"] == {"a": 5, "b": 3, "c": 1})

# 2) merge: history + log concatenated then de-duplicated, nothing lost
m = srv.merge_stats(
    {"history": [{"r": 1}], "log": [{"q": 1}]},
    {"history": [{"r": 1}, {"r": 2}], "log": [{"q": 1}, {"q": 2}]},
)
check("merge: history/log deduped", len(m["history"]) == 2 and len(m["log"]) == 2)

# 3) merge: correct/wrong/flagged counters also take the max side
m = srv.merge_stats(
    {"correct": {"a": 2}, "wrong": {"b": 4}, "flagged": {"c": 1}},
    {"correct": {"a": 5}, "wrong": {"b": 1}, "flagged": {"c": 3}},
)
check("merge: counters max per side",
      m["correct"]["a"] == 5 and m["wrong"]["b"] == 4 and m["flagged"]["c"] == 3)

# 4) save/load roundtrip
A = {"seen": {"x": 2}, "correct": {"x": 2}, "wrong": {}, "flagged": {}, "history": [], "log": []}
srv.save_record(A)
check("save/load roundtrip", srv.load_record()["seen"] == {"x": 2})

# 5) BACKUP captures the PREVIOUS record BEFORE overwrite (the Commander rule)
bf = srv.backup_record()
check("backup file returned", bf is not None)
assert bf is not None, "backup_record() returned None — record rule broken"
bobj = json.loads((srv.BACKUP_DIR / bf).read_text(encoding="utf-8"))
check("backup holds PRE-state (a=2 kept)", bobj["seen"] == {"x": 2})
srv.save_record({"seen": {"x": 99}, "correct": {}, "wrong": {}, "flagged": {}, "history": [], "log": []})
bobj2 = json.loads((srv.BACKUP_DIR / bf).read_text(encoding="utf-8"))
check("backup NOT clobbered by later write", bobj2["seen"] == {"x": 2})

# 6) rotation keeps exactly BACKUP_KEEP (10)
for i in range(13):
    srv.save_record({"seen": {"n": i}, "correct": {}, "wrong": {}, "flagged": {}, "history": [], "log": []})
    srv.backup_record()
n = len(list(srv.BACKUP_DIR.glob("pcep_stats_backup_*.json")))
check(f"backup rotation keeps 10 (got {n})", n == srv.BACKUP_KEEP)

# 7) first-sync path: no master yet -> backup returns None, never crashes
srv.RECORD_FILE = tmp / "fresh" / "never.json"
srv.BACKUP_DIR = tmp / "fresh" / "bk"
check("first sync: no master -> no backup, no crash", srv.backup_record() is None)

# 8) side_size (direction math used in the sync log)
check("side_size sums answers", srv.side_size({"seen": {"a": 5, "b": 3}}) == 8)

# 9) junk input tolerated (merge never raises on missing fields)
m = srv.merge_stats({}, {"seen": None, "history": "not-a-list"})
check("merge tolerates missing/garbage fields", m["seen"] == {} and m["history"] == [])

print(("ALL SYNC SERVER TESTS PASSED" if not FAILED else f"{len(FAILED)} FAILED: {FAILED}"))
sys.exit(1 if FAILED else 0)
