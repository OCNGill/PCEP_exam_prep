/* Functional regression suite v2 for practice.html (jsdom, headless).
   Covers: bank load, explanations/concepts coverage, 30Q/40min exam, back
   button, explain panel, flag checkbox, full drill, multi-select, stats
   persistence, wrong path, blank-spot drill, flagged drill, stats screen,
   run history, readiness. */
const fs = require("fs");
const path = require("path");
const { JSDOM } = require(path.join(process.env.TEMP, "node_modules", "jsdom"));

const SRC = "C:/Users/Gillsystems Laptop/source/repos/OCNGill/PCEP_exam_prep";
const APPDIR = path.join(process.env.TEMP, "pcep_test");
const APP = APPDIR.replace(/\\/g, "/") + "/practice.html";

fs.mkdirSync(APPDIR, { recursive: true });
fs.copyFileSync(path.join(SRC, "practice.html"), path.join(APPDIR, "practice.html"));
fs.copyFileSync(path.join(SRC, "bank.js"), path.join(APPDIR, "bank.js"));

const html = fs.readFileSync(path.join(APPDIR, "practice.html"), "utf-8");
const dom = new JSDOM(html, {
  runScripts: "dangerously",
  resources: "usable",
  url: "file:///" + APP,
  pretendToBeVisual: true,
  beforeParse(window) {
    // jsdom treats file: origins as opaque; provide a working localStorage stub
    const store = new Map();
    Object.defineProperty(window, "localStorage", {
      value: {
        getItem: k => (store.has(k) ? store.get(k) : null),
        setItem: (k, v) => store.set(k, String(v)),
        removeItem: k => store.delete(k),
        clear: () => store.clear(),
      },
      configurable: true,
    });
    window.confirm = () => true; // auto-accept dialogs in tests
    window.alert = () => {};
  },
});
const { window: w } = dom;
const doc = w.document;
let failures = 0;
const check = (name, cond) => {
  console.log((cond ? "PASS" : "FAIL") + " - " + name);
  if (!cond) failures++;
};

