/* verify_singlefile.js - prove the built single-file trainer works offline.
 *
 * 1. Static: no resource tag may reference a local file (everything inlined).
 * 2. Load it in jsdom exactly like file:// (no resource loader -> nothing can
 *    be fetched), capture any script errors.
 * 3. Functional smoke: bank, flashcards, home render, exam sim, flashcards.
 *
 * Usage: node verify_singlefile.js [path/to/practice_singlefile.html]
 */
const fs = require("fs");
const path = require("path");
const { JSDOM, VirtualConsole } = require("jsdom");

const FILE =
  process.argv[2] ||
  path.join(__dirname, "practice_singlefile.html");

let failures = 0;
const check = (name, cond, detail) => {
  console.log((cond ? "PASS" : "FAIL") + " - " + name + (cond ? "" : " :: " + (detail || "")));
  if (!cond) failures++;
};

const html = fs.readFileSync(FILE, "utf-8");

// ---- 1. static self-containment ----
const RESOURCE_ATTR = /<(?:script|link|img|iframe|source|video|audio|embed)\b[^>]*?\b(?:src|href)\s*=\s*["']([^"']*)["']/gi;
const locals = [];
const externals = [];
let m;
while ((m = RESOURCE_ATTR.exec(html)) !== null) {
  const url = m[1].trim();
  if (url.startsWith("data:")) continue;
  if (/^(?:[a-zA-Z][a-zA-Z0-9+.\-]*:|\/\/|#)/.test(url)) externals.push(url);
  else locals.push(url);
}
check("no <script src=...> left", !/<script\b[^>]*\bsrc\s*=/i.test(html));
check("no local resource references remain", locals.length === 0, locals.join(", "));
check("bank.js contents present (PCEP_BANK declared)", /const\s+PCEP_BANK\s*=\s*\[/.test(html));
check("flashcards present (PCEP_FLASHCARDS declared)", /const\s+PCEP_FLASHCARDS\s*=\s*\[/.test(html));

// ---- 2. load as file:// with NO external fetching ----
const jsErrors = [];
const vc = new VirtualConsole();
vc.on("jsdomError", (e) => jsErrors.push(e.message));
vc.on("error", (...a) => jsErrors.push(a.join(" ")));

const store = new Map();
const lsValue = {
  getItem: (k) => (store.has(k) ? store.get(k) : null),
  setItem: (k, v) => store.set(k, String(v)),
  removeItem: (k) => store.delete(k),
  clear: () => store.clear(),
};

const dom = new JSDOM(html, {
  runScripts: "dangerously",
  url: "file:///" + FILE.replace(/\\/g, "/"),
  pretendToBeVisual: true,
  virtualConsole: vc,
  beforeParse(window) {
    Object.defineProperty(window, "localStorage", { value: lsValue, configurable: true });
    window.confirm = () => true;
    window.alert = () => {};
  },
});

setTimeout(() => {
  const w = dom.window;
  const doc = w.document;
  try {
    check("no script errors on load", jsErrors.length === 0, jsErrors.join(" | "));

    // ---- 3. functional smoke ----
    check("PCEP_BANK loaded (148 questions)", w.eval("bank.length") === 148, "got " + w.eval("bank.length"));
    check("PCEP_FLASHCARDS loaded (100 cards)", w.eval("PCEP_FLASHCARDS.length") === 100, "got " + w.eval("PCEP_FLASHCARDS.length"));
    check("home stats rendered (0/148)", (doc.getElementById("homeStats") || {}).textContent?.includes("0/148"));

    w.eval("startExam()");
    check("exam sim: 30 questions", w.eval("state.qs.length") === 30, "got " + w.eval("state.qs.length"));
    check("exam sim: 40:00 timer", doc.getElementById("timer").textContent === "40:00", doc.getElementById("timer").textContent);

    w.eval("state.idx = 0; renderQ();");
    const answers = w.eval("state.qs[0].answers");
    if (answers.length > 1) {
      answers.forEach((a) => w.eval(`pick(${a}, true)`));
      w.eval("submitMulti()");
    } else {
      w.eval(`pick(${answers[0]}, false)`);
    }
    check("answering renders feedback", doc.getElementById("fb").textContent.startsWith("✅"), doc.getElementById("fb").textContent.slice(0, 40));
    w.eval("goHome()");

    w.eval("startFlashcards()");
    check("flashcards view opens", !doc.getElementById("flash").classList.contains("hidden"));
    check("card question rendered", doc.getElementById("fcQ").textContent.length > 3);
    w.eval("revealCard()");
    check("answer revealed", !doc.getElementById("fcA").classList.contains("hidden"));

    w.eval("showStats()");
    check("stats screen renders", !doc.getElementById("statsScr").classList.contains("hidden"));
    w.eval("goHome()");
  } catch (e) {
    check("functional smoke ran without exception", false, e.message);
  }

  console.log(failures === 0 ? "ALL SINGLE-FILE CHECKS PASSED" : failures + " CHECK(S) FAILED");
  console.log("external refs still referenced (must be empty for offline): " + JSON.stringify(externals));
  w.close();
  process.exit(failures ? 1 : 0);
}, 500);