"""Trace engine v2: real line-tracer via sys.settrace (worker thread + timeout
for infinite-loop snippets). For every executed line it snapshots the variable
state BEFORE the line runs, so explanations can show actual arithmetic:
  a = a ^ b    →  a = 1 ^ 0 = 1
"""
import ast, json, os, re, sys, threading, io, queue, copy

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

def _pl(n, unit):
    return f"{n} {unit}" + ("" if n == 1 else "s")


def _concat_note(expr, locs):
    """WHY annotation for sequence concatenation: show that lengths add."""
    try:
        if " + " not in expr:
            return ""
        left, right = expr.split(" + ", 1)
        ev = {"__builtins__": __builtins__}
        lv = eval(left, ev, dict(locs))
        rv = eval(right, ev, dict(locs))
        total = eval(expr, ev, dict(locs))
        if isinstance(lv, (str, tuple, list)) and type(lv) is type(rv) is type(total):
            unit = "character" if isinstance(lv, str) else "element"
            return f"  [concatenation: {_pl(len(lv), unit)} + {_pl(len(rv), unit)} = {_pl(len(total), unit)}]"
    except Exception:
        return ""
    return ""


class _NoBreak(Exception):
    pass


_OPFN = {
    ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b, ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b, ast.LShift: lambda a, b: a << b,
    ast.RShift: lambda a, b: a >> b, ast.BitAnd: lambda a, b: a & b,
    ast.BitOr: lambda a, b: a | b, ast.BitXor: lambda a, b: a ^ b,
}
_OPSYM = {
    ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
    ast.FloorDiv: "//", ast.Mod: "%", ast.Pow: "**",
    ast.LShift: "<<", ast.RShift: ">>", ast.BitAnd: "&",
    ast.BitOr: "|", ast.BitXor: "^",
}
_PREC = {ast.Pow: 6, ast.Mult: 4, ast.Div: 4, ast.FloorDiv: 4, ast.Mod: 4,
         ast.LShift: 3, ast.RShift: 3, ast.Add: 2, ast.Sub: 2,
         ast.BitAnd: 1, ast.BitXor: 1, ast.BitOr: 1}
_SAFE_MAP = {"len": len, "abs": abs, "round": round, "int": int,
             "float": float, "str": str, "sum": sum, "min": min,
             "max": max, "ord": ord, "bin": bin, "oct": oct, "hex": hex}


def _arith_breakdown(expr, locs):
    """Step-by-step arithmetic chain for a compound expression, e.g.
        1 / 2 + 3 // 3 + 4 ** 2
    becomes
        ['4 ** 2 = 16', '1 / 2 = 0.5', '3 // 3 = 1',
         '0.5 + 1 = 1.5', '1.5 + 16 = 17.5']
    Each line shows real operands and the intermediate result, ordered so
    every value is computed before it is used (dependency-safe) with the
    highest-precedence ready operator first (PEMDAS). Returns [] when there
    is nothing to break down: fewer than two operations, side-effect calls,
    or syntax outside the arithmetic whitelist — callers keep the old
    rendering then."""
    try:
        tree = ast.parse(str(expr).strip(), mode="eval").body
    except Exception:
        return []
    steps = []  # each: {prec, deps:set, text}

    def red(n, depth=0):
        if depth > 12 or len(steps) > 14:
            raise _NoBreak()
        if isinstance(n, ast.Constant):
            return n.value, None
        if isinstance(n, ast.Name):
            if n.id in locs:
                return locs[n.id], None
            raise _NoBreak()
        if isinstance(n, ast.UnaryOp) and type(n.op) in (ast.USub, ast.UAdd, ast.Invert):
            v, dep = red(n.operand, depth + 1)
            if isinstance(v, (list, tuple, str)) and isinstance(n.op, ast.USub):
                raise _NoBreak()  # sequence negation does not exist
            v = -v if isinstance(n.op, ast.USub) else (+v if isinstance(n.op, ast.UAdd) else ~v)
            return v, dep
        if isinstance(n, ast.BinOp) and type(n.op) in _OPFN:
            lv, ld = red(n.left, depth + 1)
            rv, rd = red(n.right, depth + 1)
            if type(n.op) is ast.Pow and isinstance(rv, int) and abs(rv) > 64:
                raise _NoBreak()
            try:
                v = _OPFN[type(n.op)](lv, rv)
            except Exception:
                raise _NoBreak()
            if isinstance(v, int) and not isinstance(v, bool) and v.bit_length() > 512:
                raise _NoBreak()
            sid = len(steps)
            steps.append({
                "prec": _PREC.get(type(n.op), 1),
                "deps": {d for d in (ld, rd) if d is not None},
                "text": f"{fmt(lv)} {_OPSYM[type(n.op)]} {fmt(rv)} = {fmt(v)}",
            })
            return v, sid
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id in _SAFE_MAP and not n.keywords):
            args, deps = [], set()
            for a in n.args:
                av, ad = red(a, depth + 1)
                args.append(av)
                if ad is not None:
                    deps.add(ad)
            try:
                v = _SAFE_MAP[n.func.id](*args)
            except Exception:
                raise _NoBreak()
            if isinstance(v, int) and not isinstance(v, bool) and v.bit_length() > 512:
                raise _NoBreak()
            sid = len(steps)
            rendered = ", ".join(fmt(a) for a in args)
            steps.append({"prec": 7, "deps": deps,
                          "text": f"{n.func.id}({rendered}) = {fmt(v)}"})
            return v, sid
        raise _NoBreak()

    try:
        red(tree)
    except Exception:
        return []
    # emit: dependency-safe, highest precedence first among ready steps
    emitted, out, pend = set(), [], list(range(len(steps)))
    while pend:
        ready = [i for i in pend if steps[i]["deps"] <= emitted]
        if not ready:
            return []
        pick = min(ready, key=lambda i: (-steps[i]["prec"], i))
        out.append(steps[pick]["text"])
        emitted.add(pick)
        pend.remove(pick)
    return out if len(out) >= 2 else []


