"""SECONDARY VALIDATION PASS - independent of build_bank.py's key.

Method:
 1. Re-execute every code snippet from bank_raw.json in a fresh subprocess.
 2. Auto-match the verified output against option text (incl. word-numbers
    and expression re-evaluation with print-wrapping).
 3. Compare exec-derived answer vs the keyed answer in pcep_bank.json.
 4. Duplicate-consistency: questions that are semantically identical must
    carry identical answers.
Reports CONFIRMED / MISMATCH / MANUAL buckets.
"""
import json, re, subprocess, sys, os

HERE = os.path.dirname(__file__)
BANK = os.path.join(HERE, "bank_raw.json")
KEYED = os.path.join(HERE, "pcep_bank.json")

# expression-only snippets that need print-wrapping or len() evaluation
WRAP_PRINT = {26: "123 + 0.0", 43: "1 / 1", 50: "1 // 2 * 3", 54: "z = 10\ny = 0\nx = z > y or z == y",
              67: "z = 10\ny = 0\nx = y < z and z > y or y > z and z < y",
              76: "x = 1\nx = x == x", 120: "1 // 2", 129: "1 // 5 + 1 / 5", 142: "z = 0\ny = 10\nx = y < z and z > y or y > z and z < y"}
WRAP_LEN = {59: "[0 for i in range(1, 3)]", 71: "[i for i in range(-1, 2)]", 124: "[i for i in range(-1, -2)]"}
# snippet questions whose answer is a statement about the code, not its output
STATEMENT_QS = {28, 56, 57, 58, 66, 70, 79, 80, 114, 127, 141}
OVERRIDES = {
 11: 'print("Hello!")', 17: 'prin("Goodbye!")',
 91: 'try:\n    first_prompt = input("Enter the first value: ")\n    a = len(first_prompt)\n    second_prompt = input("Enter the second value: ")\n    b = len(second_prompt) * 2\n    print(a/b)\nexcept ZeroDivisionError:\n    print("Do not divide by zero!")\nexcept ValueError:\n    print("Wrong value.")\nexcept:\n    print("Error.Error.Error.")',
 92: 'value = input("Enter a value: ")\nprint(10/value)',
 94: 'try:\n    value = input("Enter a value: ")\n    print(value/value)\nexcept ValueError:\n    print("Bad input...")\nexcept ZeroDivisionError:\n    print("Very bad input...")\nexcept TypeError:\n    print("Very very bad input...")\nexcept:\n    print("Booo!")',
 122: 'try:\n    value = input("Enter a value: ")\n    print(int(value)/len(value))\nexcept ValueError:\n    print("Bad input...")\nexcept ZeroDivisionError:\n    print("Very bad input...")\nexcept TypeError:\n    print("Very very bad input...")\nexcept:\n    print("Booo!")',
 125: 'try:\n    print(5/0)\n    break\nexcept:\n    print("Sorry, something went wrong...")\nexcept (ValueError, ZeroDivisionError):\n    print("Too bad...")',
 144: 'foo = (1, 2, 3)\nfoo.index(0)',
 98: "my_list = ['Mary', 'had', 'a', 'little', 'lamb']\ndef my_list(my_list):\n    del my_list[3]\n    my_list[3] = 'ram'\nprint(my_list(my_list))",
}
WORDS = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}

DUP_GROUPS = [[6, 16], [22, 135], [51, 128], [113, 148]]

RUNNER = r'''
import sys, io, os
code = sys.stdin.read()
stdin_data = os.environ.get("SNIPPET_STDIN", "")
old = sys.stdin, sys.stdout
try:
    buf = io.StringIO()
    sys.stdin = io.StringIO(stdin_data + "\n")
    sys.stdout = buf
    exec(compile(code, "snippet", "exec"), {})
    out = buf.getvalue()
except Exception as e:
    out = "<<EXC %s>>" % type(e).__name__
finally:
    sys.stdin, sys.stdout = old
print("===RESULT===")
print(out.strip())
'''

def run_snippet(code, stdin, timeout=5):
    tmp = os.path.join(HERE, "_runner2_tmp.py")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(RUNNER)
    env = dict(os.environ); env["SNIPPET_STDIN"] = stdin; env["PYTHONIOENCODING"] = "utf-8"
    try:
        p = subprocess.run([sys.executable, tmp], input=code, capture_output=True,
                           text=True, timeout=timeout, env=env, encoding="utf-8")
        if "===RESULT===" in p.stdout:
            return p.stdout.split("===RESULT===")[1].strip()
        return "<<EXC UNKNOWN>>"
    except subprocess.TimeoutExpired:
        return "<<TIMEOUT>>"

