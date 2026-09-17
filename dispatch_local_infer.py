"""Dispatch PCEP explanation subtasks to HTPC + Deck local inference. Fleet op 2026-09-16."""
import json, urllib.request, urllib.error, time, sys

BANK = r"C:\Users\Gillsystems Laptop\source\repos\OCNGill\PCEP_exam_prep\pcep_bank.json"
HTPC = "http://10.0.0.42:8080"
DECK = "http://10.0.0.139:8080"

def health(base, tries=10, wait=6):
    for i in range(tries):
        try:
            with urllib.request.urlopen(base + "/health", timeout=5) as r:
                if json.loads(r.read()).get("status") == "ok":
                    return True
        except Exception:
            time.sleep(wait)
    return False

def pick(qs, ids):
    out = []
    for q in qs:
        if q["id"] in ids:
            letters = "ABCDEF"
            correct = [letters[a] for a in q["answers"]]
            out.append({"id": q["id"], "q": q["q"], "options": q["options"], "correct": correct})
    return out

def build_prompt(batch):
    lines = ["You are a PCEP (Certified Entry-Level Python Programmer) study assistant.",
             "For each question below, write: (1) a 2-3 sentence explanation of why the correct answer is correct,",
             "(2) one short line per wrong option explaining why it is wrong.",
             "Be precise, exam-level, no fluff. Format as plain text under 'Q<id>:' headers.", ""]
    for b in batch:
        lines.append(f"Q{b['id']}: {b['q']}")
        for i, o in enumerate(b["options"]):
            lines.append(f"  {'ABCDEF'[i]}) {o}")
        lines.append(f"  Correct: {', '.join(b['correct'])}")
        lines.append("")
    return "\n".join(lines)

def infer(base, prompt, max_tokens=1200):
    payload = {"model": "qwen3.5-9b-it", "temperature": 0.2,
               "max_tokens": max_tokens,
               "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(base + "/v1/chat/completions",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.loads(r.read())
    txt = data["choices"][0]["message"]["content"]
    if data["choices"][0]["message"].get("reasoning_content"):
        txt = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return txt, time.time() - t0, usage

def main():
    bank = json.load(open(BANK, encoding="utf-8"))
    qs = bank["questions"] if isinstance(bank, dict) else bank
    htpc_batch = pick(qs, {1, 2, 3, 4, 5})
    deck_batch = pick(qs, {6, 7, 8, 9, 10})
    results = {}
    for name, base, batch in (("HTPC", HTPC, htpc_batch), ("DECK", DECK, deck_batch)):
        print(f"== {name} ==")
        if not health(base):
            print(f"{name}: server not healthy after retries"); continue
        try:
            txt, dt, usage = infer(base, build_prompt(batch))
            print(f"{name} OK {dt:.1f}s  tokens={usage}")
            out = rf"C:\Users\Gillsystems Laptop\source\repos\OCNGill\PCEP_exam_prep\local_infer_{name.lower()}.txt"
            with open(out, "w", encoding="utf-8") as f:
                f.write(f"# {name} subtask output (PCEP explanations)\n\n{txt}")
            print(txt[:800])
        except Exception as e:
            print(f"{name} FAIL: {e}")

if __name__ == "__main__":
    main()
