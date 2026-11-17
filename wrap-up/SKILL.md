---
name: wrap-up
description: Use when ending a session that involved significant code changes, architectural decisions, merged PRs, schema migrations, or new subsystems — OR when the session produced a design, spec, audit or review that changed what is true about the system, even with no code changes. Also when the user signals session end ("wrap up", "we're done here", "start a new session", "move on to the next stage").
user-invocable: true
---

# Session Wrap-Up

## Overview

At session end, memory and docs drift from reality: CLAUDE.md describes refactored-away layouts, the roadmap says "in progress" for shipped work, one memory store gets updated and the other doesn't. The next session reads stale context and proposes stale plans. This skill is the sync pass that prevents that.

**Every fact has one home, and every other surface points to it.** The homes:

| Fact | Home |
|---|---|
| What a session did, found, and left open | That session's **handoff doc** |
| Which sessions belong to which arc, and which handoff to read for it | The **handoff index** (`<handoff dir>/INDEX.md`) |
| Where the work is right now and the next action | The **Current state slot** in CLAUDE.md (replaced each wrap-up) |
| Rules, locks, conventions | CLAUDE.md Hard Rules, or the spec / convention doc they point to |
| Lessons and preferences | Memory (auto-memory + second brain) |
| Open work | The thread tracker |

Session narrative has no home in CLAUDE.md. When CLAUDE.md grows a new status paragraph every session, that is the defect this skill exists to prevent. Budgets and the audit table: `references/budgets.md`. Read it before Step 3.7.

## When to use / skip

**Use:** the session shipped a PR, made architectural decisions, added or removed a major subsystem, or completed a plan. **Also use when the session produced a design, spec, audit or review that changed what is true about the system**, even with no code. Step 5's Pass B is the reason: a session that writes a spec and supersedes an old one has a large doc-sync surface and an empty diff.

**Skip:** an exploratory conversation that reached no conclusion; a single small fix (<10 lines, no architectural implication); pausing mid-work rather than ending.

"No code changed" is not a skip criterion. Judge by *did anything I now know make an existing document wrong?*, not by the size of the diff.

## The checklist

Execute in order; each step is a todo. Do the grep-audits in Steps 3.5, 4 and 5 inline when they are a handful of greps. Fan out to read-only Explore subagents (grep/read only, no tests or builds) only when an audit spans many files, and keep the judgment and the edits here, where the session context lives.

### 1. Scan what changed
`git log main..HEAD --oneline` (on a branch) or `git log --oneline --since='12 hours ago'` (on main). Identify merged PRs, migrations, new or deleted files, architectural shifts, and open loops the user flagged.

### 1.5. Session number
Sessions are numbered per project (`s215`), and `sN` rides alongside ISO dates wherever cadence matters; it never replaces them (dates are ground truth; on conflict the date wins). **This skill owns the counter.** This session's N = the `Session:` line of the newest handoff doc, +1. No numbered handoff yet? Seed by estimate (count handoff docs and wrap-up-style doc commits) and label it an estimate; approximate-but-large beats resetting to s1. Correct forward only; never renumber history. Stamp `sN` in: the MEMORY.md one-liner (Step 2), the tracker `session:` header and `last-touched` stamps (Step 3.6), the handoff index row (Step 7), the handoff `Session:` line (Step 7), and the kickoff prompt's `Starting s<N+1>` (Step 7.5).

### 2. Update auto-memory
Add this session's one-liner to `MEMORY.md`'s session log, and keep only the most recent ~5 lines there, because the handoff index holds the full sequence and MEMORY.md is loaded every session under a 200-line cap. Update topic files that describe systems touched this session.

### 3. Update second brain
Per the Memory Sync Rule: every auto-memory write gets its counterpart (`update_project` / `add_decision` / `add_research` / `remember`, with `summary` params).

### 3.5. Fix drift surfaced during the session
Claims in CLAUDE.md, specs or docs that the session's work revealed as false: fix in place if small, citing the primary source you verified against (file:line, schema constraint). Larger drift goes to a "Drift queue" entry in MEMORY.md plus a follow-up thread. Verify schema-level claims against the schema file itself, never against prior audits, because audits are syntheses and misattribute.

### 3.6. Reconcile the thread tracker
**REQUIRED SUB-SKILL: `project-threads` (Reconcile mode).** It owns the tracker walk: statuses, `next` pointers, collapse-on-ship, uncaptured threads, `card:` validation, execution-order legibility. The step is done only when no thread body still describes pre-session state that its header contradicts, because the bodies are what the next session works from.

### 3.7. Anti-bloat audit
Run the audit table in `references/budgets.md` across **all** surfaces, not only the ones this session touched, because bloat accretes from prior sessions too. A surface over budget collapses to a pointer at its home (see the table in the Overview). Phases that shipped this session get their detail compressed to ≤150 words now.

### 4. Update CLAUDE.md
CLAUDE.md is the session-zero orientation file: rules plus one Current state slot. Each wrap-up leaves it the same length or shorter unless a genuinely new rule landed.

