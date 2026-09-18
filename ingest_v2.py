"""V3 ingestion: parse all raw_data_v2 TestInvitation exports (incl. let-data
wrappers), extract with codep-preserving stripper, dedupe vs existing bank and
internally, emit bank_new_raw.json for keying."""
import json, os, re, hashlib, sys
sys.path.insert(0, os.path.dirname(__file__))
from html.parser import HTMLParser
import html as ihtml

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.join(HERE, "raw_data_v2")

class Stripper3(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.in_codep = [], 0
    def handle_starttag(self, tag, attrs):
        if tag == "code" and "codep" in (dict(attrs).get("class") or ""):
            self.in_codep += 1
        elif tag == "br":
            self.parts.append("\n")
        elif tag in ("p", "div", "li") and not self.in_codep:
            self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag == "code" and self.in_codep:
            self.in_codep -= 1
            self.parts.append("\n@@CODEEND@@\n")
        elif tag in ("p", "div", "li") and not self.in_codep:
            self.parts.append("\n")
    def handle_data(self, d):
        self.parts.append(d)

def strip_html_ml(s):
    if s is None: return ""
    p = Stripper3(); p.feed(s)
    out = []
    for seg in re.split(r"@@CODEEND@@", "".join(p.parts)):
        code_like = seg.count("\n") >= 1 and re.search(r"[=:{}]", seg)
        for line in seg.split("\n"):
            line = line.replace("\t", "    ").rstrip()
            c = " ".join(line.split())
            if c: out.append(c)
    return ihtml.unescape("\n".join(out)).strip()

def norm(s): return re.sub(r"\s+", " ", s).strip().lower()

def parse_export(path):
    txt = open(path, encoding="utf-8-sig", errors="replace").read()
    m = re.search(r"let data = (\{.*\})\s*;?\s*</script>", txt, re.S) or \
        re.search(r"let data = (\{.*\})\s*;?\s*$", txt, re.S)
    if m:
        txt = m.group(1)
    return json.loads(txt)

def main():
    # existing bank for dedupe
    existing = json.load(open(os.path.join(HERE, "bank_raw.json"), encoding="utf-8"))
    seen = set()
    for b in existing:
        seen.add(hashlib.md5((norm(b["q"]) + "||" + "||".join(norm(o) for o in b["options"])).encode()).hexdigest())

    new_bank, dup_internal, dup_existing = [], 0, 0
    for f in sorted(os.listdir(V2)):
        if not f.endswith(".json"): continue
        path = os.path.join(V2, f)
        try:
            d = parse_export(path)
        except Exception as ex:
            print(f"SKIP {f}: {str(ex)[:60]}")
            continue
        qs = d.get("questions") or []
        src_date = "unknown"
        mdate = re.search(r"(20\d{2})[.\-_ ]?(\d{2})[.\-_ ]?(\d{2})", f)
        if mdate: src_date = "-".join(mdate.groups())
        track = "PCAP" if "PCAP" in f else "PCEP"
        for q in qs:
            qtext = strip_html_ml(q["question"]).strip()
            opts = [strip_html_ml(o["option"]).strip() for o in (q["options"] or [])]
            key = hashlib.md5((norm(qtext) + "||" + "||".join(norm(o) for o in opts)).encode()).hexdigest()
            if key in seen:
                # is it existing-library dup or internal dup?
                dup_existing += 1
                continue
            seen.add(key)
            new_bank.append({"id": len(new_bank) + 1, "q": qtext, "options": opts,
                             "type": q["type"], "source": f, "source_date": src_date,
                             "track": track})
    json.dump(new_bank, open(os.path.join(HERE, "bank_new_raw.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(f"new unique questions: {len(new_bank)} (dups vs library: {dup_existing}, internal dups: {dup_internal})")
    from collections import Counter
    print(Counter((b["source_date"], b["track"]) for b in new_bank))

if __name__ == "__main__":
    main()
