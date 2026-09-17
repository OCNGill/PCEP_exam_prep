"""PCEP answer-key verifier: executes every code snippet in the bank in an
isolated subprocess (timeout-guarded) and records real output per question."""
import json, re, subprocess, sys, os

BANK = os.path.join(os.path.dirname(__file__), "bank_raw.json")

override = {
 11: ('print("Hello!")', ''),
 17: ('prin("Goodbye!")', ''),
 104: ('', ''),
 109: ("dictionary = {}\nmy_list = ['a', 'b', 'c', 'd']\nfor i in range(len(my_list) - 1):\n    dictionary[my_list[i]] = (my_list[i], )\nfor i in sorted(dictionary.keys()):\n    k = dictionary[i]\n    print(k[0])", ''),
 92: ('value = input("Enter a value: ")\nprint(10/value)', '0'),
 91: ('try:\n    first_prompt = input("Enter the first value: ")\n    a = len(first_prompt)\n    second_prompt = input("Enter the second value: ")\n    b = len(second_prompt) * 2\n    print(a/b)\nexcept ZeroDivisionError:\n    print("Do not divide by zero!")\nexcept ValueError:\n    print("Wrong value.")\nexcept:\n    print("Error.Error.Error.")', 'kangaroo\n0'),
 94: ('try:\n    value = input("Enter a value: ")\n    print(value/value)\nexcept ValueError:\n    print("Bad input...")\nexcept ZeroDivisionError:\n    print("Very bad input...")\nexcept TypeError:\n    print("Very very bad input...")\nexcept:\n    print("Booo!")', 'x'),
 122: ('try:\n    value = input("Enter a value: ")\n    print(int(value)/len(value))\nexcept ValueError:\n    print("Bad input...")\nexcept ZeroDivisionError:\n    print("Very bad input...")\nexcept TypeError:\n    print("Very very bad input...")\nexcept:\n    print("Booo!")', '0'),
 125: ('try:\n    print(5/0)\n    break\nexcept:\n    print("Sorry, something went wrong...")\nexcept (ValueError, ZeroDivisionError):\n    print("Too bad...")', ''),
 144: ('foo = (1, 2, 3)\nfoo.index(0)', ''),
 98: ("my_list = ['Mary', 'had', 'a', 'little', 'lamb']\ndef my_list(my_list):\n    del my_list[3]\n    my_list[3] = 'ram'\nprint(my_list(my_list))", ''),
 116: ('', ''),
}

RUNNER = r'''
import sys, io
code = sys.stdin.read()
import os
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
    tmp = os.path.join(os.path.dirname(__file__), "_runner_tmp.py")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(RUNNER)
    env = dict(os.environ)
    env["SNIPPET_STDIN"] = stdin
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        p = subprocess.run([sys.executable, tmp], input=code, capture_output=True,
                           text=True, timeout=timeout, env=env, encoding="utf-8")
        if "===RESULT===" in p.stdout:
            return p.stdout.split("===RESULT===")[1].strip()
        return f"<<EXC {p.stderr.strip().splitlines()[-1][:60] if p.stderr.strip() else 'UNKNOWN'}>>"
    except subprocess.TimeoutExpired:
        return "<<TIMEOUT (infinite loop)>>"

def main():
    bank = json.load(open(BANK, encoding="utf-8"))
    results = {}
    for b in bank:
        qid = b["id"]
        q = b["q"]
        if qid in override:
            code, stdin = override[qid]
        else:
            lines = q.split("\n")
            code = "\n".join(l for l in lines[1:] if l.strip())
        if not code.strip():
            continue
        stdin = ""
        mq = re.search(r"enters?\s+(?:two lines containing\s+)?(.+?)\s+(?:respectively|at the)", q)
        if mq:
            vals = re.findall(r"\d+", mq.group(1))
            if not vals:
                vals = [mq.group(1)]
            stdin = "\n".join(vals)
        if "input(" in code and not stdin:
            mq2 = re.search(r"enters?\s+(\w+)", q)
            if mq2:
                stdin = mq2.group(1)
        results[str(qid)] = run_snippet(code, stdin)
    json.dump(results, open(os.path.join(os.path.dirname(__file__), "exec_results.json"), "w"), indent=1)
    for qid in sorted(results, key=int):
        print(f"[{qid:>3s}] {results[qid][:90]}")

if __name__ == "__main__":
    main()
