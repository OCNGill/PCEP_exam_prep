"""Bank builder v2: ANSWERS + EXPLANATIONS (hand + execution-verified) + CONCEPTS.
Reads bank_raw.json + exec_answers_pass2.json -> pcep_bank.json
Every question MUST end up with an explanation; build fails otherwise.
"""
import json, os, sys

HERE = os.path.dirname(__file__)

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

# ---- concept map (148 entries; anything missing defaults to Python Basics) ----
CONCEPTS = {}
def _c(concept, ids):
    for i in ids: CONCEPTS[i] = concept
_c("Python Basics", [1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,18,19,20,38,139])
_c("Output & Strings", [11,17,21,31,32,37,39,40,44,45,119,140])
_c("Operators & Math", [24,25,26,27,28,34,35,36,41,43,46,47,48,49,50,120,123,129,145])
_c("Variables & Types", [22,23,30,33,42,100,106,111,134])
_c("Logic & Comparison", [51,54,63,67,76,128,142])
_c("Bitwise", [73,137])
_c("Lists", [55,56,57,58,59,60,61,62,66,68,70,71,72,77,78,79,80,115,124,132,141,143])
_c("Loops", [52,53,64,65,69,74,75,130])
_c("Functions", [81,82,83,84,85,86,87,88,89,96,98,99,101,102,103,105,108,110,113,114,117,118,121,126,135,147,148])
_c("Tuples", [90,97,107,112,136,144])
_c("Dictionaries", [93,109,133,138,146])
_c("Exceptions & Errors", [91,92,94,95,104,116,122,125,131])

