# CHANGELOG

All notable changes to the PCEP Rapid Practice system.
Format: Keep-a-Changelog-ish, newest first.

## [2.3.1] — 2026-10-14

### Fixed
- **Arithmetic chains in explanations** — Commander: *"how the FUCK did it
  calculate 17.5?"* Walkthroughs no longer echo the source and jump to the
  final value. Every compound expression now breaks into operand-by-operand
  intermediate steps. Q36 now reads:
  `4 ** 2 = 16 · 1 / 2 = 0.5 · 3 // 3 = 1 · 0.5 + 1 = 1.5 · 1.5 + 16 = 17.5`.
  Chains are dependency-safe (each value is computed before it is used) and
  precedence-first (highest-ready operator emits first — the exponent shows
  even though it sits rightmost in source). Wired into assignments,
  augmented assignments, `return`, `print()` arguments and bare expressions;
  single-operation lines and non-arithmetic syntax keep the prior rendering.
  Safe builtins render as their own step (`len('abc') = 3`).

### Verified
- `node test_practice.js` → **70/70 checks** (+2: Q36 chain contains the
  17.5 derivation; chain order is PEMDAS + dependency-safe).
- `validate2.py` → 0 mismatches; `regen_walkthroughs.py` → 58/58,
  0 trace failures, 0 fallback phrases.

**Verse:** *"The beginning of wisdom is this: Get wisdom, and whatever you
get, get insight." — Proverbs 4:7 (ESV).* Chosen because the walkthroughs now
hand over the insight — every intermediate step — instead of just the answer.

## [2.3.0] — 2026-10-14

### Fixed
- **v2.2.0 explanation regression repaired (Commander caught it live).** The
  2.2.0 chain ran `build_bank_v2.py` WITHOUT `regen_walkthroughs.py` afterward;
  that builder regenerates `pcep_bank.json` from scratch, silently reverting
  all **58 execution-verified explanations** to the lazy
  `live-verified by executing the snippet: actual output is 'X'` fallback.
  All 58 walkthroughs restored — 0 trace failures, 0 fallbacks remaining.
  Chain order is now locked in `conductor/tracks.md`, and `build_bank_v2.py`
  prints a loud NOTE pointing at the required regen step.

### Added
- **WHY annotations in the trace engine** (learning-grade walkthroughs):
  - sequence concatenation shows lengths adding:
    `tup = (1,1) + (1,1) = (1,1,1,1)  [concatenation: 2 elements + 2 elements = 4 elements]`
  - `print(len(x))` shows the real value: `tup = (1,1,1,1), len = 4 → prints '4'`
  - numeric promotion annotated: `123 + 0.0 → evaluates to 123.0  [type promotion: int + float → float]`
  - bare expression statements are now evaluated instead of echoing source.
- **📈 Blind-spot trends card on Home**: run-accuracy sparkline (last 6 runs),
  momentum (last 20 vs prior 20 answers), concept drift (⚠ worsening /
  ✓ improving vs the earlier half of your answer log), and a count of
  🆕 newly-blind questions. Empty state until enough data exists.
- **Universal 🏠 Home top-nav** on every screen (quiz, flashcards, results,
  statistics); abandoning a live exam sim still requires the confirm guard.
- **Resumable drills** — Full Drill and every other drill persists question
  order, position, answers and revealed state to localStorage on every answer,
  advance, and leave. Home then offers `▶️ Continue … — Question N/148` plus
  `🔁 Restart`. Completing or resetting clears the saved state. Exam sims are
  deliberately NOT persisted (the 40-minute clock is a single sitting).

### Verified
- `node test_practice.js` → **68/68 checks**, including a fresh-JSDOM
  kill-tab simulation: instance 2 over the same storage sees
  `Continue … Question 7/148`, resumes at idx 6 with identical question order,
  answers and reveal state, and does not double-count statistics.
- `validate2.py` → 0 mismatches; `regen_walkthroughs.py` → 58/58 walkthroughs,
  0 trace failures.

**Verse:** *"…forgetting what lies behind and straining forward to what lies
ahead, I press toward the goal…" — Philippians 3:13–14 (ESV).* Chosen because
the drill now lets you press on from exactly where you stopped, while the
trends card keeps your eyes forward on what is slipping.

## [2.2.0] — 2026-09-20

### Added
- **PCEP-only flashcard deck rebuilt** (`build_flashcards_v2.py`): 100 cards
  mapped to the official PCEP-30-02 objectives — 25 fundamentals, 25 control
  flow, 25 data collections, 25 functions/exceptions.
- Every card carries `objective`, `topic`, `source_url`, `practice_url`, and
  `verification` metadata; the trainer displays the objective and topic above
  each card.
- Code cards are execution-verified in an isolated subprocess during the deck
  build (timeout-guarded); expected output or exception mismatch fails the build.
- Deck validator rejects non-PCEP material (SciPy, pandas, NumPy, data science,
  CSV tooling) and enforces 100-card count, unique questions, valid objective
  IDs, and 25/25/25/25 block distribution.

### Changed
- **Retired the 138-card KimWynne class deck.** It mixed SciPy/data-science
  material with Python basics and carried no objective mapping, so it did not
  represent the PCEP exam.
- `bank.js` now carries both the 148-question MCQ bank and the 100-card
  PCEP-only deck with source metadata.
- README, Conductor state, tracks, and shared-drive ingestion report updated to
  document the rebuild and the source provenance.

