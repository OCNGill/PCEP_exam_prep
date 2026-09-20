"""Trace engine v2: real line-tracer via sys.settrace (worker thread + timeout
for infinite-loop snippets). For every executed line it snapshots the variable
state BEFORE the line runs, so explanations can show actual arithmetic:
  a = a ^ b    →  a = 1 ^ 0 = 1
"""
import json, os, re, sys, threading, io, queue, copy

HERE = os.path.dirname(os.path.abspath(__file__))

def fmt(v):
    try:
        if isinstance(v, float) and v.is_integer():
            return repr(v)
        if isinstance(v, list):
            return "[" + ", ".join(fmt(x) for x in v) + "]"
        if isinstance(v, tuple):
            return "(" + ", ".join(fmt(x) for x in v) + ("," if len(v) == 1 else "") + ")"
    except Exception:
        pass
    return repr(v)

def run_trace(code, stdin_lines=(), max_events=400, timeout=3.0):
    """Return (steps, printed). steps = [{'src': line, 'before': {var: val}}]"""
    result_q = queue.Queue()

    def worker():
        src_lines = code.splitlines()
        steps = []
        prev_locals = {}

        class TraceLimit(Exception):
            pass

        def snap(v):
            if isinstance(v, (list, dict, set, tuple)):
                return copy.deepcopy(v)
            return v

        def tracer(frame, event, arg):
            if event == "line":
                fname = frame.f_code.co_name
                # skip comprehension/genexpr/lambda sub-frames (same source lines,
                # no useful locals) but allow real named functions
                if fname != "<module>" and (fname.startswith("<") or fname == "__trace__"):
                    return tracer
                ln = frame.f_lineno - 1
                if 0 <= ln < len(src_lines):
                    src = src_lines[ln].strip()
                    locs = {k: snap(v) for k, v in frame.f_locals.items()
                            if not k.startswith("__")}
                    steps.append({"src": src, "before": dict(locs), "fn": fname})
                    prev_locals.update(locs)
                    if len(steps) >= max_events:
                        raise TraceLimit()
            return tracer

        stdin_iter = iter(list(stdin_lines))
        def mock_input(prompt=""):
            try:
                return next(stdin_iter)
            except StopIteration:
                return ""

        buf = io.StringIO()
        old = sys.stdout
        g = {"__name__": "__trace__", "input": mock_input}
        sys.stdout = buf
        try:
            code_obj = compile(code, "<snippet>", "exec")
            g["__trace__code__"] = code_obj
            sys.settrace(tracer)
            try:
                exec(code_obj, g)
            except TraceLimit:
                pass
            finally:
                sys.settrace(None)
        except Exception:
            pass
        finally:
            sys.stdout = old
            printed = buf.getvalue()
        result_q.put((steps, printed))

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return None, "<<TIMEOUT>>"
    try:
        return result_q.get_nowait()
    except queue.Empty:
        return None, "<<TIMEOUT>>"

def _subst(expr, locs, depth=0):
    """Substitute variable values into an expression string for display."""
    if depth > 3:
        return expr
    out = expr
    for k, v in sorted(locs.items(), key=lambda kv: -len(kv[0])):
        if re.search(r"\b" + re.escape(k) + r"\b", out):
            out = re.sub(r"\b" + re.escape(k) + r"\b", fmt(v), out)
    return out

