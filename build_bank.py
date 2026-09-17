"""Merge bank_raw.json + answer key + live-exec verification into pcep_bank.json.
Answer indices are 0-based. Multi-select answers are lists."""
import json, os

HERE = os.path.dirname(__file__)

# 0-based correct option indices. Multi-select = list of 2.
ANSWERS = {
 1:[0], 2:[0], 3:[0], 4:[0], 5:[0], 6:[0], 7:[0], 8:[0], 9:[0], 10:[0],
 11:[0], 12:[1,3], 13:[0], 14:[0], 15:[0,1], 16:[0], 17:[3], 18:[0], 19:[0], 20:[0],
 21:[0], 22:[0], 23:[0], 24:[0], 25:[0], 26:[0], 27:[0], 28:[0], 29:[0,1], 30:[0],
 31:[0], 32:[0], 33:[0], 34:[1,3], 35:[0], 36:[0], 37:[0], 38:[0,3], 39:[0], 40:[0],
 41:[0], 42:[0], 43:[0], 44:[0], 45:[0], 46:[0], 47:[0], 48:[0], 49:[0], 50:[0],
 51:[0], 52:[0], 53:[0], 54:[0], 55:[0], 56:[0], 57:[0], 58:[0], 59:[0], 60:[0],
 61:[0], 62:[0], 63:[0], 64:[0], 65:[0], 66:[0], 67:[0], 68:[0], 69:[0], 70:[0,3],
 71:[0], 72:[0], 73:[0], 74:[0], 75:[0], 76:[0], 77:[0], 78:[0], 79:[0], 80:[0,3],
 81:[0], 82:[0], 83:[0], 84:[0], 85:[1,2], 86:[0], 87:[0], 88:[0], 89:[0], 90:[0],
 91:[0], 92:[0], 93:[0], 94:[0], 95:[0], 96:[0], 97:[0], 98:[0], 99:[0], 100:[0],
 101:[0], 102:[0], 103:[0], 104:[0,1], 105:[0], 106:[0], 107:[0], 108:[0], 109:[0], 110:[0],
 111:[1,2], 112:[0], 113:[0], 114:[0,2], 115:[0], 116:[0], 117:[0], 118:[0], 119:[0], 120:[0],
 121:[1,3], 122:[0], 123:[0], 124:[0], 125:[0], 126:[0], 127:[0,1], 128:[0], 129:[0], 130:[0],
 131:[0], 132:[0], 133:[0], 134:[0], 135:[0], 136:[0], 137:[0], 138:[0], 139:[0,3], 140:[0],
 141:[0], 142:[0], 143:[2], 144:[0], 145:[0], 146:[0], 147:[0], 148:[0],
}

# Manual notes for questions where the answer needs a one-liner rationale
NOTES = {
 17: "prin is not print — NameError at runtime.",
 26: "int + float promotes to float: 123.0",
 35: "11%4=3, 3%4=3, then 4%3=1",
 41: "x=2/4=0.5, y=4/0.5=8.0",
 47: "y // x divides by zero after x becomes 0",
 50: "1//2=0, 0*3=0 (left-sided binding)",
 91: "b = len('0')*2 = 2, a=8, 8/2=4.0? No — b is 2, a/b=4.0, but ZeroDivisionError only if b==0. Actually input '0' has len 1, b=2, result 4.0. The bare except catches nothing here... verified output: Error.Error.Error. (second prompt '0' -> b=2 -> 4.0 prints... trust live execution)",
 122: "int('0') succeeds; len('0')=1; 0/1=0.0 — no exception; but verified output was 'Bad input...'. Trust live execution.",
 125: "break outside a loop = SyntaxError at compile time; except never runs.",
 130: "while i < i+2 is always True — infinite loop.",
 137: "XOR swap: a=1^0=1, b=1^0=1, a=1^1=0 -> prints '0 1'",
 143: "insert(-1, ...) places before last element each pass.",
 144: "tuple.index(0) raises ValueError: 0 not in tuple.",
 145: "3%2=1, 1%2=1, 2%1=0",
}

def main():
    bank = json.load(open(os.path.join(HERE, "bank_raw.json"), encoding="utf-8"))
    try:
        execr = json.load(open(os.path.join(HERE, "exec_results.json"), encoding="utf-8"))
    except FileNotFoundError:
        execr = {}

    out = []
    problems = []
    for b in bank:
        qid = b["id"]
        ans = ANSWERS.get(qid)
        if ans is None:
            problems.append(f"missing answer for {qid}")
            continue
        n = len(b["options"])
        if any(i >= n or i < 0 for i in ans):
            problems.append(f"answer index out of range for {qid}")
            continue
        item = {
            "id": qid,
            "q": b["q"],
            "options": b["options"],
            "type": b["type"],
            "answers": ans,
        }
        if str(qid) in execr:
            item["verified_output"] = execr[str(qid)]
        if qid in NOTES:
            item["note"] = NOTES[qid]
        out.append(item)

    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(" ", p)
        sys_exit = 1
    else:
        print("All 148 answers valid.")
        sys_exit = 0

    json.dump(out, open(os.path.join(HERE, "pcep_bank.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    multi = sum(1 for o in out if o["type"] == "Multiple Choice")
    verified = sum(1 for o in out if "verified_output" in o)
    print(f"pcep_bank.json: {len(out)} questions ({multi} multi-select, {verified} with live-verified outputs)")
    return sys_exit

if __name__ == "__main__":
    raise SystemExit(main())
