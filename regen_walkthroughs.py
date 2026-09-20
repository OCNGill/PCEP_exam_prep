"""Regenerate explanations for all 58 execution-verified questions using the
trace engine: real line-by-line arithmetic + verified output + contextual
wrong-option notes (intermediate values referenced when applicable)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trace_engine import run_trace, build_walkthrough, fmt
from validate2 import OVERRIDES, WRAP_PRINT, WRAP_LEN, STATEMENT_QS

HERE = os.path.dirname(os.path.abspath(__file__))

def code_for(qid, raw):
    q = raw["q"]
    if qid in WRAP_PRINT:
        code = WRAP_PRINT[qid]
    elif qid in WRAP_LEN:
        code = "print(len(" + WRAP_LEN[qid] + "))"
    elif qid in OVERRIDES:
        code = OVERRIDES[qid]
    else:
        lines = q.split("\n")
        code = "\n".join(l for l in lines[1:] if l.strip())
    return code

def stdin_for(qid, raw):
    q = raw["q"]
    stdin = ""
    mq = re.search(r"enters?\s+(?:two lines containing\s+)?(.+?)\s+(?:respectively|at the)", q)
    if mq:
        vals = re.findall(r"\d+", mq.group(1))
        stdin = "\n".join(vals) if vals else mq.group(1)
    code = code_for(qid, raw)
    if "input(" in code and not stdin:
        mq2 = re.search(r"enters?\s+(\w+)", q)
        if mq2: stdin = mq2.group(1)
    return stdin

def intermediate_values(steps):
    vals = set()
    for st in steps:
        for v in st["before"].values():
            try:
                if isinstance(v, (int, float, str, tuple)):
                    vals.add(fmt(v))
            except Exception:
                pass
    return vals

def wrong_notes(q, steps, output):
    """Contextual why-wrong for each incorrect option."""
    letters = "ABCDEF"
    inter = intermediate_values(steps)
    out_clean = output.strip() if output and output != "<<TIMEOUT>>" else None
    notes = []
    for i, o in enumerate(q["options"]):
        if i in q["answers"]:
            continue
        ot = o.strip()
        note = None
        # count-word questions
        if out_clean and re.fullmatch(r"[-\d.]+", out_clean):
            try:
                words = {0:"zero",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten"}
                w = words.get(int(float(out_clean)))
                if w and ot.lower() == w:
                    note = f"the trace produced only {out_clean} symbol(s)/element(s)"
            except (ValueError, OverflowError):
                pass
        if note is None and ot in inter and out_clean and ot != out_clean:
            # appears as intermediate value
            step_idx = None
            for idx, st in enumerate(steps):
                for v in st["before"].values():
                    try:
                        if fmt(v) == ot:
                            step_idx = idx
                    except Exception:
                        pass
            if step_idx is not None:
                note = f"this value appears as an INTERMEDIATE state around step {step_idx+1}, but the program keeps running and ends at {out_clean!r}"
        if note is None and out_clean:
            note = f"the executed trace above ends with {out_clean!r} — this is not what the code produces"
        notes.append(f"❌ {letters[i]} — {note or 'does not match the traced execution'}.")
    return notes

def count_summary(q, steps, output):
    """For 'How many …' questions: summarize loop passes and which ones printed."""
    letters = "ABCDEF"
    correct = ", ".join(letters[i] for i in q["answers"])
    printed = [l for l in (output or "").split("\n") if l.strip()]
    n = len(printed)
    sym = printed[0] if printed else "#"
    # find loop-header steps and pass var values
    headers = [st for st in steps if re.match(r"(while|for) ", st["src"])]
    # walk steps sequentially: each header starts a pass; count prints/skips inside
    passes = []  # list of dicts {val, prints, skipped}
    cur = None
    for st in steps:
        src = st["src"]
        if re.match(r"(while|for) ", src):
            m = re.search(r"\b(var|i|c)\b", src)
            cur = {"val": st["before"].get(m.group(1)) if m else None, "prints": 0, "skipped": False}
            passes.append(cur)
        elif cur is not None:
            if src.startswith("print("):
                cur["prints"] += 1
            elif src in ("continue", "break"):
                cur["skipped"] = True
    lines = [f"✅ {correct} — the loop ran {len(passes)} pass(es); here is each pass:"]
    # effective check value: the var AFTER the loop-body update = next header's var
    last_before = steps[-1]["before"] if steps else {}
    mvar = re.search(r"\b(var|i|c)\b", headers[0]["src"]) if headers else None
    var_name = mvar.group(1) if mvar else None
    for i, p in enumerate(passes):
        eff = passes[i + 1]["val"] if i + 1 < len(passes) else last_before.get(var_name)
        tag = f"var {fmt(p['val'])} → becomes {fmt(eff)}"
        if p["prints"]:
            lines.append(f"  • pass {i+1}: {tag} → prints {sym!r}")
        elif p["skipped"]:
            lines.append(f"  • pass {i+1}: {tag} → skipped (continue/break), no print")
        else:
            lines.append(f"  • pass {i+1}: {tag} → no print")
    lines.append(f"  → {sym!r} was printed {n} time(s) total: {' '.join(printed)!r}")
    lines.append(f"  → that's why the answer is {correct} ({NUM.get(n, n)} {sym!r}).")
    return "\n".join(lines), n, sym

NUM = {0:"zero",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten"}

def main():
    raws = {b["id"]: b for b in json.load(open(os.path.join(HERE, "bank_raw.json"), encoding="utf-8"))}
    bank = json.load(open(os.path.join(HERE, "pcep_bank.json"), encoding="utf-8"))
    changed = failed = 0
    for q in bank:
        if q.get("explsrc") != "execution-verified":
            continue
        qid = q["id"]
        raw = raws[qid]
        code = code_for(qid, raw)
        stdin = stdin_for(qid, raw)
        steps, output = run_trace(code, stdin.split("\n") if stdin else [])
        if not steps:
            failed += 1
            continue
        if raw["q"].split("\n")[0].startswith("How many"):
            wt, n, sym = count_summary(q, steps, output)
            letters = "ABCDEF"
            word = NUM.get(n, str(n))
            for i, o in enumerate(q["options"]):
                if i in q["answers"]:
                    continue
                if o.strip().lower() == word:
                    wt += f"\n❌ {letters[i]} — tempting: that's the count of loop PASSES, not of printed symbols. The loop ran {len([s for s in steps if re.match(r'(while|for) ', s['src'])])} times but printed only {n}."
                else:
                    wt += f"\n❌ {letters[i]} — the trace printed exactly {n} {sym!r}; count them in the pass list above."
        else:
            wt = build_walkthrough(q, steps, output)
            for note in wrong_notes(q, steps, output):
                wt += "\n" + note
        q["expl"] = wt
        changed += 1
    json.dump(bank, open(os.path.join(HERE, "pcep_bank.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(f"regenerated {changed} walkthroughs, {failed} trace failures")

if __name__ == "__main__":
    main()
