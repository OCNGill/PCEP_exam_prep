"""Local-inference answer-key cross-check for PCEP bank.

Usage: python local_verify.py <host_ip> <batch_start> <batch_count>
Sends conceptual (non-code) single-choice questions to a llama-server
/v1/chat/completions endpoint, has the local model answer independently,
and compares against the Hermes-derived key.
"""
import json
import sys
import time
import urllib.request

HOST = sys.argv[1] if len(sys.argv) > 1 else "10.0.0.42"
START = int(sys.argv[2]) if len(sys.argv) > 2 else 0
COUNT = int(sys.argv[3]) if len(sys.argv) > 3 else 6

CODE_MARKERS = ("print(", "def ", ">>>", "```", "==", "= ", " f'", 'f"',
                "[", "{", "%", "\\", "range(")


def load_conceptual():
    bank = json.load(open("pcep_bank.json", encoding="utf-8"))
    picks = []
    for item in bank:
        if item.get("type") != "Single Choice":
            continue
        qtext = item.get("q", "")
        if any(m in qtext for m in CODE_MARKERS):
            continue
        if len(item.get("options", [])) > 4:
            continue
        picks.append(item)
    return bank, picks


def ask_local(ip, q, options):
    letters = "ABCDE"
    opts = "\n".join(f"{letters[i]}) {o}" for i, o in enumerate(options))
    payload = {
        "model": "local",
        "temperature": 0,
        "max_tokens": 8,
        "messages": [
            {"role": "system",
             "content": ("You are a precise Python certification exam taker. "
                         "Answer with ONLY the letter of the correct option "
                         "(A, B, C, or D) and nothing else.")},
            {"role": "user",
             "content": f"Question: {q}\n\n{opts}\n\nAnswer letter:"},
        ],
    }
    req = urllib.request.Request(
        f"http://{ip}:8080/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


def main():
    bank, picks = load_conceptual()
    batch = picks[START:START + COUNT]
    print(f"Endpoint: http://{HOST}:8080  |  batch {START}..{START + len(batch) - 1} "
          f"of {len(picks)} conceptual questions")
    match = 0
    rows = []
    t_all = time.time()
    for item in batch:
        truth = item["answers"][0]
        t0 = time.time()
        try:
            raw = ask_local(HOST, item["q"], item["options"])
            letter = next((c for c in raw.upper()[:3] if c in "ABCD"), None)
            local_idx = "ABCD".find(letter) if letter else -1
            ok = (local_idx == truth)
        except Exception as exc:
            raw, letter, ok = f"ERROR: {exc}", "-", False
            local_idx = -1
        dt = time.time() - t0
        match += int(ok)
        short_q = (item["q"][:52] + "...") if len(item["q"]) > 55 else item["q"]
        rows.append((item["id"], short_q, "ABCD"[truth] if 0 <= truth < 4 else "?",
                     letter or "-", "PASS" if ok else "FAIL", f"{dt:.1f}s"))
    total_dt = time.time() - t_all
    print(f"{'ID':>4} | {'question':<55} | key | loc | res  | time")
    for r in rows:
        print(f"{r[0]:>4} | {r[1]:<55} | {r[2]:>3} | {r[3]:>3} | {r[4]:<4} | {r[5]}")
    print(f"\nAGREEMENT: {match}/{len(batch)} "
          f"({100 * match / max(len(batch), 1):.0f}%)  |  wall: {total_dt:.1f}s")
    mismatches = [(r[0], r[1]) for r in rows if r[4] == "FAIL"]
    if mismatches:
        print("REVIEW QUEUE (disagreements for human/zero-trust pass):")
        for mid, mq in mismatches:
            print(f"  Q{mid}: {mq}")


if __name__ == "__main__":
    main()
