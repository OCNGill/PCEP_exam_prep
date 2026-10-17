/* Functional regression suite v2 for practice.html (jsdom, headless).
   Covers: bank load, explanations/concepts coverage, 30Q/40min exam, back
   button, explain panel, flag checkbox, full drill, multi-select, stats
   persistence, wrong path, blank-spot drill, flagged drill, stats screen,
   run history, readiness. */
const fs = require("fs");
const path = require("path");
const { JSDOM } = require("jsdom"); /* repo node_modules — %TEMP% copy dies to temp sweeps */

const SRC = __dirname; /* portable — no filesystem usernames in the repo */
const APPDIR = path.join(process.env.TEMP, "pcep_test");
const APP = APPDIR.replace(/\\/g, "/") + "/practice.html";

fs.mkdirSync(APPDIR, { recursive: true });
fs.copyFileSync(path.join(SRC, "practice.html"), path.join(APPDIR, "practice.html"));
fs.copyFileSync(path.join(SRC, "bank.js"), path.join(APPDIR, "bank.js"));

const html = fs.readFileSync(path.join(APPDIR, "practice.html"), "utf-8");
// Shared store across JSDOM instances: simulates "kill the tab, reopen" with
// the same persisted localStorage (same file:// origin behavior as Chrome).
const store = new Map();
const lsValue = () => ({
  getItem: k => (store.has(k) ? store.get(k) : null),
  setItem: (k, v) => store.set(k, String(v)),
  removeItem: k => store.delete(k),
  clear: () => store.clear(),
});
const mkDom = () => new JSDOM(html, {
  runScripts: "dangerously",
  resources: "usable",
  url: "file:///" + APP,
  pretendToBeVisual: true,
  beforeParse(window) {
    Object.defineProperty(window, "localStorage", { value: lsValue(), configurable: true });
    window.confirm = () => true; // auto-accept dialogs in tests
    window.alert = () => {};
  },
});
const dom = mkDom();
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
    check("Q36 explain shows arithmetic chain to 17.5",
      w.eval("bank.find(q => q.id === 36).expl.includes('4 ** 2 = 16') && bank.find(q => q.id === 36).expl.includes('3 // 3 = 1') && bank.find(q => q.id === 36).expl.includes('1.5 + 16 = 17.5')"));
    check("Q36 chain ordered PEMDAS + dependency-safe",
      w.eval("(e => e.indexOf('4 ** 2 = 16') < e.indexOf('1 / 2 = 0.5') && e.indexOf('1 / 2 = 0.5') < e.indexOf('0.5 + 1 = 1.5') && e.indexOf('4 ** 2 = 16') < e.indexOf('1.5 + 16 = 17.5'))(bank.find(q => q.id === 36).expl)"));
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
    check("flashcards loaded (100 PCEP-only cards)", w.eval("PCEP_FLASHCARDS.length") === 100);
    check("flashcards have PCEP objective metadata", w.eval("PCEP_FLASHCARDS.every(c => c.id && c.objective.startsWith('PCEP-30-02 ') && c.source_url && c.practice_url)"));
    check("flashcards exclude non-PCEP topics", !w.eval("PCEP_FLASHCARDS.some(c => /scipy|pandas|numpy|data science|machine learning|csv/i.test(c.q + ' ' + c.a))"));
    w.eval("startFlashcards()");
    check("flash view visible", !doc.getElementById("flash").classList.contains("hidden"));
    check("card 1 question rendered", doc.getElementById("fcQ").textContent.length > 3);
    check("card objective metadata rendered", doc.getElementById("fcMeta").textContent.includes("PCEP-30-02"));
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

    // ---- run controls triad on fresh home (no resume): New + Reset ALL, menu reset deduped ----
    w.localStorage.removeItem("pcep_drill_resume_v1");
    w.eval("renderHome()");
    const slot0 = [...doc.querySelectorAll("#resumeSlot .menu-btn")];
    const st0 = slot0.map(b => b.textContent).join(" | ");
    check("fresh home triad: no Continue without resume", !st0.includes("Continue"));
    check("fresh home triad: New Full Run present", st0.includes("New Full Run"));
    check("fresh home triad: Reset ALL present", st0.includes("Reset ALL"));
    check("fresh home triad: New before Reset ALL (wipe last)", st0.indexOf("New Full Run") < st0.indexOf("Reset ALL"));
    check("menu duplicate Reset Progress removed", ![...doc.querySelectorAll("#home .menu-btn")].some(b => b.textContent.includes("Reset Progress")));
    check("results screen offers New Full Run chain button", !!doc.querySelector("#results .bar button[onclick='newFullRun()']"));
    check("WiFi sync button mounted", !!doc.getElementById("syncBtn"));
    check("Export Stats removed (LAN sync only)", ![...doc.querySelectorAll("#home .menu-btn")].some(b => b.textContent.includes("Export Stats")));
    check("Import Stats removed (LAN sync only)", !doc.getElementById("importStatsBtn"));
    check("version stamp on Home shows v2.5.0", ((doc.getElementById("appVersion") || {}).textContent || "").includes("v2.5.0"));
    check("brand header logo present", !!doc.querySelector(".hdr-logo"));
    check("donation footer with PayPal link present", (doc.querySelector(".gill-footer") || {}).textContent.includes("paypal.me/gillsystems"));
    check("no baked-in private IP; host typed once per device then persisted", w.__pcepSyncHostDefault === "" && !/10\.0\.0\./.test(doc.documentElement.innerHTML));
    const seen0 = Object.keys(JSON.parse(w.localStorage.getItem("pcep_practice_stats_v1")).seen).length;
    [...doc.querySelectorAll("#resumeSlot .menu-btn")].find(b => b.textContent.includes("New Full Run")).click();
    check("fresh-home New starts a 148 run immediately", w.eval("state.mode") === "all" && w.eval("state.qs.length") === 148);
    check("fresh-home New preserves stats", Object.keys(JSON.parse(w.localStorage.getItem("pcep_practice_stats_v1")).seen).length === seen0);
    w.eval("clearResume(); goHome()");

    // ---- universal top-nav Home ----
    w.eval('startExam()');
    check("topnav visible in quiz", !doc.getElementById("topnav").classList.contains("hidden"));
    doc.querySelector("#topnav button").click(); // confirm auto-accepted
    check("topnav Home returns to home", !doc.getElementById("home").classList.contains("hidden"));
    check("topnav hidden on home", doc.getElementById("topnav").classList.contains("hidden"));

    // ---- home trends (seeded deterministically) ----
    const st = JSON.parse(w.localStorage.getItem("pcep_practice_stats_v1"));
    st.history = [];
    [50,55,60,65,70].forEach((p,i) => st.history.push({ts:"2026-10-1"+i+" 10:0"+i, mode:"all", correct:p, total:100, pct:p}));
    const lp = w.eval("bank.find(q => q.concept === 'Loops').id");
    st.log = [];
    for (let i = 0; i < 60; i++) {
      if (i < 10) st.log.push({id: lp, ok: 1});
      else if (i < 30) st.log.push({id: ((i*13)%148)+1, ok: 1});
      else if (i < 40) st.log.push({id: lp, ok: 0});
      else st.log.push({id: ((i*17)%148)+1, ok: (i%2)});
    }
    w.localStorage.setItem("pcep_practice_stats_v1", JSON.stringify(st));
    w.eval("renderHome()");
    const tr = doc.getElementById("trendsBody").textContent;
    check("trends: run accuracy sparkline", tr.includes("Run accuracy"));
    check("trends: momentum delta", tr.includes("Momentum"));
    check("trends: worsening blind spot flagged", tr.includes("Worsening blind spot"));

    // ---- drill resume: save → KILL INSTANCE → reopen shared storage ----
    w.localStorage.removeItem("pcep_drill_resume_v1");
    w.eval('startDrill("all")');
    const firstOrder = [];
    for (let i = 0; i < 6; i++) {
      w.eval(`state.idx=${i}; renderQ();`);
      firstOrder.push(w.eval("state.qs[state.idx].id"));
      const ans = w.eval("state.qs[state.idx].answers");
      if (ans.length > 1) { for (const a of ans) w.eval(`pick(${a},true)`); w.eval("submitMulti();"); }
      else w.eval(`pick(${ans[0]},false);`);
      w.eval("nextQ()");
    }
    check("drill paused at question 7 (idx 6)", w.eval("state.idx") === 6);
    w.eval("goHome()");
    const btns = [...doc.querySelectorAll("#resumeSlot .menu-btn")];
    check("home shows Continue at Question 7/148", btns.some(b => b.textContent.includes("Continue") && b.textContent.includes("Question 7/148")));
    const slotText1 = btns.map(b => b.textContent).join(" | ");
    check("home shows New Full Run option", slotText1.includes("New Full Run"));
    check("triad order: Continue, New, Reset ALL", slotText1.indexOf("Continue") < slotText1.indexOf("New Full Run") && slotText1.indexOf("New Full Run") < slotText1.indexOf("Reset ALL"));
    const seenBeforeResume = Object.keys(JSON.parse(w.localStorage.getItem("pcep_practice_stats_v1")).seen).length;

    // FRESH JSDOM over the SAME store = kill the tab and reopen it
    const dom2 = mkDom();
    setTimeout(() => {
      try {
        const w2 = dom2.window, doc2 = w2.document;
        const btns2 = [...doc2.querySelectorAll("#resumeSlot .menu-btn")];
        check("fresh instance sees Continue at Question 7/148", btns2.some(b => b.textContent.includes("Continue") && b.textContent.includes("Question 7/148")));
        w2.eval("resumeDrill()");
        check("resumed at idx 6", w2.eval("state.idx") === 6);
        check("resumed question order preserved", JSON.stringify(w2.eval("state.qs.slice(0,6).map(q=>q.id)")) === JSON.stringify(firstOrder));
        check("resumed answers preserved (6)", w2.eval("Object.keys(state.answers).length") === 6);
        check("resumed revealed preserved (6)", w2.eval("Object.keys(state.revealed).length") === 6);
        const seenAfter = Object.keys(JSON.parse(w2.localStorage.getItem("pcep_practice_stats_v1")).seen).length;
        check("resume does not double-count stats", seenAfter === seenBeforeResume);
        w2.eval("goHome()");
        const nb = [...doc2.querySelectorAll("#resumeSlot .menu-btn")].find(b => b.textContent.includes("New Full Run"));
        check("New Full Run button present after reopen", !!nb);
        const seenBeforeNew = Object.keys(JSON.parse(w2.localStorage.getItem("pcep_practice_stats_v1")).seen).length;
        if (nb) nb.click();
        check("New Full Run begins a fresh 148 run", w2.eval("state.idx") === 0 && w2.eval("state.mode") === "all" && w2.eval("state.qs.length") === 148);
        const seenAfterNew = Object.keys(JSON.parse(w2.localStorage.getItem("pcep_practice_stats_v1")).seen).length;
        check("New Full Run does NOT wipe stats (adds to ongoing data)", seenAfterNew === seenBeforeNew);
        w2.eval("goHome()");
        const cont1 = [...doc2.querySelectorAll("#resumeSlot .menu-btn")].find(b => b.textContent.includes("Continue"));
        check("after New run, Continue shows Question 1/148", !!cont1 && cont1.textContent.includes("Question 1/148"));
        dom2.window.close();
      } catch (e2) {
        console.log("TEST CRASH (instance 2):", e2.message);
        console.log((e2.stack || "").split("\n").slice(0, 4).join("\n"));
        failures++;
      }
      console.log(failures === 0 ? "ALL FUNCTIONAL TESTS PASSED (v2)" : failures + " FAILURES");
      w.close();
      process.exit(failures ? 1 : 0);
    }, 400);
  } catch (e) {
    console.log("TEST CRASH:", e.message);
    console.log((e.stack || "").split("\n").slice(0, 5).join("\n"));
    process.exit(1);
  }
}, 400);
