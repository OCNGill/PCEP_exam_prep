# Conductor — PCEP_exam_prep

## Product Definition (product.md)

**Product:** PCEP Rapid Practice — a zero-install, browser-based rapid-practice
certification trainer that takes raw exam Q&A exports to a passed PCEP exam.

**Owner:** Commander Stephen Gill (OCNGill)
**Commissioned by:** Rich Lysakowski, Ph.D. (NTAI) — "raw data to passed exam in
30 days or less."

**Success criteria:**
1. Trainer mirrors the real exam: 30 questions / 40 minutes.
2. Answer key is dual-validated (execution + independent pass) with zero mismatches.
3. Repeated runs measurably cement correct answers: per-question and per-concept
   accuracy tracking, algorithmic + user-flagged blind spots, > 90% readiness metric.
4. Every question explains why each option is right or wrong.
5. All changes verified by the headless regression suite before commit.

## Current State (setup_state.json)

```json
{
  "version": "2.2.0",
  "date": "2026-09-20",
  "status": "OPERATIONAL",
  "bank": {"questions": 148, "unique_sources": 169, "multi_select": 14, "concepts": 12},
  "validation": {
    "pass1_execution_verified": 94,
    "pass2_machine_confirmed": 58,
    "pass2_mismatches": 0,
    "expert_reviewed": 90,
    "external_key_check": "Q104 confirmed vs official PE1 key"
  },
  "tests": {"suite": "test_practice.js", "checks": 50, "passing": 50},
  "features": [
    "exam sim 30Q/40min", "drill all", "blank-spot drill (algorithmic)",
    "flagged drill (user blind spots)", "multi-select focus",
    "flashcard drill (100 PCEP-only cards mapped to official objectives)",
    "explain panels (correct + incorrect options)",
    "per-question + per-concept statistics", "run history",
    "readiness rolling metric (last 50)", "flag checkbox persistence",
    "back button", "reset progress"
  ]
}
```

## Tracks (tracks.md)

### Active
- Flashcard deck rebuild complete: 100 PCEP-only cards, 25 per official block,
  source metadata on every card; 50/50 functional tests green (v2.2.0).

### Next
- Sandra/Steve first real run-through → seed flag + accuracy data
- Optional: spaced-repetition scheduling (Leitner boxes) on top of blank-spot drill
- Optional: export/print a daily miss report

### Future
- PE2 (PCAP) question bank when Rich supplies the data
- Android delivery via the Gillsystems Commander app