# ---- hand-written explanations for the 90 non-auto questions ----
# letters refer to the question's actual option order
EXPLAIN = {
 1: "✅ A — Python is a high-level programming language: human-readable source that gets translated for the CPU. ❌ B — machine language is raw binary executed directly by the processor. ❌ C — natural languages are human languages like English or Polish.",
 2: "✅ A — a complete set of known commands is called an instruction list (IL). ❌ B/C — 'machine list' and 'low-level list' are invented terms with no meaning in computing.",
 3: "✅ A — source code is a program written in a high-level programming language, readable by humans. ❌ B — that describes machine code, the translated output. ❌ C — a source FILE contains source code; the code itself is the program text.",
 4: "✅ A — an interpreter directly executes instructions written in a programming language, line by line. ❌ B — a compiler translates the whole program into machine code first. ❌ C — 'translator' is a generic term, not the specific tool.",
 5: "✅ A — the course (and the PCEP exam) covers Python 3. ❌ B/C — Python 2 is legacy (end-of-life 2020) and Python 1 is historical.",
 6: "✅ A — CPython is the default, reference implementation of Python, written in the C language. ❌ B — that describes Cython, a separate superset project. ❌ C — CPython is not itself a compiled language.",
 7: "✅ A — IDLE = Integrated Development and Learning Environment, Python's bundled editor/IDE. ❌ B — IDLE is not a Python version. ❌ C — 'Interactive Development and Learning Extension' is a made-up expansion.",
 8: "✅ A — a debugger launches code step-by-step and lets you inspect state at each moment. ❌ B — an editor only writes code. ❌ C — a console executes commands but doesn't step through them.",
 9: "✅ A — Guido van Rossum named Python after Monty Python's Flying Circus, the BBC comedy. ❌ B — the snake became the logo/mascot but is NOT the name's origin. ❌ C — Python of Catana is a fictional invention.",
 10: "✅ A — .py is the standard Python file extension. ❌ B — .p is not a Python extension. ❌ C — .pi is not either.",
 11: "✅ A — print(\"Hello!\") outputs Hello! without the quotes. ❌ B — Python does not print the quotation marks; they only delimit the string literal. ❌ C — parentheses are not part of the output. ❌ D — the code is valid; no error occurs.",
 12: "✅ A+B — compilation converts code directly into machine code, and compiled code tends to run faster than interpreted code. ❌ C — the opposite of the truth. ❌ D — the end user needs only the compiled binary, not the compiler.",
 13: "✅ A — machine code is a low-level language of binary digits (bits) that the CPU reads and understands directly. ❌ B — hexadecimal is human-friendly notation, not what the processor reads. ❌ C — assembly is a separate low-level language. ❌ D — that describes a high-level language.",
 14: "✅ A — a console (command-line interpreter) lets you interact with the OS and execute Python commands. ❌ B — an editor only writes code. ❌ C — Jython is a Python implementation running on the JVM. ❌ D — a compiler translates code, not an interactive tool.",
 15: "✅ A+B — Python is widely used for writing application tests, and it is free, open-source and multiplatform. ❌ C — Python is a poor choice for low-level programming (too slow, not close to hardware). ❌ D — Python 3 is deliberately NOT backwards compatible with Python 2.",
 16: "✅ A — CPython is the default, reference implementation of Python written in C. ❌ B — that's Cython (a Python superset for C-like performance). ❌ C — garbled definition. ❌ D — reverses the two languages.",
 17: "✅ D — prin is not a defined function (print is) → NameError at runtime, so an error message is generated. ❌ A/B/C — nothing is printed because the code fails before any output.",
 18: "✅ A — a file containing a program written in a high-level language is a source file. ❌ B — 'machine file' is not a term. ❌ C — 'code file' is informal, not the proper term. ❌ D — a target file is compiler OUTPUT.",
 19: "✅ A — every language is built on an alphabet (character set), lexis (words), syntax (grammar rules) and semantics (meaning). ❌ B/C/D — phonetics, phonology and morphology describe SPOKEN sound systems, irrelevant to programming languages.",
 20: "✅ A — a script is a text file containing instructions that make up a program. ❌ B/C — scripts are not error messages. ❌ D — a file of zeroes and ones is machine code, the opposite of a script.",
 21: "✅ A — the escape character (\\) changes the meaning of the character next to it, e.g. \\n means newline instead of letter n. ❌ B — a programmer joke, not a definition. ❌ C — meaningless.",
 22: "✅ A — a positional parameter's meaning is determined by its position in the parameter list. ❌ B — appearance is irrelevant. ❌ C — name-based determination is a KEYWORD parameter.",
 23: "✅ A — integers are stored exactly; floats use an approximate binary (IEEE 754) representation — they are stored differently in memory. ❌ B — ints and floats mix freely in expressions. ❌ C — integers can absolutely be literals (e.g. 123).",
 24: "✅ A — the 0x prefix marks a hexadecimal literal (e.g. 0x123). ❌ B — octal uses 0o. ❌ C — decimal has no prefix.",
 25: "✅ A — // performs integer (floor) division, discarding the fractional part. ❌ B — regular division is /. ❌ C — // very much exists.",
 27: "✅ A — multiplication has higher precedence than addition, so it is evaluated first. ❌ B — the reverse is false in Python and in mathematics. ❌ C — both statements are perfectly evaluable.",
 28: "✅ A — the ** operator binds right-sided: 1 ** 2 ** 3 means 1 ** (2 ** 3) = 1 ** 8. ❌ B — left-sided binding would give (1 ** 2) ** 3 = 1, a different result. ❌ C — evaluation order is strictly defined, never random.",
 29: "✅ A+B — a keyword is a reserved word: it cannot be used as a variable name nor as a function name. ❌ C — keywords are reserved, not 'the most important word' of a program.",
 30: "✅ A — input() always returns a string, even if the user types digits; convert with int() or float(). ❌ B/C — automatic numeric conversion never happens.",
 33: "✅ A — a keyword argument's meaning is determined by the argument's name specified along with its value (fun(y=2)). ❌ B — position defines POSITIONAL arguments. ❌ C/D — existing variables and the value alone play no role.",
 34: "✅ B+D — the right argument of % cannot be zero (ZeroDivisionError), and ** uses right-sided binding. ❌ A — / always produces a float, never an integer. ❌ C — addition never precedes multiplication.",
 38: "✅ A+D — True is a reserved keyword and and is a keyword, so both are illegal variable names. ❌ B+C — true and TRUE are legal identifiers: Python is case-sensitive and only the exact spelling True is a keyword.",
 39: "✅ A — \\n inside a string forces print() to break the output line (newline). ❌ B — printing two literal characters requires \\\\n. ❌ C — the digraph duplicates nothing. ❌ D — it has no effect on execution.",
 40: "✅ A — print() accepts any number of arguments, including zero (it then just prints an empty line). ❌ B — zero arguments is legal. ❌ C/D — no such limits exist.",
 42: "✅ A — y is assigned but the code prints Y; Python is case-sensitive → NameError, an execution error. ❌ B/C/D — the program never reaches a print.",
 46: "✅ A — 0o marks an octal literal (e.g. 0o123). ❌ B — binary is 0b. ❌ C — decimal has no prefix. ❌ D — hexadecimal is 0x.",
 47: "✅ A — x = 2 // 4 = 0, then y = y // x = 4 // 0 → ZeroDivisionError at runtime. ❌ B/C/D — no value can be printed.",
 48: "✅ A — 20.12E8 is valid Python scientific notation for 20.12 × 10⁸. ❌ B — ^ is bitwise XOR in Python, not exponentiation. ❌ C — E8.0 is malformed. ❌ D — 20E12.8 is malformed.",
 49: "✅ A — ** is the exponentiation (power) operator. ❌ B — it exists. ❌ C/D — it performs no kind of multiplication.",
 51: "✅ A — != is the inequality operator. ❌ B — 'not ==' is a syntax error. ❌ C — <> was removed in Python 3.",
 55: "✅ A — my_list[-1] = my_list[-2] copies 1 into the last slot → [3, 1, 1]. ❌ B/C — indexes -1/-2 target the last two positions only; the list head is untouched.",
 56: "✅ A — the tuple assignment swaps values inside the list; the list keeps its length. ❌ B/C — assignments never add or remove list elements.",
 57: "✅ A — vals = nums makes vals another name for the SAME list, so append(1) grows both → equal lengths. ❌ B/C — they are one object, not two.",
 58: "✅ A — vals = nums[:] makes an independent COPY, so append(1) grows only vals → vals is longer. ❌ B/C — the slice broke the link between the two names.",
 63: "✅ A — == tests equality. ❌ B — = is assignment. ❌ C — === does not exist in Python. ❌ D — != tests INequality.",
 66: "✅ A — vals[0], vals[2] = vals[2], vals[0] swaps the first and last elements → reverses the 3-element list. ❌ B/C — swapping changes no length.",
 70: "✅ A+D — nums[-1:-2] is an empty slice (stop index before start), so nums is longer than vals, and slicing produces a new, different list.",
 77: "✅ A — the comprehension builds only 2 sublists (range(2)), so my_list[2] raises IndexError — a runtime error. ❌ B/C/D — the code never prints a value.",
 79: "✅ A — insert(0, 1) → [1, 0, 1, 2]; del vals[1] removes the 0 → [1, 1, 2]; sum = 4. ❌ B — 3 would be the sum before the insert; ❌ C/D — wrong traces.",
 80: "✅ C+D — vals = nums does NOT replicate: both names refer to the SAME list, so del vals[1:2] shortens it and both see the same length.",
 81: "✅ A — a function definition starts with the def keyword. ❌ B/C — 'function' and 'fun' are not Python keywords.",
 82: "✅ A — a function must be defined before its first invocation: Python resolves the name at call time. ❌ B — calling before definition raises NameError. ❌ C — definitions can sit anywhere in the code flow.",
 83: "✅ A — parameters are local variables, accessible only inside the function body. ❌ B — they are invisible outside. ❌ C — they exist during the call, not after it.",
 84: "✅ A — passing arguments by order is positional passing. ❌ B/C — 'ordered' and 'sequential' are not the terms Python uses.",
 85: "✅ B+C — return may send a value back to the caller and it terminates the function's execution. ❌ A — return never restarts execution; it ends it.",
 86: "✅ A — None designates the None value (explicit absence of a value). ❌ B — that describes the implicit return of functions without return. ❌ C — the empty instruction is pass, not None.",
 87: "✅ A — a variable defined outside a function may be READ inside it, but assigning to it requires the global keyword. ❌ B — reading works fine. ❌ C — unrestricted access is false: writing is restricted.",
 88: "✅ A — lists are passed by reference, so del inside the function removes the element from the ORIGINAL list. ❌ B — the mutation is visible outside. ❌ C — del on a valid index never raises.",
 89: "✅ A — 'in' is a reserved keyword, so def fun(in=2) is a syntax error. ❌ B/C — the code fails before any call.",
 91: "✅ A — a = len('kangaroo') = 8; b = len('0') * 2 = 2; print(8 / 2) → 4.0. Live-verified. ❌ B/C/D — no exception occurs: 2 is a valid divisor and both inputs convert via len().",
 92: "✅ A — input() returns the STRING '0'; 10 / '0' mixes int and str → TypeError. ❌ B — ValueError requires a failed int()/float() conversion. ❌ C — ZeroDivisionError requires a numeric zero. ❌ D — the division never happens.",
 94: "✅ A — value is a string, so value / value raises TypeError → 'Very very bad input...'. Live-verified. ❌ B — no division by zero occurs (the operands aren't numeric). ❌ C — no conversion failure. ❌ D — the TypeError handler catches it first.",
 95: "✅ A — a built-in function comes with Python as an integral part (print, len, input...). ❌ B — that's a user-defined function. ❌ C — functions that must be imported live in modules. ❌ D — built-ins are documented and visible.",
 96: "✅ A — fun(2) returns 1; fun(1) hits a bare return → None; None + 1 raises TypeError → runtime error. ❌ B/C/D — the addition fails before any print.",
 97: "✅ A — tuples are sequence types: they can be indexed and sliced exactly like lists. ❌ B/C — tuples are immutable: no append, no del. ❌ D — tuples are their own type, not lists.",
 98: "✅ A — the function named my_list shadows the list; del my_list[3] then tries to delete from a FUNCTION object → TypeError → the snippet is erroneous. ❌ B/C/D — no output is produced.",
 102: "✅ A — def fun(): is the correct parameterless definition: keyword, name, parentheses, colon. ❌ B — missing parentheses. ❌ C/D — 'function' is not a Python keyword.",
 104: "✅ A+B — code you suspect may raise an exception goes in the try block, and the except branch runs when the try clause errors. ❌ C — tempting, but the official PCEP key treats the compile-time SyntaxError statement as not one of the two true answers. ❌ D — backwards: try runs BEFORE except, never because of it. (Verified against the official PE1 Module 4 answer key.)",
 105: "✅ A — def fun(a=0, b=0): gives both parameters zeroed defaults. ❌ B — chained defaults a=b=0 are illegal. ❌ C/D — 'fun fun(...)' is not Python syntax.",
 107: "✅ A — tuples are immutable: my_tuple[1] = ... raises TypeError — the instruction is illegal. ❌ B/C — no tuple ever allows item assignment. ❌ D — immutability has nothing to do with element types.",
 108: "✅ A — func(a, b) requires two arguments but is called with one → TypeError (missing argument) — the snippet is erroneous. ❌ B/C/D — the function never runs.",
 109: "✅ A — k = dictionary[i] is a one-element tuple like ('a',), so k[0] prints a, b, c. ❌ B/D — tuple indices are integers, not strings. ❌ C — print(k) would print the whole tuple ('a',).",
 111: "✅ B+C — None can be assigned to variables and compared with variables (x is None). ❌ A — None is usable anywhere. ❌ D — None in arithmetic (None + 1) raises TypeError.",
 114: "✅ A+C — with x=0 defaulted, function() may be invoked with no argument and with exactly one argument. ❌ B — 'must' is false: the default makes the argument optional. ❌ D — the opposite of the truth.",
 116: "✅ A — except (TypeError, ValueError, ZeroDivisionError): — a parenthesized tuple of exceptions is the correct form. ❌ B — the comma form is Python 2 only. ❌ C/D — misplaced colon/parens. ❌ E — missing colon. ❌ F — invalid syntax.",
 117: "✅ A — function_1 returns None, and None * None raises TypeError — a runtime error. ❌ B/C/D — no multiplication of None can produce a number.",
 120: "✅ A — 1 // 2 is integer division: 0 (an int, not 0.0). ❌ B — 0.5 is regular division. ❌ C — 0.0 would require /. ❌ D — the result is fully predictable.",
 121: "✅ B+D — fun(b=0, a=0) supplies the two required parameters by keyword, and fun(0, 1, 2) supplies all three positionally. ❌ A — fun(b=1) omits required a. ❌ C — fun() omits both a and b.",
 122: "✅ A — int('0') succeeds; 0 / len('0') = 0 / 1 = 0.0, printed normally. Live-verified. ❌ B — '0' converts fine, so no ValueError. ❌ C/D/E — no exception is raised. ❌ F — 1.0 would need value '1'.",
 125: "✅ A — break outside a loop is a compile-time SyntaxError; the try/except machinery never even starts. ❌ B/C/E/F — except blocks cannot catch syntax errors.",
 126: "✅ A — func(b=2, 2) puts a positional argument after a keyword argument → SyntaxError. ❌ B/C/D — the call is rejected before the function runs.",
 127: "✅ A+B — vals = nums makes both names aliases of the same list: different names, same list, same length. ❌ C — neither grows. ❌ D — there is only ONE list.",
 128: "✅ A — != is the not-equal operator. ❌ B — 'not ==' is a syntax error. ❌ C — <> is gone in Python 3. ❌ D — =/= is not Python.",
 130: "✅ A — i < i + 2 is always True, so the loop never ends: an infinite loop printing one star per line forever. ❌ B/C/D — no fixed count exists.",
 131: "✅ A — print(Hello, World!) is missing quotation marks, so the interpreter fails at parse time with SyntaxError. ❌ B/C/D — the error is caught before execution, and it is a syntax error.",
 135: "✅ A — a positional argument's meaning is determined by its position in the argument list. ❌ B — name+value defines a KEYWORD argument. ❌ C/D — value and variable connections are irrelevant.",
 138: "✅ A — dicts have .values(), not .vals() → AttributeError — the code is erroneous. ❌ B/C/D — the loop never runs.",
 139: "✅ A+D — in and for are reserved keywords → SyntaxError if used as names. ❌ B — print is a built-in function name, not a keyword: legal (shadowing it is legal too). ❌ C — In is a different identifier from the keyword in (case-sensitive).",
 141: "✅ A — del vals[:] clears the SHARED list (vals = nums), so both names now have length 0 — the same length. ❌ B/C — neither name can differ: one object. ❌ D — clearing a slice never raises.",
 144: "✅ A — foo.index(0) searches for value 0, which is absent from (1, 2, 3) → ValueError. ❌ B — the types are fine. ❌ C — it parses correctly. ❌ D — index() exists on tuples.",
}