def describe_step(step, printed_lines=()):
    src = step["src"]
    locs = step["before"]
    # print lines: attribute captured output lines in order
    if src.startswith("print("):
        if printed_lines:
            return f'{src}    →  prints {printed_lines[0]!r}'
        return None  # skip duplicate print headers
    m = re.match(r"(\w+)\s*=\s*(.+)$", src)
    if m and not m.group(2).startswith(("input",)):
        var, expr = m.group(1), m.group(2)
        try:
            val = eval(expr, {"__builtins__": __builtins__}, dict(locs))
            if re.search(r"\bfor\b.+\bin\b", expr):
                # comprehension: don't substitute inlined iteration locals
                return f"{src}    →  {var} = {fmt(val)}"
            sub = _subst(expr, locs)
            arrow = f" = {sub} = {fmt(val)}" if sub != fmt(val) else f" = {fmt(val)}"
            return f"{src}    →  {var}{arrow}"
        except Exception:
            return f"{src}    →  {_subst(expr, locs)}" if _subst(expr, locs) != expr else src
    mret = re.match(r"return (.+)$", src)
    if mret:
        return f"{src}    →  returns {_subst(mret.group(1), locs)}"
    mfor = re.match(r"for (\w+) in (.+):$", src)
    if mfor:
        var = mfor.group(1)
        if var in locs:
            return f"{src}    →  {var} = {fmt(locs[var])}"
        return src
    mwhile = re.match(r"while (.+):$", src)
    if mwhile:
        cond = _subst(mwhile.group(1), locs)
        return f"{src}    →  {cond} is True"
    mif = re.match(r"if (.+):$", src)
    if mif:
        return f"{src}    →  checks {_subst(mif.group(1), locs)}"
    maug = re.match(r"(\w+)\s*(\+=|-=|\*=|/=|//=|%=|\*\*=)\s*(.+)$", src)
    if maug and maug.group(1) in locs:
        var, op, rhs = maug.groups()
        _ops = {"+=": lambda a, b: a + b, "-=": lambda a, b: a - b,
                "*=": lambda a, b: a * b, "/=": lambda a, b: a / b,
                "//=": lambda a, b: a // b, "%=": lambda a, b: a % b,
                "**=": lambda a, b: a ** b}
        try:
            val = _ops[op](locs[var], eval(rhs, {"__builtins__": __builtins__}, dict(locs)))
        except Exception:
            return f"{src}    →  {_subst(rhs, locs)}"
        return f"{src}    →  {var} = {fmt(locs[var])} {op.replace('=','')} ({_subst(rhs, locs)}) = {fmt(val)}"
    # list mutation lines: execute on a copy of before-state, show result
    mm = re.match(r"(\w+)\.(insert|append|extend|pop|remove)\(", src) or \
         re.match(r"del (\w+)\[", src)
    if mm:
        base = mm.group(1)
        if base in locs:
            ns = dict(locs)
            try:
                exec(src, {"__builtins__": __builtins__}, ns)
                return f"{src}    →  {base} becomes {fmt(ns.get(base))}"
            except Exception:
                return src
    return src

def build_walkthrough(q, steps, output):
    """Pedagogical walkthrough with real arithmetic per line."""
    letters = "ABCDEF"
    correct = ", ".join(letters[i] for i in q["answers"])
    lines = [f"✅ {correct} — walk through it line by line:"]
    # attribute prints: collect print outputs in order
    printed_lines = [l for l in output.split("\n")] if output and output != "<<TIMEOUT>>" else []
    pi = 0
    prev_src = None
    prev_desc = None
    shown = 0
    for st in steps:
        if st["src"].startswith("print(") and st["src"] == prev_src:
            continue
        d = describe_step(st, printed_lines[pi:pi+1] if pi < len(printed_lines) else [])
        if d is None:
            continue
        if d == prev_desc:
            continue  # collapse identical consecutive lines (comprehension echoes)
        if st["src"].startswith("print(") and d and "prints" in d:
            pi += 1
        prev_src = st["src"]
        prev_desc = d
        fn = st.get("fn")
        prefix = f"[in {fn}()] " if fn and fn != "<module>" else ""
        lines.append("  • " + prefix + d)
        shown += 1
        if shown >= 24:
            lines.append("  • … (long run truncated; see verified output below)")
            break
    if printed_lines:
        lines.append(f"  → output: {' | '.join(l for l in printed_lines if l.strip())!r}")
    return "\n".join(lines)

if __name__ == "__main__":
    demo = 'a = 1\nb = 0\na = a ^ b\nb = a ^ b\na = a ^ b\nprint(a, b)'
    steps, out = run_trace(demo)
    print(out)
    q = {"answers": [0], "options": ["0 1"]}
    print(build_walkthrough(q, steps, out))