def _chain(steps):
    """Render a breakdown chain as indented continuation lines."""
    return "\n        " + "\n        ".join("· " + s for s in steps)


def _num_note(expr, locs):
    """WHY annotation for int/float promotion in arithmetic."""
    try:
        if " + " not in expr:
            return ""
        ev = {"__builtins__": __builtins__}
        left, right = expr.split(" + ", 1)
        lv = eval(left, ev, dict(locs))
        rv = eval(right, ev, dict(locs))
        if (isinstance(lv, (int, float)) and isinstance(rv, (int, float))
                and type(lv) is not type(rv)
                and not isinstance(lv, bool) and not isinstance(rv, bool)):
            total = eval(expr, ev, dict(locs))
            return f"  [type promotion: {type(lv).__name__} + {type(rv).__name__} → {type(total).__name__}]"
    except Exception:
        return ""
    return ""


def describe_step(step, printed_lines=()):
    src = step["src"]
    locs = step["before"]
    # print lines: attribute captured output lines in order
    if src.startswith("print("):
        if printed_lines:
            inner = src[6:-1] if src.endswith(")") else ""
            if inner.startswith("len(") and inner.endswith(")"):
                target = inner[4:-1].strip()
                if target in locs:
                    v = locs[target]
                    return f"{src}    →  {target} = {fmt(v)}, len = {len(v)} → prints {printed_lines[0]!r}"
            chain = _arith_breakdown(src[6:-1], locs) if src.startswith("print(") and src.endswith(")") else []
            base = f'{src}    →  prints {printed_lines[0]!r}'
            return base + (_chain(chain) if chain else "")
        return None  # skip duplicate print headers
    m = re.match(r"(\w+)\s*=\s*(.+)$", src)
    if m and not m.group(2).startswith(("input",)):
        var, expr = m.group(1), m.group(2)
        try:
            val = eval(expr, {"__builtins__": __builtins__}, dict(locs))
            if re.search(r"\bfor\b.+\bin\b", expr):
                # comprehension: don't substitute inlined iteration locals
                return f"{src}    →  {var} = {fmt(val)}"
            chain = _arith_breakdown(expr, locs)
            if chain:
                # arithmetic chain replaces the source echo: show the numbers
                return (f"{src}    →  {var} = {fmt(val)}"
                        + _concat_note(expr, locs) + _chain(chain))
            sub = _subst(expr, locs)
            arrow = f" = {sub} = {fmt(val)}" if sub != fmt(val) else f" = {fmt(val)}"
            return f"{src}    →  {var}{arrow}" + _concat_note(expr, locs) + _num_note(expr, locs)
        except Exception:
            return f"{src}    →  {_subst(expr, locs)}" if _subst(expr, locs) != expr else src
    mret = re.match(r"return (.+)$", src)
    if mret:
        chain = _arith_breakdown(mret.group(1), locs)
        return (f"{src}    →  returns {_subst(mret.group(1), locs)}"
                + (_chain(chain) if chain else ""))
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
        head = f"{src}    →  {var} = {fmt(locs[var])} {op.replace('=','')} ({_subst(rhs, locs)}) = {fmt(val)}"
        chain = _arith_breakdown(rhs, locs)
        if chain:
            head += _chain(chain)
        return head
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
    # Bare expression statements (e.g. `123 + 0.0`): evaluate them so the
    # walkthrough shows the RESULT, not just the source echo.
    _kw = ("def ", "class ", "for ", "while ", "if ", "elif", "else", "try",
           "except", "finally", "with ", "pass", "break", "continue", "return",
           "global ", "nonlocal ", "del ", "raise", "yield", "import ", "from ",
           "assert", "@")
    if src and not src.endswith(":") and "input(" not in src and not src.startswith(_kw):
        try:
            val = eval(src, {"__builtins__": __builtins__}, dict(locs))
            chain = _arith_breakdown(src, locs)
            if chain:
                return f"{src}    →  evaluates to {fmt(val)}" + _chain(chain)
            return f"{src}    →  evaluates to {fmt(val)}" + _num_note(src, locs)
        except Exception:
            pass
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
