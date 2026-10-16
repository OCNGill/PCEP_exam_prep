#!/usr/bin/env python3
"""build_singlefile.py - package the PCEP trainer into ONE self-contained HTML file.

Reads practice.html (source is NEVER modified), inlines every *local* asset
reference so the result runs from file:// with no sibling files, and writes
practice_singlefile.html next to it.

Handled:
  <script src="local.js">          -> inline <script>...</script>
  <link rel="stylesheet" href=...> -> inline <style>...</style>
  <img src="local.png">            -> inline data: URI

Anything http(s)://, protocol-relative (//) or data: is left alone (and
reported as an external dependency, which breaks offline use). Any other
unresolvable local reference fails the build (exit 1) instead of silently
producing a broken file.

Usage:
    python build_singlefile.py [--source practice.html] [--output practice_singlefile.html]

Deterministic: no timestamps, so repeated runs over the same inputs produce
byte-identical output (sha256 stays stable).
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import re
import sys
from pathlib import Path

# url that cannot be resolved against the filesystem
EXTERNAL_URL = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.\-]*:|//|#)")

SCRIPT_OPEN = re.compile(r"<script\b([^>]*)>", re.IGNORECASE)
LINK_TAG = re.compile(r"<link\b([^>]*)>", re.IGNORECASE)
IMG_TAG = re.compile(r"<img\b([^>]*)>", re.IGNORECASE)
SRC_ATTR = re.compile(r"\bsrc\s*=\s*([\"'])(.*?)\1", re.IGNORECASE)
HREF_ATTR = re.compile(r"\bhref\s*=\s*([\"'])(.*?)\1", re.IGNORECASE)
REL_ATTR = re.compile(r"\brel\s*=\s*([\"'])(.*?)\1", re.IGNORECASE)
ATTR_NAME = re.compile(r"\b([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*(?:=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?")


def is_external(url: str) -> bool:
    return bool(EXTERNAL_URL.match(url.strip()))


def local_path(url: str, base: Path) -> Path:
    """Resolve a local reference relative to the HTML file (query/fragment stripped)."""
    clean = url.split("#", 1)[0].split("?", 1)[0]
    from urllib.parse import unquote

    clean = unquote(clean)
    p = Path(clean)
    return p if p.is_absolute() else (base / p)


def attrs_without(attrs: str, drop: set[str]) -> str:
    """Strip named attributes from a raw attribute string, keep everything else."""
    out, pos = [], 0
    for m in ATTR_NAME.finditer(attrs):
        if m.group(1).lower() in drop:
            out.append(attrs[pos : m.start()])
            pos = m.end()
    out.append(attrs[pos:])
    return "".join(out).rstrip()


def inline_scripts(html: str, base: Path, report: dict, problems: list) -> str:
    """Replace <script src="local.js">…</script> with its file contents."""

    def repl(m: re.Match) -> str:
        attrs = m.group(1)
        sm = SRC_ATTR.search(attrs)
        if not sm:
            return m.group(0)  # inline script, untouched
        url = sm.group(2)
        if is_external(url):
            report["external_refs"].append(url)
            return m.group(0)
        path = local_path(url, base)
        if not path.is_file():
            problems.append(f"<script src=\"{url}\"> -> file not found: {path}")
            return m.group(0)
        js = path.read_text(encoding="utf-8")
        # a literal "</script" anywhere would terminate the inline block early
        n = js.lower().count("</script")
        if n:
            js = re.sub(r"</script", r"<\\/script", js, flags=re.IGNORECASE)
            report["escaped_closing_script_sequences"] += n
        report["inlined_scripts"].append({"src": url, "bytes": len(js.encode("utf-8"))})
        new_attrs = attrs_without(attrs, {"src"})
        return "<script" + new_attrs + ">" + js + "</script>"

    # walk tags from the end so earlier offsets stay valid
    matches = list(SCRIPT_OPEN.finditer(html))
    for m in reversed(matches):
        sm = SRC_ATTR.search(m.group(1))
        if not sm or is_external(sm.group(2)):
            continue
        close = re.compile(r"</script\s*>", re.IGNORECASE).search(html, m.end())
        if not close:
            problems.append(f"unclosed <script> after src=\"{sm.group(2)}\"")
            continue
        segment = html[m.start() : close.end()]
        html = html[: m.start()] + repl(m) + html[close.end() :]
        _ = segment  # segment kept for clarity/debugging
    return html


def inline_links(html: str, base: Path, report: dict, problems: list) -> str:
    """Replace <link rel="stylesheet" href="local.css"> with a <style> block."""

    def repl(m: re.Match) -> str:
        attrs = m.group(1)
        hm = HREF_ATTR.search(attrs)
        if not hm:
            return m.group(0)
        rm = REL_ATTR.search(attrs)
        rel = (rm.group(2).lower() if rm else "")
        if "stylesheet" not in rel:
            return m.group(0)
        url = hm.group(2)
        if is_external(url):
            report["external_refs"].append(url)
            return m.group(0)
        path = local_path(url, base)
        if not path.is_file():
            problems.append(f"<link href=\"{url}\"> -> file not found: {path}")
            return m.group(0)
        css = path.read_text(encoding="utf-8")
        report["inlined_styles"].append({"href": url, "bytes": len(css.encode("utf-8"))})
        keep = attrs_without(attrs, {"href", "rel"})
        media = re.search(r"\bmedia\s*=\s*([\"'])(.*?)\1", keep, re.IGNORECASE)
        open_tag = f"<style{(' media=' + chr(34) + media.group(2) + chr(34)) if media else ''}>"
        return open_tag + css + "</style>"

    for m in reversed(list(LINK_TAG.finditer(html))):
        hm = HREF_ATTR.search(m.group(1))
        if not hm or is_external(hm.group(2)):
            continue
        html = html[: m.start()] + repl(m) + html[m.end() :]
    return html


def inline_images(html: str, base: Path, report: dict, problems: list) -> str:
    """Replace <img src="local.png"> with a base64 data: URI."""

    def repl(m: re.Match) -> str:
        attrs = m.group(1)
        sm = SRC_ATTR.search(attrs)
        if not sm:
            return m.group(0)
        url = sm.group(2)
        if is_external(url):
            report["external_refs"].append(url)
            return m.group(0)
        path = local_path(url, base)
        if not path.is_file():
            problems.append(f"<img src=\"{url}\"> -> file not found: {path}")
            return m.group(0)
        mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        report["inlined_images"].append({"src": url, "bytes": path.stat().st_size})
        return "<img" + attrs_without(attrs, {"src"}) + f" src=\"data:{mime};base64,{b64}\">"

    for m in reversed(list(IMG_TAG.finditer(html))):
        sm = SRC_ATTR.search(m.group(1))
        if not sm or is_external(sm.group(2)):
            continue
        html = html[: m.start()] + repl(m) + html[m.end() :]
    return html


RESOURCE_ATTR = re.compile(
    r"<(?:script|link|img|iframe|source|video|audio|embed)\b[^>]*?\b(?:src|href)\s*=\s*([\"'])(.*?)\1",
    re.IGNORECASE,
)


def self_containment_scan(html: str) -> tuple[list, list]:
    """Return (remaining_local_refs, remaining_external_refs) for resource tags."""
    local, external = [], []
    for m in RESOURCE_ATTR.finditer(html):
        url = m.group(2).strip()
        if url.startswith("data:"):
            continue
        (external if is_external(url) else local).append(url)
    return local, external


def build(source: Path, output: Path) -> dict:
    html = source.read_text(encoding="utf-8")
    base = source.parent
    report = {
        "source": str(source),
        "output": str(output),
        "source_bytes": len(html.encode("utf-8")),
        "inlined_scripts": [],
        "inlined_styles": [],
        "inlined_images": [],
        "external_refs": [],
        "escaped_closing_script_sequences": 0,
        "problems": [],
    }
    html = inline_scripts(html, base, report, report["problems"])
    html = inline_links(html, base, report, report["problems"])
    html = inline_images(html, base, report, report["problems"])

    local_left, external_left = self_containment_scan(html)
    if local_left:
        report["problems"].append(
            "unresolved local resource reference(s) remain: " + ", ".join(sorted(set(local_left)))
        )
    report["remaining_local_refs"] = local_left
    report["remaining_external_refs"] = external_left

    if report["problems"]:
        report["built"] = False
        return report

    data = html.encode("utf-8")
    output.write_bytes(data)
    report["built"] = True
    report["output_bytes"] = len(data)
    report["sha256"] = hashlib.sha256(data).hexdigest()
    return report


def main(argv=None) -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Build the single-file PCEP trainer HTML.")
    ap.add_argument("--source", default=str(here / "practice.html"))
    ap.add_argument("--output", default=str(here / "practice_singlefile.html"))
    args = ap.parse_args(argv)

    source = Path(args.source)
    output = Path(args.output)
    if not source.is_file():
        print(f"ERROR: source not found: {source}", file=sys.stderr)
        return 1

    report = build(source, output)
    print("=== BUILD REPORT ===")
    print(json.dumps(report, indent=2))
    if not report["built"]:
        for p in report["problems"]:
            print(f"BUILD FAILED: {p}", file=sys.stderr)
        return 1
    n_scripts = len(report["inlined_scripts"])
    print(
        f"OK: {source.name} ({report['source_bytes']} B) -> {output.name} "
        f"({report['output_bytes']} B), {n_scripts} external script(s) inlined, "
        f"sha256={report['sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())