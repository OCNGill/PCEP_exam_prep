# Flashcard Rebuild Report — 2026-09-20

## Decision

The 138-card KimWynne class deck was **retired**. It was open-ended class Q&A,
not an exam-scoped deck: it mixed Python basics with SciPy and data-science
material and carried no mapping to the PCEP objectives. A learner could not tell
which cards actually represented the certification exam.

## Replacement

The shipped deck is **100 cards** derived from the active PCEP-30-02 syllabus,
distributed 25 per official block:[1]

| Block | Cards | Focus |
|---|---:|---|
| 1 | 25 | Computer programming and Python fundamentals |
| 2 | 25 | Control flow |
| 3 | 25 | Data collections |
| 4 | 25 | Functions and exceptions |

Each card carries:

- `objective` — e.g. `PCEP-30-02 3.2`
- `topic` — e.g. `Block 3 · Tuples`
- `source_url` — official syllabus
- `practice_url` — w3resource practice cross-reference[2]
- `verification` — `execution-verified` or `syllabus-reviewed`

## Exclusions

The deck validator rejects cards whose question or answer contains out-of-scope
material: SciPy, pandas, NumPy, data science, machine learning, and CSV tooling.
Those topics are outside the PCEP-30-02 objectives.

## Verification

`build_flashcards_v2.py` validates every card before writing `flashcards.json`
and `bank.js`:

- exactly 100 cards;
- unique questions;
- valid objective IDs and official/practice source URLs;
- no out-of-scope terms;
- 25/25/25/25 block distribution;
- every code card executes with the expected output or expected exception
  (isolated subprocess, 3-second timeout).

`test_practice.js` then verifies the app end to end: **50/50 checks passing**,
including deck count, objective metadata, out-of-scope exclusion, and flashcard
UI rendering.

## Reproduce

```bash
python build_flashcards_v2.py
node test_practice.js
```

## Sources

[1] https://pythoninstitute.org/pcep-exam-syllabus — Python Institute PCEP-30-02 exam syllabus
[2] https://www.w3resource.com/python/certificate/index.php — w3resource PCEP certification preparation guide