### Verified
- `python build_flashcards_v2.py` → 100 validated PCEP-only flashcards, block
  distribution 25/25/25/25.
- `node test_practice.js` → **50/50 checks passing**, including deck count,
  objective metadata, out-of-scope exclusion, and flashcard UI rendering.

**Verse:** *"But test everything; hold fast what is good." — 1 Thessalonians 5:21.*
Chosen because the old deck was not defended — it was tested against the official
exam scope, the off-scope cards were removed, and only what held up was kept.

## [2.1.1] — 2026-09-17

### Changed
- **Explanations rebuilt as code walkthroughs** (Commander directive: the
  boilerplate "does not match the verified output" notes were useless).
  New trace engine (`trace_engine.py` + `regen_walkthroughs.py`) executes each
  snippet line-by-line under sys.settrace and generates real arithmetic:
  - assignments shown as equations: `a = a ^ b → a = 1 ^ 0 = 1`
  - list mutations shown as state evolution: `insert(1, …) → my_list becomes [1, 1, 2, 3]`
  - loop-count questions summarized pass-by-pass: `var 0 → becomes 1 → prints '#'` / `skipped (continue)`
  - recursion traced call-by-call with substituted arguments and return values
  - augmented assignments computed: `s += t[i][i] → s = 3 + (t[1][1]) = 5`
  - wrong options now explained contextually: intermediate values are called
    out as traps ("this appears around step 5, but the program ends at '1'")

### Verified
- 48/48 functional tests passing; all 58 execution-verified questions
  regenerated (0 trace failures).

**Verse:** *"Give me understanding, that I may observe your law and follow it
with all my heart." — Psalm 119:34.* Chosen because the Commander asked for
understanding of the logic, not memorized outputs — understanding is what
makes knowledge stick.

## [2.1.0] — 2026-09-17

### Added
- **Class shared-drive ingestion** (`ingest_v2.py`): swept Rich's NTAI shared
  drive — last 2 years of test data (2024Q4, 2025Q2, 2025Q4, PCAP practice,
  loose exports). Result: **all 340+ parsed questions were duplicates of the
  existing pool** — the library already contained the full PE1 question bank.
  Zero new MCQs; zero lost.
- **🃏 Flashcard Drill**: 138 open-ended KimWynne class Q&A cards (basics +
  scipy/data-science) as a new deck mode — show question, reveal answer,
  mark known/again ("again" re-queues the card), stats persisted.
- **Third-validation cross-check** vs the EDU "correct answers" study notes:
  6 agreements; 2 disagreements were EDU file errors (the EDU notes contradicted
  both our live-executed output and their own explanation text — and disagreed
  with each other). Our execution-verified key stands.

### Verified
- 48/48 headless functional tests passing (37 prior + 11 flashcard checks).

**Verse:** *"Iron sharpens iron, as one person sharpens another." — Proverbs 27:17.*
Chosen because the EDU cross-check sharpened our confidence: independent sources
were tested against each other, and only verified truth survived.

## [2.0.0] — 2026-09-12

### Added
- Exam simulation re-scoped to the REAL PCEP format: **30 questions / 40 minutes**
  (verified against pythoninstitute.org; real pass bar 70%, sim trains at 75%).
- **▼ Explain panel** on every question: expandable breakdown of the correct
  answer AND each incorrect option. 58 execution-verified + 90 expert-written.
- **⚑ Flag-for-review checkbox** — user-flagged questions persist and feed a
  personal blind-spot system, aggregated per concept, with a dedicated drill.
- **Statistics & Blind-Spot Analysis screen**: per-question accuracy detail
  (148 rows), per-concept table (12 concepts: BLANK SPOT / WEAK / SOLID / UNSEEN),
  run history, readiness metric (rolling last-50 accuracy).
- **Blank-Spot Drill (algorithmic)** — targets accuracy < 70% or any miss.
- **Flagged Drill (user-perceived blind spots)**.
- **Back button** in quiz and results views (exam abandon guarded by confirm).
- Run history logging + rolling readiness metric (90% = exam-ready zone).
- Dual-validation pass 2 (`validate2.py`): independent re-execution of all
  executable snippets with automatic option matching — **0 mismatches**.
- Headless regression suite expanded 16 → 37 checks (all passing).

### Changed
- Concept tags added to all 148 questions (12 concepts).
- Trainer rewritten as v2 (bank v2: answers + explanations + concepts).

### Verified
- `validate2.py`: 58/58 executable answers machine-confirmed, duplicate-group
  consistency clean, multi-select structural checks clean.
- Q104 try-except item cross-checked against the official PE1 Module 4 key.

**Verse:** *"Whatever you do, work at it with all your heart, as working for the
Lord, not for human masters." — Colossians 3:23.* Chosen because every answer in
this bank was re-verified and documented as if the examiner Himself would read it.

## [1.0.0] — 2026-09-12

### Added
- Initial build from 10 raw NTAI PE1 exports (169 questions → 148 unique).
- Answer key derived (raw exports contain no answer keys — deep field scan).
- Pass-1 verification: 94 snippets executed in sandboxed subprocesses; 2
  provisional answers corrected by live execution (Q91, Q122).
- Trainer v1: exam sim, drill all, weak-spot drill, multi-select focus, stats
  persistence. 16/16 functional tests passing.

**Verse:** *"The fear of the LORD is the beginning of wisdom." — Proverbs 9:10.*
Chosen because honest telemetry (admitting the exports had no answer key) is
where real wisdom in this build started.