**Rewrite the Current state slot.** It is one section, headed exactly `## Current state`, holding exactly these parts in this order, ≤150 words in total:
1. `Session: s<N> (YYYY-MM-DD)`: the session that last wrote the slot.
2. **Where the work is**: one or two sentences on the state relative to the next action, not a recap of what shipped.
3. **Next action**: one concrete step.
4. **Read first**: a link to this session's handoff and a pointer to the thread board.
5. **Binding warnings**: at most three one-line warnings the next session needs that do not yet live in a rule, a memory, or a thread. Each links to where the full reasoning lives.

Replace the whole slot. Do not keep the previous session's slot as a "collapsed" line; it already lives in its handoff and the index row. A warning that has carried over two wrap-ups is not transient: graduate it to a Hard Rule (if it is a rule), a memory (if it is a lesson), or a thread (if it is work), then remove it from the slot.

**Migration.** If CLAUDE.md has accreted status blocks outside the slot (per-session paragraphs, "collapsed at sN" lines, era narratives), move each one out: its sessions become handoff-index rows, any rule inside it goes to Hard Rules or memory, and CLAUDE.md keeps only the slot.

**Also:**
- **Add** new rules (one line, pointing to the doc with full context), operational gotchas, new docs for the index, layer-model changes.
- **Remove** old API signatures, renamed directories and deleted paths found in this session's diff, and prose now duplicated in a doc.
- **Check** that a fresh reader orients in under 60 seconds and that the Hard Rules are on the first screen.

### 5. Canonical docs: two passes

The path diff is necessary and not sufficient.

**Pass A — the path diff (mechanical).** If the project has a canonical-docs registry (`docs/canonical-docs.yml`, or the path its CLAUDE.md names), this half is deterministic:

1. Take the session's touched files (Step 1's diff).
2. Match them against each **current-state** and **convention** entry's `describes:` globs.
3. Every hit is a doc to re-verify against the code, or to flag stale in the handoff. The question is *does this doc still describe what the code now does?*, not "did I add a lock?"
4. Fix a current-state doc by **full edit**, not a banner, because a reader who hits the stale prose before the banner has already been misled.
5. Don't edit a **decision record** (specs, RFCs, ADRs, audits, handoffs) to match new reality. Supersede it with a new record, or add a dated correction banner to an audit, because editing one destroys the trail of what was decided when.

**Pass B — the learned-facts sweep (judgment).** Pass A catches code that outran a doc. It cannot catch a doc that was already wrong and that this session proved wrong, because nothing in the diff points at it. Ask:

> *What did I learn this session that makes an existing document untrue?*

Chase each such fact into every doc that asserts otherwise: architecture prose, specs you superseded, and **thread bodies**, not just thread headers.

A session with few or no code changes has the highest ratio of Pass B findings, not the lowest. Design, research, audit and review sessions give the path diff almost nothing and can invalidate documents wholesale. Real incident (s360, UncoverIQ): a design session touched zero `src/` files, correctly reported Pass A clean, and left three live falsehoods: a superseded draft spec with no banner, an architecture paragraph describing a fetch that no longer happens, and a thread body prescribing a superseded plan under a SUPERSEDED header.

**5b. Supersession banners go on the OLD document.** When this session replaced a spec, plan, design or RFC, add a `> ## ⚠ SUPERSEDED` banner at the top of the old doc naming its replacement, what was inherited intact, and what changed. The old doc is the one already linked from threads, handoffs and other specs, so a banner only in the new doc leaves the old one looking authoritative. The banner is a dated pointer, not an edit to the record. Then grep for inbound references and repoint them.

**No registry?** Propose creating one the first time this step bites. Meanwhile, grep the main architecture doc for stale module paths, component tables, queue or job lists, and framework descriptions touched by this session's diff.

Why Pass A matches on touched paths rather than asking "did this session add a lock or convention?": that question ran in a real project for months while its architecture doc came to describe a four-queue worker that had ten. The change that rots a doc usually adds no lock and no convention; it makes a described path untrue.

### 6. Roadmap
**REQUIRED SUB-SKILL: `auto-roadmap`.** Delegate fully; it owns every roadmap file edit, including the thread projection that keeps cards in lockstep. Run it every session that did real work, internal infrastructure included, because "internal, skip the roadmap" drifted a real partner page for ~90 sessions.

If the project's CLAUDE.md or sidecar `$config` says a live page reads the roadmap from a specific branch, the synced files land on that branch every session, via the project's landing script if it has one. Pushing the default branch may need the user's OK; the files reaching it is not optional.

### 6.5. Graphify refresh (only if `graphify-out/` exists)
Run `graphify update <path>` (free, structural). Semantic re-extraction (`graphify extract --backend …`) is metered LLM spend, so run it only when the user explicitly authorizes it in this session. Keep graph artifacts (`graph.json`, `graph.html`, `cache/`) out of the doc commit.

### 7. Handoff doc and index row

