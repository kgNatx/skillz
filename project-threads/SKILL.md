---
name: project-threads
description: Use when a work stream is spawned, parked, blocked, resumed, or shipped mid-session in a project that has (or should have) a project-threads.md tracker; when the wrap-up skill reaches its working-set step; when the user asks where the threads stand; or when the board flags triage due / the user asks to triage or clean up parked threads.
user-invocable: true
---

# project-threads

Current board (rendered fresh at invocation; empty ⇒ no tracker in this project or shell execution disabled): !`THREADS_BOARD_PLAIN=1 python3 ${CLAUDE_SKILL_DIR}/scripts/threads-board.py 2>/dev/null`

## Overview

`project-threads.md` (repo root) is the canonical registry of in-flight work streams. Each thread carries a structured header that three consumers parse: the SessionStart board script (renders the orientation picture), the `auto-roadmap` skill (projects thread state onto partner-facing roadmap cards via the `card:` join), and future sessions (orient without re-deriving the dependency graph).

**Capture at the moment of change, not at wrap-up.** The whole value of the tracker depends on threads being logged when they spawn/park/block — reconstruction at session end is where fidelity dies. Logging a thread takes under a minute; do it the moment the state changes, then return to the main work.

## Thread header format (the contract)

Every thread is a `##` or `###` section whose heading starts with `t-` (match the tracker's existing heading depth):

```markdown
## t-lantern-ingest — Earnings-call ingestion pipeline
- status: active
- card: f-earnings-intel
- epic: e-lantern                 <!-- optional: initiative this thread belongs to -->
- next: wire transcript fetcher into the queue worker
- last-touched: 2026-07-12 (s214) — fetcher scaffolded, queue worker untouched
- blocked-on: <reason>            <!-- only when status: blocked -->

Free-form prose below the header: decisions, blockers, links, detail.
Active threads may carry as much prose as they need.
```

**The heading is `<slug> — <title>`: the slug is frozen; the title is a stable name, not a status line.** No decorations — no "✅", no "(NEW s294)", no "SHIPPED s294 / CLOSED / FIXED" annotations. Lifecycle lives in `status:` and `last-touched:`; the board renders it from there. Decorated titles duplicate the status field, drift when it changes, and eat the board's title clip. The board flags decorated titles; fix by moving the annotation into the fields. The descriptive title after the dash MAY be freely improved when it's vague (Triage does this) — only the slug and the no-decorations rule are frozen. Threads belonging to an epic SHOULD take the epic's stem in the slug (`t-lantern-ingest` under `e-lantern`): the name is a mnemonic, the `epic:` field is the truth — parsers never read meaning from the stem, and on the rare reparent the slug keeps its old stem. When referencing a thread to the user in prose, give slug plus title ("`t-lantern-ingest` — earnings-call ingestion"), never the bare slug.

Field rules:

- `status`: one of `active` | `next` | `blocked` | `backlog` | `parked` | `done`.
  - `backlog`: identified, never started, waiting its turn. This is where ideas and known-future work live — NOT `parked`.
  - `parked`: was started (or explicitly ruled on) and deliberately set aside, with a one-line why. Parked implies a decision; backlog implies a queue.
- `card`: a feature id from the project's `roadmap-data.yml` (e.g. `f-earnings-intel`), or `none` for internal chores no partner-facing card covers. **Never invent an id — check the sidecar.** If the work deserves a card that doesn't exist yet, set `card: none` and say so; auto-roadmap proposes new cards, not this skill. **Projects with no roadmap sidecar omit the `card:` line entirely** — this skill works standalone; the field only exists to feed auto-roadmap's projection where a roadmap exists.
- `epic`: optional; an `e-` prefixed initiative id (e.g. `e-lantern`) grouping related threads — and, via auto-roadmap, related roadmap cards — into one arc. This is the hierarchy layer: threads are fine-grained, cards are coarse, epics tie a decomposed initiative together so "how much of X shipped?" stays answerable. The value must match an entry in this file's `## Epics` registry (below) — same never-invent rule as `card:`, but the fix is different because epics are born HERE: need a new one, add its registry entry (id, one-liner, `status: live`) in the same edit that first references it. The sidecar's `epics:` block, where one exists, is the partner-facing projection of this registry, reconciled by auto-roadmap — never invent epic ids sidecar-side. Epics are *finite initiatives* that eventually close (flip the registry entry to `status: closed`; never delete it), not permanent product areas (those are the sidecar's `streams`).
- `next`: one concrete action, specific enough that a fresh session could start on it. "Continue work" is a failure. **One line, ≤160 chars** — handoff detail, review notes, and scope rulings live in the body prose, not the header. The board flags any thread whose `next` exceeds the bound; fix flagged threads by moving the detail down into the body, never by deleting it.
- `last-touched`: ISO date required; session number `(sN)` alongside it per the project session-numbering convention (below); one-line outcome after the dash. Date-only is acceptable only in projects not numbering yet — the date always stays; `sN` never replaces it.
- `blocked-on`: present only while `status: blocked`.

Sections not starting with `## t-` (e.g. `## Session log`) are ignored by parsers — free space.

**File header — session counter mirror.** Near the top of the file, above any `##` section, a bare line `session: s215` mirrors the per-project session counter: it holds the **last wrapped** session's number, bumped by `wrap-up` at reconcile (the counter's source of truth is the newest handoff doc's `Session:` line; `wrap-up` owns increments and seeding — this file just carries the working copy the board renders). Mid-session captures stamp `last-touched` with the **current** session = that number + 1. Absent line ⇒ the project isn't numbering yet; the board doesn't flag it — suggest seeding at the next wrap-up, don't block.

## Epics registry

Epics are defined in THIS file, in a `## Epics` section (conventionally above the threads). One line per epic:

```markdown
## Epics
- e-lantern — earnings intelligence: ingest → scoring → digest — status: live
- e-onboard-v2 — partner onboarding rework — status: closed
```

Entry contract: `- <e-id> — <one-line working description> — status: live | closed`. The section heading text must be literally `Epics` (`##` or `###` depth) — the parsers match it exactly; a decorated heading silently yields an empty registry. The registry is where epics are born and defined for working purposes; the roadmap sidecar's `epics:` block (where one exists) is the partner-facing projection — display naming, page presentation — reconciled by auto-roadmap in the same direction it projects threads onto cards. Same split as threads vs cards: the sidecar says what the partner sees; this file says what we're doing; they join by `e-` id. Standalone projects (no sidecar) get a first-class registry for free.

### Id prefixes (the key)

| Prefix | Means | Defined in |
|---|---|---|
| `t-` | thread | this file (`## t-` headings) |
| `f-` | feature card | `roadmap-data.yml` (`features:`) |
| `e-` | epic | this file (`## Epics` registry) |

Hierarchy is never encoded in id strings — no `t-<epic>.<child>` syntax, no card ids embedded in thread slugs. Relationships live in fields (`card:`, `epic:`); ids are flat names. If thread nesting is ever genuinely needed, the mechanism is a `parent:` field, not id syntax.

## Operations

**Capture (mid-session, the common case).** When a work stream spawns, parks, blocks, resumes, or finishes: add or update its header + 1–3 lines of prose. Announce it in one line ("Logged t-foo as blocked on X") and return to the main task. Do not turn capture into ceremony. **Parking has a gate** — at the moment of parking, all four, no deferral: (1) the one-line why, (2) a fresh `last-touched`, (3) an explicit `card:` ruling (a real id or `none`) and an explicit `epic:` ruling (a real id or deliberate omission — `none` is card-only; the board flags `epic: none` as malformed), never absent-by-neglect, (4) body compressed to the ≤150-word parked budget. A park that skips the gate is the intake valve of the dumping ground Triage exists to clean up.

**Reconcile (from wrap-up, or on request).** Walk every non-`done` thread top to bottom:

1. Update `status`, `next`, and `last-touched` to post-session truth, stamping `last-touched` with this session's `(sN)` (wrap-up computes N; see the file-header contract above). When running from wrap-up, bump the file's `session:` header to this session's number in the same pass — or seed it (with the estimate wrap-up produced) if the project wasn't numbering yet. A `next` that describes a completed action is the classic stale state — every reconcile must leave `next` pointing at genuinely-undone work.
2. Catch threads the session spawned but never captured — scan session memory for work streams with no header.
3. **Collapse-on-ship:** when a thread finishes, flip it to `done` and compress its prose to ≤150 words (what shipped + link to the handoff doc). The handoff is canonical for detail; the thread body just points. This is the highest-leverage move per reconcile — do it actively, never by accretion.

3b. ⛔ **HARD GATE — the body must not contradict its own header.** A header saying `SUPERSEDED` / `done` / `blocked` above a body that still prescribes the old plan is **worse than no update at all**: a future session reads the body as current guidance, and the header's contradiction reads as staleness in the *header*. When a thread's direction changes, **edit the body in the same pass** — strike or mark the superseded prose explicitly (`⛔ the list above is SUPERSEDED (sN) — do not action it`) and state what replaced it. This is the single most-reported-done-while-undone step in reconcile: updating headers is quick and visible, rewriting bodies is neither. **The step is not complete while any body still describes pre-session state its header denies.**
4. **Execution-order legibility:** if a thread tracks a decomposed phase (sub-PRs / sub-tasks whose id numbers are not execution order), its prose must pair every sub-unit reference with its execution position and a plain-language label ("step 2 of 8 — sub-PR 3.3: trackedLLMCall + run()"), and link the canonical ordered-status table in the plan doc. A bare "NEXT = 3.X" is a hard fail: a reader must answer "where are we / what's next / in what order" without re-deriving the graph.
5. Verify every `card:` value still exists in `roadmap-data.yml`, and every `epic:` value in this file's `## Epics` registry; flag orphans.
6. **Archive sweep:** move `done` threads, and `parked` threads untouched for 30+ days, to `project-threads-archive.md` (repo root; same format, newest at top; add an `- archived: <date>` field line). Move verbatim — archiving is relocation, never editing or deleting. The board only reads `project-threads.md`, so the working file stays scrollable while history stays greppable. Never archive `active` / `next` / `blocked` / `backlog` threads. Don't wait for reconcile if the working file is unwieldy — the user can ask for an archive sweep anytime.
7. **Parked-pile health report (one line, no action):** state parked+backlog count, missing `last-touched` count, and epic-alignment orphans; when the board's triage-due thresholds are crossed, suggest a Triage pass. Reconcile never performs triage itself.

**Triage (on demand — "triage the parked threads" — or when the board says triage due).** Never runs automatically at wrap-up. Walk every `parked` and `backlog` thread and force exactly one ruling per thread:

- **revive** → `status: next` (or `active`) with a fresh, concrete `next:`
- **requeue** → `status: backlog` (never actually started, or the park decision no longer holds but the idea remains)
- **re-affirm** → stays `parked`; refresh `last-touched` to today and confirm or rewrite the one-line why
- **archive** → move to `project-threads-archive.md` (relocation, verbatim, add `- archived:`)
- **attach** (composes with any ruling) → set/repair `epic:`/`card:` where a matching initiative or card now exists

**Epic-alignment test** — run per thread before proposing its ruling: on a **live** epic → propose revive, or merge into that epic's active threads; on a **closed** epic → likely dead, default proposal is archive; no epic but plainly belongs to a live one → propose attach.

**Metadata repair** rides along on every pass: fill missing `last-touched` (from git history where recoverable, else today with a note), compress over-budget parked/backlog bodies to ≤150 words, reclassify never-started "parked" threads as `backlog`, improve vague titles.

**Interaction model: propose-and-confirm in batches.** Pre-sort every triaged thread into recommended-ruling buckets and present each bucket for approval/adjustment — never interrogate thread-by-thread.

**Bootstrap.** No `project-threads.md` in a project doing multi-session work? Offer to create one from current session state + recent git history. Get approval on the initial thread set before writing.

**Orient.** The SessionStart hook renders the board automatically, and invoking this skill re-renders it fresh (top of this file). If the user asks to see or refresh the board at any other moment, run the script directly — never reconstruct the board by hand from the headers, and don't dump the file:

```bash
THREADS_BOARD_PLAIN=1 python3 ~/.claude/skills/project-threads/scripts/threads-board.py   # from the repo root
```

(Without `THREADS_BOARD_PLAIN=1` in a non-interactive shell, the script emits its SessionStart-hook JSON envelope instead of plain text.)

## Budgets

| Surface | Budget |
|---|---|
| `done` / `parked` thread body | ≤150 words: outcome + handoff link |
| `backlog` thread body | ≤150 words: the idea + why it matters |
| `active` / `next` / `blocked` thread body | No cap — this is the live working set |
| Capture operation | 1 header + 1–3 prose lines; under a minute |
| Working file | When `done`+`parked` bulk dominates, run the archive sweep |

## Hard boundaries

- **Never delete a thread.** Finished → `done`; abandoned → `parked` with a one-line why. History is the recovery surface. Archiving (relocation to `project-threads-archive.md`) is the only compaction mechanism — content is never edited on the way out.
- **Never invent `card:` or `epic:` ids.** Cards: verify against the sidecar or use `none`. Epics: verify against this file's `## Epics` registry — or register the new epic in the same edit.
- Do not restate roadmap card content in thread prose — the card says what the partner sees; the thread says what we're doing. They join by id, not by copied text.
- Do not maintain a separate at-a-glance table in the file. The headers are the single source; the board script renders the view.

## Integration

- `wrap-up` invokes Reconcile as its working-set step.
- `auto-roadmap` reads headers for its projection step (active → `in-progress` card, next → `next-up` card, no live thread → staleness question, `epic:` → epic tag consistency on cards).
- `scripts/threads-board.py` (in this skill directory) renders the SessionStart board: parses the `session:` file header (rendered in the board's top rule as "last wrap sN"), parses the `## Epics` registry, groups live threads by epic in a rollup line using registry one-liners, validates `epic:` values against the registry, flags threads idle 21+ days, flags `next:` fields over the length bound, flags decorated titles, flags malformed `card:`/`epic:` values, and renders a triage-due line when parked debt crosses thresholds (parked+backlog > 15, missing `last-touched` dates, threads on closed epics, parked threads on live epics). The user-facing board (systemMessage / plain stdout) is condensed — markdown stripped, fields clipped so lines never wrap; the model receives the full-fidelity board via `additionalContext`. Tests: `scripts/test_threads_board.py` (plain unittest; run it after any board change).

## Distribution / install

This skill directory is self-contained — copying it to another machine's `~/.claude/skills/project-threads/` brings everything:

- `scripts/threads-board.py` — the board renderer (stdlib-only Python 3; parses the header contract above).
- `scripts/install-hook.sh` — registers the SessionStart hook in `~/.claude/settings.json`. Idempotent: safe to re-run; updates the path if the skill directory moved; touches nothing else in settings.

Setup on a new machine is one command:

```bash
~/.claude/skills/project-threads/scripts/install-hook.sh
```

If the board format or header contract changes, `scripts/threads-board.py` in THIS directory is the only copy — there is no second install location to sync.