def norm(s):
    return re.sub(r"[^a-z0-9.\[\] ]", "", s.lower()).strip()

def match_option(output, options):
    """Return index of the single option matching the output, else None."""
    if not output or output.startswith("<<"):
        return None
    outn = norm(output.replace("\n", " "))
    # direct text match
    hits = [i for i, o in enumerate(options) if norm(o) == outn]
    if len(hits) == 1:
        return hits[0]
    # containment match: output embedded in option phrase ("is equal to 123.0")
    if len(outn) >= 2:
        hits = [i for i, o in enumerate(options) if outn in norm(o)]
        if len(hits) == 1:
            return hits[0]
    # count questions: output is N repeated symbols -> word number
    lines = [l for l in output.split("\n") if l.strip()]
    if lines and len(set(lines)) == 1 and not re.search(r"[A-Za-z0-9]", lines[0]):
        w = WORDS.get(len(lines))
        if w:
            hits = [i for i, o in enumerate(options) if o.strip().lower() == w]
            if len(hits) == 1:
                return hits[0]
    # numeric output vs numeric or word-number option
    m = re.fullmatch(r"[-\d.]+", output.strip())
    if m:
        hits = [i for i, o in enumerate(options) if o.strip().rstrip(".") == output.strip().rstrip(".")]
        if len(hits) == 1:
            return hits[0]
        try:
            w = WORDS.get(int(output.strip()))
        except ValueError:
            w = None
        if w:
            hits = [i for i, o in enumerate(options) if o.strip().lower() == w]
            if len(hits) == 1:
                return hits[0]
    return None

def main():
    bank = {b["id"]: b for b in json.load(open(BANK, encoding="utf-8"))}
    keyed = {q["id"]: q for q in json.load(open(KEYED, encoding="utf-8"))}
    confirmed, mismatch, manual = [], [], []
    exec_ans = {}

    for qid, b in bank.items():
        q = b["q"]
        if qid in WRAP_PRINT:
            code, wrap = WRAP_PRINT[qid], True
        elif qid in WRAP_LEN:
            code, wrap = WRAP_LEN[qid], True
        elif qid in OVERRIDES:
            code, wrap = OVERRIDES[qid], False
        elif qid in STATEMENT_QS:
            manual.append((qid, "answer is a statement about the code, not its output"))
            continue
        else:
            lines = q.split("\n")
            code = "\n".join(l for l in lines[1:] if l.strip())
            wrap = False
        if not code.strip():
            manual.append((qid, "no code to execute"))
            continue
        stdin = ""
        mq = re.search(r"enters?\s+(?:two lines containing\s+)?(.+?)\s+(?:respectively|at the)", q)
        if mq:
            vals = re.findall(r"\d+", mq.group(1))
            stdin = "\n".join(vals) if vals else mq.group(1)
        if "input(" in code and not stdin:
            mq2 = re.search(r"enters?\s+(\w+)", q)
            if mq2: stdin = mq2.group(1)
        if wrap and "print" not in code:
            if qid in WRAP_LEN:
                code = "print(len(" + code + "))"
            elif "\n" not in code:
                code = "print(" + code + ")"
            elif re.search(r"^\s*x\s*=", code, re.M):
                code = code + "\nprint(x)"
        out = run_snippet(code, stdin)
        idx = match_option(out, b["options"])
        if idx is None:
            manual.append((qid, f"output not auto-matchable: {out[:60]!r}"))
        else:
            exec_ans[qid] = idx
            if idx in keyed[qid]["answers"]:
                confirmed.append(qid)
            else:
                mismatch.append((qid, keyed[qid]["answers"], idx, out[:60]))

    # duplicate consistency
    dup_bad = []
    for grp in DUP_GROUPS:
        answers = [tuple(keyed[i]["answers"]) for i in grp]
        if len(set(answers)) != 1:
            dup_bad.append((grp, answers))

    # multi-select structural check
    multi_bad = [qid for qid, q in keyed.items()
                 if q["type"] == "Multiple Choice" and len(q["answers"]) != 2]

    print(f"CONFIRMED by independent execution: {len(confirmed)}")
    print(f"MISMATCH: {len(mismatch)}")
    for m in mismatch: print("   !!", m)
    print(f"MANUAL-REVIEW bucket: {len(manual)}")
    for m in manual: print("   -", m)
    print(f"Duplicate-group inconsistencies: {dup_bad or 'none'}")
    print(f"Multi-select structural violations: {multi_bad or 'none'}")
    json.dump(exec_ans, open(os.path.join(HERE, "exec_answers_pass2.json"), "w"), indent=1)
    return 1 if mismatch or dup_bad or multi_bad else 0

if __name__ == "__main__":
    raise SystemExit(main())
