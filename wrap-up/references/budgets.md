# Doc economy: budgets and the anti-bloat audit

**Each fact lives in exactly one place; everything else points to it.** The homes are listed in SKILL.md's Overview table. If a future session can find the same fact in three or more places, prune until one copy remains.

Why this exists: without a fixed shape, every wrap-up surface accretes a paragraph per session "for completeness": the same content re-narrated four times and never removed. The next session reads all four and spends context relearning what one handoff already recorded. The observed end state is a CLAUDE.md whose first screen is a stack of per-session status blocks, each "collapsed" rather than removed.

## The audit table (Step 3.7 runs this)

| Surface | Budget | Bloat smell |
|---|---|---|
| **CLAUDE.md Current state slot** | One `## Current state` section, ≤150 words, the five parts in SKILL.md Step 4, replaced whole each wrap-up | A second status block anywhere in the file; "collapsed at sN" lines; the previous session's slot kept "for context"; a warning that has survived two wrap-ups |
| **CLAUDE.md outside the slot** | Rules, orientation, pointers. No session numbers except as provenance on a rule ("lead ruling s415") | Paragraphs that say what a session shipped or found |
| **Handoff index (`INDEX.md`)** | One row per arc; one-line outcome; one or two `Read first` links | Per-session rows; outcomes that grow into paragraphs |
| **MEMORY.md session log** | One line per session, recent ~5 only | Lines growing into paragraphs; the log reaching back dozens of sessions |
| **Thread tracker `done`/`parked` bodies** | ≤150 words: outcome (1 line) + locks added (1 line) + handoff link | 3–8 paragraph collapsed summaries |
| **Thread tracker `last-touched` lines** | 1–2 sentences pointing to the handoff | A restatement of what shipped |
| **ROADMAP.md "Last updated" + session blocks** | One line each | "Earlier (session N):" paragraphs accumulating |
| **Handoff doc** | ~750 words standalone; appendix below if needed | Mid-execution handoffs growing to 5K–10K tokens |

## Rules that govern the audit

1. Sweep **all** surfaces every wrap-up, not only the ones this session touched, because bloat accretes from prior sessions too. The cost is one grep.
2. **Collapse on ship.** The session a phase ships, its detail block compresses to the ≤150-word form actively, never by accretion.
3. **Active** thread and phase detail blocks are exempt; that is where the live working set lives. Budgets bind at ship time.
4. A log growing one *line* per session is fine where the budget allows it; the bloat is each line growing into a paragraph.
5. Over-budget handoffs: structure them so the first ~750 words stand alone (TL;DR + shipped + carry-forwards + read-first list); the rest is appendix. The `## Next session kickoff` section sits below that line and is exempt, like the appendix.
6. The session-start ritual loads two surfaces by default: the latest handoff and the thread board. Loading more is a user-chosen special case.
