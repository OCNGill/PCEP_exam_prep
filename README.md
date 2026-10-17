![Gillsystems Logo](assets/gillsystems_logo.png)

# Gillsystems PCEP Rapid Practice
> _"30 questions. 40 minutes. Train to >90% — one artifact, two devices, one record."_

![PCEP-30-02](https://img.shields.io/badge/Python%20Institute-PCEP--30--02-3776AB?logo=python)
![Bank](https://img.shields.io/badge/bank-148%20verified%20questions-4B8BBE)
![Flashcards](https://img.shields.io/badge/cards-100%20PCEP--only-4CAF50)
![Tests](https://img.shields.io/badge/tests-87%20app%20%C2%B7%2011%20sync%20%C2%B7%2015%20offline-brightgreen)
![Sync](https://img.shields.io/badge/sync-WiFi%20LAN%20%C2%B7%20manual%20%C2%B7%20backed%20up-FF9800)
![License](https://img.shields.io/badge/license-MIT-yellow)
[![Version](https://img.shields.io/badge/version-2.5.0-blue)](CHANGELOG.md)

**Gillsystems PCEP Rapid Practice** is a fully offline, single-file trainer for the Python Institute **PCEP-30-02** certification: a **148-question multiple-choice bank** whose code answers are verified by actual execution (58 with line-by-line walkthroughs and operand-by-operand arithmetic chains), a **100-card PCEP-only flashcard deck**, a real-format exam simulator (**30 questions / 40 minutes**), weak-spot analytics — and **manual two-way stats sync with your computer over home WiFi**: one backup of the record is always kept, and whichever device is behind gets added to.

**Status:** v2.5.0 — WiFi LAN sync live, single-file artifact verified offline (zero external references), 87 app checks + 11 sync-server checks + 15 single-file checks green. See [`CHANGELOG.md`](CHANGELOG.md).

## Contents
* [Overview](#overview)
* [Key Features](#key-features)
* [Quick Start](#quick-start)
* [WiFi Sync (manual, two-way, backed up)](#wifi-sync-manual-two-way-backed-up)
* [Stats, Drills & Readiness](#stats-drills--readiness)
* [Flashcards](#flashcards)
* [Testing](#testing)
* [Project Layout](#project-layout)
* [Privacy & Public Repo Policy](#privacy--public-repo-policy)
* [Support / Donate](#support--donate)

---

## Overview
Passing the real PCEP exam (30 questions, 40 minutes, official pass mark 70%) takes more than reading — it takes repeated, spaced, honest practice against the official syllabus. This trainer:

1. Presents the **official-syllabus 148-question bank** (12 concept areas) in drill or real-format exam mode.
2. Explains **every** answer — why the correct option is correct, why each distractor is wrong, with executed traces and step-by-step arithmetic for code output questions.
3. Measures exactly **where you are weak** (per-question, per-concept, trends, rolling last-50 readiness) and routes you to the right follow-up drill.
4. Keeps the record **synchronized between phone and computer** with a manual WiFi sync that never loses data: the server backs up before it writes, and the merge is add-only.

## Key Features
| Feature | Detail |
|---|---|
| **Execution-verified bank** | 148 questions; 58 code answers confirmed by running them (validate2.py: 58 confirmed, 0 mismatches) |
| **Deep walkthroughs** | Line-by-line WHY + operand-by-operand arithmetic chains (e.g. `4 ** 2 = 16 → 1 / 2 = 0.5 → 3 // 3 = 1 → 0.5 + 1 + 16 = 17.5`) |
| **Real exam format** | Exam Sim = 30 questions / 40 min countdown / 75% trainer bar (official pass = 70%) |
| **Run-controls triad** | ▶️ Continue (resume) · 🆕 New Full Run (additive) · ⚠️ Reset ALL (explicit, last) — stats are cumulative by default |
| **Weak-spot engine** | Per-question + per-concept stats, 🎯 Blank-Spot Drill, ⚑ Flagged Drill, blind-spot trends, rolling last-50 readiness |
| **WiFi LAN sync** | Manual, same-home-WiFi, two-way merge (whichever device is behind gets added), one backup always kept first |
| **Fully offline** | `file://` operation — single HTML file with everything inlined (zero external references) |
| **Flashcards** | 100 PCEP-only cards mapped to official objectives (25 per block), rate/re-queue persistence |
| **Branded** | Gillsystems header logo + donation footer — MIT licensed |

## Quick Start
**Just train (phone or computer):**
1. Grab `PCEP_Trainer_v2.5.0.html` (repo, or the shared Drive copy) — it is completely self-contained.
2. Open it in any modern browser. Add to Home Screen for an app-like icon. Works with no network at all.

**Develop / run the suite:**
```bash
git clone https://github.com/OCNGill/PCEP_exam_prep.git
cd PCEP_exam_prep
npm install jsdom          # test-only dependency (lives in repo node_modules)
python build_singlefile.py --output PCEP_Trainer_v2.5.0.html
node verify_singlefile.js PCEP_Trainer_v2.5.0.html
node test_practice.js
```

## WiFi Sync (manual, two-way, backed up)
Design rule: sync is **manual and only over the same home WiFi** — the phone can only sync when the laptop is present to see the request. No cloud sync path for stats; no hidden background traffic. It stays hands-on so you stay engaged with the learning process.

1. **Laptop:** start the server (port 8787 — never port 80):
   ```bash
   python pcep_sync_server.py
   ```
   Each incoming sync is logged to the console and `sync_server/sync.log`.
2. **Phone (same WiFi):** open the trainer → tap **📶 Sync (WiFi)** → enter the laptop address once (e.g. `192.168.1.10:8787`) — it is remembered per device.
3. The server then, in order: **backs up its current record** (`sync_server/backups/`, last 10 kept — a bad sync can never lose the record), **merges** (per-question highest count wins; history/log de-duplicated — whichever device is behind is added to), stores the master, and returns the merged record to the phone.
4. Both devices now hold the identical record — continue on either.

Stats never travel via Drive anymore; app updates ship as the new single-file artifact.

## Stats, Drills & Readiness
* Home card: totals, last-run line, trends sparkline + worsening-blind-spot flag.
* **🎯 Blank-Spot Drill** and **⚑ Flagged Drill** — the ranked follow-ups after a full 148 run.
* Rolling **last-50 readiness** targets a sustained >90% (trainer bar on runs: 75%).
* Everything persists in `localStorage` (stats format `pcep_practice_stats_v1`) — kill the tab, reopen, resume.

## Flashcards
100 cards, PCEP-30-02 objectives only (`PCEP-30-02 3.2` style IDs), 25 per block, Again/Known re-queue with persistence. Non-PCEP topics (pandas/NumPy/CSV) are excluded by the builder.

## Testing
Locked chain (run in order before any commit):
```bash
python regen_walkthroughs.py       # 58 walkthroughs, byte-deterministic, 0 failures
python build_flashcards_v2.py      # 100 cards validated, bank.js rebuilt
python validate2.py                # 58 execution-confirmed, 0 mismatches
node test_practice.js              # 87 app checks
python test_sync_server.py         # 11 sync/backup/merge checks
python build_singlefile.py --output PCEP_Trainer_v2.5.0.html
node verify_singlefile.js PCEP_Trainer_v2.5.0.html   # 15 offline checks, external refs []
```

## Project Layout
```
PCEP_exam_prep/
├── practice.html                 # the app (source form; bank.js sibling required)
├── PCEP_Trainer_v2.5.0.html      # single-file artifact — everything inlined
├── bank.js                       # 148 questions + 100 cards (generated)
├── pcep_bank.json                # bank source of truth
├── pcep_sync_server.py           # LAN sync server (port 8787, stdlib only)
├── assets/                       # Gillsystems logo + PayPal icon
├── build_singlefile.py           # packager: practice.html -> one file
├── verify_singlefile.js          # offline verification harness (15 checks)
├── test_practice.js              # jsdom app suite (87 checks)
├── test_sync_server.py           # sync/backup/merge unit tests (11 checks)
├── regen_walkthroughs.py         # deterministic explanation generator
├── build_flashcards_v2.py        # 100-card PCEP deck builder
├── validate2.py                  # execution validator (58 code answers)
├── trace_engine.py               # operand-by-operand arithmetic chains
├── CHANGELOG.md                  # release history (Ecclesiasts verses per release)
├── conductor/                    # 7D Conductor project tracking
└── README.md                     # this file
```

## Privacy & Public Repo Policy
This repository is **public**. Standing rules:
* **No personal data** — no home details, no private network addresses (`10.0.0.x` / public IPs banned; the sync host is typed once per device and never shipped).
* **No credentials** — API keys, tokens, and passwords never appear in any committed file.
* **Stats never committed** — `sync_server/` (masters, backups, logs) is gitignored; your record stays on your machines.
* **Branded, unbranded content is unacceptable** — every public doc carries the Gillsystems identity.

## Support / Donate
If this trainer helps you pass, you can support ongoing work — thank you!

**Donate:** [PayPal — paypal.me/gillsystems](https://paypal.me/gillsystems)

---
_Gillsystems · MIT License · Built for the fleet, shared with the crew._