setTimeout(() => {
  try {
    check("bank loaded (148 questions)", w.eval("bank.length") === 148);
    check("every question has explanation", w.eval("bank.every(q => q.expl && q.expl.length > 20)"));
    check("every question has concept", w.eval("bank.every(q => q.concept && q.concept.length > 2)"));
    check("12 concepts present", w.eval("new Set(bank.map(q => q.concept)).size") === 12);
    check("home stats rendered", doc.getElementById("homeStats").textContent.includes("0/148"));

    // ---- exam sim: 30 Q / 40 min ----
    w.eval("startExam()");
    check("exam: 30 questions", w.eval("state.qs.length") === 30);
    check("exam: 40-minute timer (40:00)", doc.getElementById("timer").textContent === "40:00");
    check("back button present in quiz", !!doc.querySelector("#quiz .bar .btn.secondary"));

    // answer 5 exam questions correctly (handle multi-select questions)
    for (let i = 0; i < 5; i++) {
      w.eval(`state.idx = ${i}; renderQ();`);
      const answers = w.eval("state.qs[state.idx].answers");
      if (answers.length > 1) {
        for (const a of answers) w.eval(`pick(${a}, true)`);
        w.eval("submitMulti()");
      } else {
        w.eval(`pick(${answers[0]}, false)`);
      }
      check("exam feedback rendered (q" + (i+1) + ")", doc.getElementById("fb").textContent.startsWith("✅"));
      w.eval("nextQ()");
    }

    // ---- explain panel (answer current question to reveal it) ----
    w.eval("renderQ(); var _ea = state.qs[state.idx].answers[0]; pick(_ea, false);");
    check("explain button rendered", doc.getElementById("explainBox").textContent.includes("▼ Explain"));
    const btn = doc.querySelector("#explainBox button");
    const panel = doc.querySelector("#explainBox .expl-panel");
    check("explain panel starts hidden", panel.classList.contains("hidden"));
    btn.click();
    check("explain panel toggles open", !panel.classList.contains("hidden"));
    check("explain text mentions correct marker", panel.textContent.includes("✅"));
    btn.click();
    check("explain panel toggles closed", panel.classList.contains("hidden"));

    // ---- flag checkbox ----
    const flagChk = doc.getElementById("flagChk");
    check("flag checkbox present", !!flagChk);
    flagChk.checked = true;
    w.eval("toggleFlag()");
    check("flag persisted", Object.keys(JSON.parse(w.localStorage.getItem("pcep_practice_stats_v1")).flagged).length === 1);
    flagChk.checked = false;
    w.eval("toggleFlag()");
    check("flag unflagged", Object.keys(JSON.parse(w.localStorage.getItem("pcep_practice_stats_v1")).flagged).length === 0);

    // ---- back button (drill mode) ----
    w.eval("backOut()");
    check("back returns to home", !doc.getElementById("home").classList.contains("hidden"));

    // ---- full drill: answer all 148 correctly ----
    w.eval('startDrill("all")');
    const n = w.eval("state.qs.length");
    check("full drill: 148 questions", n === 148);
    let multiCount = 0;
    for (let i = 0; i < n; i++) {
      w.eval(`state.idx = ${i}; renderQ();`);
      const answers = w.eval("state.qs[state.idx].answers");
      if (answers.length > 1) {
        multiCount++;
        for (const a of answers) w.eval(`pick(${a}, true)`);
        w.eval("submitMulti()");
      } else {
        w.eval(`pick(${answers[0]}, false)`);
      }
      const fb = doc.getElementById("fb").textContent;
      if (!fb.startsWith("✅")) {
        const qid = w.eval("state.qs[state.idx].id");
        console.log("UNEXPECTED WRONG at question id", qid, ":", fb.slice(0, 80));
        failures++;
        break;
      }
      w.eval("nextQ()");
    }
    check("multi-select flow exercised (14 questions)", multiCount === 14);
    const stats = JSON.parse(w.localStorage.getItem("pcep_practice_stats_v1"));
    check("all 148 marked seen", Object.keys(stats.seen).length === 148);
    check("run history logged (drill run recorded)", stats.history.length === 1 && stats.history[0].correct === 148);

    // ---- wrong-answer path + blank spot ----
    w.localStorage.setItem("pcep_practice_stats_v1", JSON.stringify({seen:{}, correct:{}, wrong:{}, history:[], flagged:{}, log:[]}));
    w.eval('startDrill("multi")');
    w.eval("var _q0 = state.qs[state.idx]; var _wIdx = _q0.options.map(function(_, i){return i;}).find(function(i){return !_q0.answers.includes(i);}); pick(_wIdx, false);");
    check("wrong answer flagged", doc.getElementById("fb").textContent.startsWith("❌"));
    check("feedback styled bad", doc.getElementById("fb").className.includes("bad"));
    check("blank spot recorded", w.eval("blankSpotIds().length") === 1);

    // ---- blank-spot drill ----
    w.eval('startDrill("blank")');
    check("blank drill contains missed question", w.eval("state.qs.some(q => q.id === _q0.id)"));
    w.eval('goHome()');

    // ---- flagged drill ----
    w.eval('startDrill("all")');
    w.eval("state.idx = 0; renderQ();");
    doc.getElementById("flagChk").checked = true;
    w.eval("toggleFlag()");
    w.eval('goHome()');
    w.eval('startDrill("flagged")');
    check("flagged drill has 1 question", w.eval("state.qs.length") === 1);
    w.eval('goHome()');

    // ---- stats screen ----
    w.eval("showStats()");
    check("stats screen visible", !doc.getElementById("statsScr").classList.contains("hidden"));
    check("concept table rendered (12 rows)", doc.querySelectorAll("#statsBody table.cpt tr").length >= 13);
    check("flagged section rendered", doc.getElementById("statsBody").textContent.includes("Your Flagged Blind Spots"));
    check("run history rendered", doc.getElementById("statsBody").textContent.includes("Run History"));
    check("per-question detail exists", doc.getElementById("statsBody").textContent.includes("per-question detail"));
    w.eval('goHome()');

    // ---- readiness ----
    const rd = w.eval("readiness()");
    check("readiness computed", typeof rd === "number");

    // ---- flashcards ----
    check("flashcards loaded (138)", w.eval("PCEP_FLASHCARDS.length") === 138);
    w.eval("startFlashcards()");
    check("flash view visible", !doc.getElementById("flash").classList.contains("hidden"));
    check("card 1 question rendered", doc.getElementById("fcQ").textContent.length > 3);
    check("answer hidden before reveal", doc.getElementById("fcA").classList.contains("hidden"));
    w.eval("revealCard()");
    check("answer revealed", !doc.getElementById("fcA").classList.contains("hidden"));
    check("rate buttons visible after reveal", !doc.getElementById("fcKnown").classList.contains("hidden"));
    const beforeLen = w.eval("fc.deck.length");
    w.eval("rateCard(0)"); // 'again' re-queues the card
    check("'again' re-queues card", w.eval("fc.deck.length") === beforeLen + 1);
    check("card advanced", w.eval("fc.idx") === 1);
    w.eval("revealCard()");
    w.eval("rateCard(1)");
    check("'known' advances card", w.eval("fc.idx") === 2);
    const fcstats = JSON.parse(w.localStorage.getItem("pcep_practice_stats_v1")).fc;
    check("flashcard stats persisted", fcstats && Object.keys(fcstats.again).length === 1 && Object.keys(fcstats.known).length === 1);
    w.eval('goHome()');

    console.log(failures === 0 ? "ALL FUNCTIONAL TESTS PASSED (v2)" : failures + " FAILURES");
    w.close();
    process.exit(failures ? 1 : 0);
  } catch (e) {
    console.log("TEST CRASH:", e.message);
    console.log((e.stack || "").split("\n").slice(0, 5).join("\n"));
    process.exit(1);
  }
}, 400);