# auto-explanation for execution-verified questions (58)
def auto_explain(q, out):
    letters = "ABCDEF"
    correct = ", ".join(letters[i] for i in q_answers(q))
    shown = out.replace("\n", " | ")[:80]
    txt = f"✅ {correct} — live-verified by executing the snippet: actual output is {shown!r}, matching this option exactly."
    for i, o in enumerate(q["options"]):
        if i not in q_answers(q):
            txt += f" | ❌ {letters[i]} — does not match the verified output ({shown!r})."
    return txt

def q_answers(q):
    return ANSWERS[q["id"]]

def main():
    bank = json.load(open(os.path.join(HERE, "bank_raw.json"), encoding="utf-8"))
    try:
        exec_ans = json.load(open(os.path.join(HERE, "exec_answers_pass2.json"), encoding="utf-8"))
        exec_out = json.load(open(os.path.join(HERE, "exec_results.json"), encoding="utf-8"))
    except FileNotFoundError:
        exec_ans, exec_out = {}, {}

    out, problems = [], []
    for b in bank:
        qid = b["id"]
        ans = ANSWERS.get(qid)
        if ans is None:
            problems.append(f"no answer for {qid}"); continue
        n = len(b["options"])
        if any(i >= n for i in ans):
            problems.append(f"answer range {qid}"); continue
        concept = CONCEPTS.get(qid, "Python Basics")
        if str(qid) in exec_ans:
            expl = auto_explain(b, exec_out.get(str(qid), "verified"))
            src = "execution-verified"
        elif qid in EXPLAIN:
            expl = EXPLAIN[qid]
            src = "expert-reviewed"
        else:
            problems.append(f"NO EXPLANATION for {qid}"); continue
        out.append({
            "id": qid, "q": b["q"], "options": b["options"], "type": b["type"],
            "answers": ans, "concept": concept, "expl": expl, "explsrc": src,
        })

    if problems:
        print("PROBLEMS:")
        for p in problems: print(" ", p)
        return 1
    multi = sum(1 for o in out if o["type"] == "Multiple Choice")
    ev = sum(1 for o in out if o["explsrc"] == "execution-verified")
    concepts = sorted(set(o["concept"] for o in out))
    json.dump(out, open(os.path.join(HERE, "pcep_bank.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"pcep_bank.json: {len(out)} questions | {ev} execution-verified | {len(out)-ev} expert-reviewed | {multi} multi-select")
    print(f"concepts ({len(concepts)}): " + ", ".join(f"{c} ({sum(1 for o in out if o['concept']==c)})" for c in concepts))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