**Filename: `<handoff dir>/YYYY-MM-DD-sNNN-<topic>-handoff.md`**: the date, then the session number zero-padded to three digits (`s007`, `s042`, `s216`), then the topic. The default handoff dir is `docs/superpowers/plans/`, unless the project names another. The prefix makes name order and chronological order agree, which `/kickoff` depends on. Sorting by name alone broke when two same-date handoffs sorted in the wrong order, and sorting by mtime breaks on any edit or checkout.

**One handoff per session.** If this session supersedes an earlier handoff (especially a same-date one), add a `> ## ⚠ SUPERSEDED` banner to the old doc naming its replacement, then repoint inbound references.

**Contents.** First line after the title: `Session: s<N>` (the counter's source of truth). Sections: TL;DR; architecture sketches for non-obvious flows; public API surface; schema changes; test state; **shipped vs explicitly NOT done**; next plans by dependency; open issues; limitations carried forward; deploy sequence; commit trail. The first ~750 words stand alone; overflow is appendix (budgets.md rule 5).

**Index row.** Update `<handoff dir>/INDEX.md`: a table with one row per arc (an epic, a phase, a run of sessions with one goal), with columns `Sessions | Arc | Outcome | Read first`. If this session continues the current arc, extend that row's session range and, if this handoff is now the best entry point, its `Read first` link. If it starts a new arc, add a row. Keep the outcome to one line. Create the file on first use, seeding rows from the handoffs that exist.

### 7.5. Kickoff prompt
Generate per `references/kickoff-prompt.md`. Write it as the handoff's final `## Next session kickoff` section (canonical; `/kickoff` reads it) and also show the full prompt in chat, with a note that `/kickoff` will pick it up.

### 8–9. Commit and push docs
Commit docs separately from code: `docs: align CLAUDE.md + ROADMAP.md + architecture doc with <change>` (or `docs: <topic> handoff + roadmap update`). Push and confirm.

### 9.5. Background residue sweep
Nothing started this session outlives it.
1. **Session tasks and monitors:** enumerate this session's background tasks and `TaskStop` every persistent Monitor or watch loop still armed, including ones inherited across a `/clear` (background tasks survive it and keep firing into the next session). Completed one-shot watches need nothing.
2. **Orphaned processes:** `ps -eo pid,etime,args | grep -E "vitest|tsx scripts|<project gate/build patterns>" | grep -v grep` is empty, or every survivor is accounted for and killed per the long-running-processes rules (check `/proc/<pid>/cwd` first; never another project's). Write grep patterns that can't match themselves (`run-ship-gate[s]`).
3. **Subagents:** all released. A subagent still mid-task means the session isn't done: finish it or hand it off in the handoff doc.

### 10. Report
The user reads this report fresh, so write it as a re-grounding, not a continuation of the working thread. Lead with the outcome, spell out project terms, and keep complete sentences. Cover: commits pushed; files touched per doc; memory writes (both stores); open loops captured; leftover housekeeping; graphify status if run; then "safe to end session" or the specific concerns.

## Completion criteria

- [ ] Both memory stores synced (listed what went to each); MEMORY.md session log trimmed to the recent lines
- [ ] Surfaced drift fixed or queued, with primary-source citations
- [ ] Thread tracker reconciled via `project-threads` (headers AND bodies)
- [ ] Bloat audit run across all surfaces; shipped phases collapsed
- [ ] CLAUDE.md: Current state slot rewritten whole (≤150 words, five parts); no session narrative outside it; stale paths and signatures grepped out
- [ ] Canonical-docs **Pass A** run: touched files matched against `describes:` globs; every hit re-verified or flagged stale
- [ ] Canonical-docs **Pass B** run, including on a low-code session: learned facts chased into every doc asserting otherwise, thread bodies included
- [ ] Any superseded spec, plan, design or handoff carries a `⚠ SUPERSEDED` banner on the old doc
- [ ] Roadmap synced via `auto-roadmap` and landed on the branch the live page reads (if the project declares one)
- [ ] Graphify structural refresh run (if adopted); no graph artifacts in the doc commit
- [ ] Handoff doc within budget with its `Session: sN` line; handoff index row updated; kickoff prompt written as `## Next session kickoff` and shown in chat
- [ ] Session number consistent across the handoff, index row, Current state slot, tracker header and MEMORY one-liner
- [ ] Background residue swept: monitors stopped (incl. `/clear` survivors), process sweep clean, subagents released
- [ ] Docs committed and pushed; report given with open loops called out

## References

- `references/budgets.md` — the per-surface budgets and the audit table (canonical; nothing restates it)
- `references/kickoff-prompt.md` — Step 7.5 template and calibration
- `references/anti-patterns.md` — rationalization table; consult when tempted to skip a step

## Related skills

- `project-threads` — owns the tracker (Step 3.6)
- `auto-roadmap` — owns roadmap files (Step 6)
- `kickoff` — reads the handoff and its `## Next session kickoff` section
- `superpowers:finishing-a-development-branch` — the code/PR side; this skill is the docs + memory side
- `claude-md-management:revise-claude-md` — deeper CLAUDE.md review when drift looks systemic
