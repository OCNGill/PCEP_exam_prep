# Shared-Drive Ingestion Report — 2026-09-17

Source: `G:\Shared drives\AI-Powered Data Analytics Training\01_PCEP-PCAP-Python_Certification_Practice`
Window: last 2 years (2024-09 → present). 2022 material excluded.

## Ingested (23 files staged to raw_data_v2/)

| Source dir | Files | Parsed |
|---|---|---|
| 0_PCEP-Practice-Tests_2024Q4 | 10 JSON exports | ✅ (TestInvitation) |
| 2025Q2_…Exam_QnAs | 1 JSON | ✅ |
| 2025Q4_…Exam_QnAs | 4 EDU raw JSONs + 1 Summary JSON | ✅ (after `let data =` unwrap) |
| root loose | Module-2 Test 2024.08.20 zip | ✅ |
| PCEP_KimWynne Q+A csv | 1 | ✅ (flashcards) |
| EDU Correct_Answers MDs | 5 | ✅ (cross-check only) |

## Result

- **340+ parsed TestInvitation questions — 100% duplicates of the existing
  library.** The 2024–2026 exports all draw from the same PE1 question pool.
  Zero new MCQs; zero lost. The 148-question bank remains complete.
- **138 flashcards** (KimWynne open-ended Q&A) → new Flashcard Drill mode.
- **EDU answer-key cross-check** (third validation signal):
  - 6 agree with our key.
  - 2 disagree — both are EDU-file errors on the print-quotes question
    (EDU contradicts our live-executed output, its own explanation text, AND
    itself across files: one marks B, another D). Our key (A) verified by
    execution stands.
  - 2 EDU stems not present in the bank (EDU-specific phrasings).
- **Zero-trust verdict:** the EDU "correct answers" MDs are AI-generated study
  notes, not official keys — used as cross-check signal only, never ingested
  as ground truth.

## Excluded (out of window / not test data)

- 2022_PCEP-PCAP_PE1-PE2_Examposter-QnAs (2022)
- PCAP practice PDF (2021)
- 5000-question MCQ rar/epub (bulk third-party book, not course test data)
- Quiz-app project folders (Streamlit, NodeJS, converters) — tooling, not data
- zzz-JUNK-2-DELETE
