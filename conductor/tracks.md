# Tracks — PCEP_exam_prep

## Active
- v2.4.0 shipped: stats IMPORT (merge-default / replace-confirm with source
  date) + Home version stamp — Phase 1 Android/Drive sync half; pairs with
  1130ac's Export for phone <-> laptop carry-across — 85/85 green.
  Single-file packager SHIPPED (Geordi): PCEP_Trainer_v2.4.0.html
  (202,383 B, sha256 41822e0c..., verify_singlefile.js 15/15,
  0 external refs) — the Drive/Droid artifact. Next: Drive push.
- v2.3.2 shipped: run-controls triad (Continue / New Full Run with ADDITIVE
  stats / Reset ALL last), results-screen New Full Run chain button, stats
  Export JSON button (committed from session 1130ac's explicit handoff),
  regen determinism fix (memory-address reprs stripped — byte-identical
  regens) — 80/80 green.
- v2.3.1 shipped: arithmetic chains in all 58 walkthroughs (operand-by-operand
  intermediate values, dependency-safe + precedence-first PEMDAS emission) —
  70/70 green.
- v2.3.0 shipped: 58 WHY-walkthroughs restored (v2.2.0 regression), home
  blind-spot trends, universal Home nav, resumable drills — 68/68 green.

## Next
- Sandra/Steve first real run-through → seed flag + accuracy data
- Optional: spaced-repetition scheduling (Leitner boxes) layered on the blank-spot drill
- Optional: daily miss report (export/print)

## Future
- PE2 (PCAP) question bank when Rich supplies the data
- Android delivery via the Gillsystems Commander app

## Rules
- No commit without, IN THIS ORDER: build_bank_v2.py (only if raw/key changed)
  → **regen_walkthroughs.py (MANDATORY after any build_bank_v2 run — it wipes
  the 58 walkthroughs back to fallback text; this exact omission shipped the
  v2.2.0 regression)** → build_flashcards_v2.py clean → validate2.py 0
  mismatches → node test_practice.js all green → CHANGELOG + conductor updated.
