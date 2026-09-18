# CHANGELOG

All notable changes to the PCEP Rapid Practice system.
Format: Keep-a-Changelog-ish, newest first.

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
