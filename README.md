# PCEP Exam Prep — Rapid Practice System

**Mission (per Rich Lysakowski, Ph.D. — Network Technology Academy Institute):**
raw data → passed PCEP certification exam in 30 days or less.

**Target:** pass the real PCEP (30 questions / 40 minutes, 70% to pass) — and
train to **> 90% knowledge** through repeated, targeted run-throughs that cement
the right answers.

**Status: OPERATIONAL.** 148-question verified bank · 100-card PCEP-only flashcard
deck · every answer dual-validated · 50/50 functional regression tests green.

---

## How to launch

Double-click **`start_practice.bat`** (opens the trainer in your default browser),
or open `practice.html` directly. Nothing to install; progress persists in the
browser (localStorage).

## Training modes

| Mode | What it does |
|---|---|
| ⏱ Exam Simulation | **30 questions / 40 minutes** — mirrors the real PCEP sitting; pass bar 75% (above the real 70%) |
| 🔁 Drill All | All 148 questions, instant feedback + explanations, reshuffled every run |
| 🎯 Blank-Spot Drill (algorithmic) | Questions the engine flagged: accuracy < 70% or any miss |
| ⚑ Flagged Drill (your blind spots) | Every question YOU ticked with the ⚑ checkbox |
| ☑ Multi-Select Focus | The 14 "Select two answers" questions — the classic PCEP trap |
| 🃏 Flashcard Drill | 100 PCEP-only cards mapped to official PCEP-30-02 objectives (reveal, know/again, re-queue) |
| 📊 Statistics & Blind-Spot Analysis | Per-question + per-concept accuracy, run history, 90% readiness |

## Answer quality engine

- **⚑ Flag for review** — during any drill, tick the checkbox on questions you
  doubt. Flagged questions aggregate into concept-level blind spots and get
  their own drill. Your perception + the algorithm, combined.
- **▼ Explain** — every question has an expandable explanation covering the
  correct answer AND each wrong option.
- **Readiness (last 50)** — rolling accuracy over your 50 most recent answers;
  ≥ 90% = exam-ready zone.
- **Concept analysis** — all 148 questions tagged into 12 concepts (Lists,
  Functions, Operators & Math, Exceptions, …), each scored and statused:
  BLANK SPOT / WEAK / SOLID / UNSEEN.

## Flashcard deck (PCEP-only)

- **100 cards**, 25 per official PCEP-30-02 block: Python fundamentals, control
  flow, data collections, and functions/exceptions.[1]
- Every card carries its objective ID, topic, source URL, and verification
  status, so an off-scope or unverified card cannot hide in the deck.
- Code cards are executed in an isolated subprocess by `build_flashcards_v2.py`;
  the build fails if any expected output or exception does not match.
- Non-PCEP material (SciPy, pandas, NumPy, data science, CSV tooling) is
  rejected by the deck validator and is not present in the shipped deck.
- Practice cross-reference: the w3resource PCEP preparation guide.[2]

## Answer key integrity (dual validation)

1. **Pass 1 — construction:** answer key derived from PCEP domain knowledge;
   94 code snippets executed in sandboxed subprocesses (`verify_snippets.py`).
   Two provisional answers were corrected by live execution (Q91, Q122).
2. **Pass 2 — independent verification** (`validate2.py`): every executable
   snippet re-run in a fresh process, outputs auto-matched against option text
   (direct, containment, numeric, word-number), compared to the key.
   **Result: 58/58 executable answers machine-confirmed, 0 mismatches.**
   Duplicate-question consistency: no conflicts. Multi-select structure: all 14
   have exactly 2 correct answers.
3. The remaining 90 questions are concept/definition items (no code to
   execute); each was re-derived and documented with per-option explanations,
   and cross-checked against duplicate phrasings and the official PE1 answer
   key (e.g. the try-except "select two" item).

**Honest disclosure:** the raw vendor exports contain **no answer keys**
(verified by deep field scan — `showAnswers` false, no correct/answer fields
anywhere). The key is derived, not extracted. Any answer that looks wrong in
review: flag it and verify.

## The 30-day plan (target: > 90% before exam day)

1. **Days 1–7:** Drill All daily (two passes). Open every ▼ Explain on misses.
2. **Days 8–14:** Blank-Spot Drill + Multi-Select Focus daily; one exam sim.
3. **Days 15–21:** Daily exam sim; ⚑ flag anything you hesitate on; drill flags.
4. **Days 22–29:** One exam sim per day until 5 consecutive sims ≥ 85% and
   Readiness (last 50) holds ≥ 90%.
5. **Day 30:** Sit the real exam (30Q / 40 min / 70% to pass) — over-prepared.

## Repository layout

```
PCEP_exam_prep/
├── practice.html           # the trainer app (open in browser)
├── bank.js                 # question bank + answers + explanations + flashcards (file://-safe)
├── pcep_bank.json          # same data, JSON form
├── flashcards.json         # 100 PCEP-only cards with objective + source metadata
├── build_flashcards_v2.py  # flashcard deck builder + validator (executes code cards)
├── start_practice.bat      # double-click launcher
├── verify_snippets.py      # pass-1 answer verification harness
├── validate2.py            # pass-2 independent dual-validation harness
├── ingest_v2.py            # shared-drive ingestion (v3 sweep, dedupe vs library)
├── build_bank.py           # pass-1 bank builder
├── build_bank_v2.py        # v2 bank builder (key + explanations + concepts)
├── bank_raw.json           # intermediate: deduped bank before keying
├── exec_results.json       # pass-1 recorded outputs
├── exec_answers_pass2.json # pass-2 exec-derived answer indices
├── test_practice.js        # headless functional regression suite (50 checks)
├── raw_data/               # untouched original NTAI exports (10 files)
├── conductor/conductor.md  # 7D Conductor: product definition, state, tracks
└── CHANGELOG.md
```

## Regenerating / extending the bank

1. Add/drop exports in `raw_data/`, regenerate the raw bank (extraction preserves
   `<code class="codep">` blocks for indentation fidelity)
2. `python build_bank_v2.py` — fails loudly if any question lacks key or explanation
3. `python build_flashcards_v2.py` — validates the 100-card PCEP-only deck and
   rebuilds both `flashcards.json` and `bank.js`
4. `python validate2.py` — must report 0 mismatches
5. `node test_practice.js` — must report all tests passed

---

*"All hard work brings a profit, but mere talk leads only to poverty." — Proverbs 14:23*

## Sources

[1] https://pythoninstitute.org/pcep-exam-syllabus — Python Institute PCEP-30-02 exam syllabus
[2] https://www.w3resource.com/python/certificate/index.php — w3resource PCEP certification preparation guide
