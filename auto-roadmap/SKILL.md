---
name: auto-roadmap
description: Use when wrapping up a session in a project that has ROADMAP.md and roadmap-data.yml, when the wrap-up skill reaches its roadmap step, or when roadmap cards need reconciling with actual project state (stale in-progress cards, shipped work not reflected, partner-facing roadmap page out of date).
user-invocable: true
---

# auto-roadmap

Anchor pre-computed at invocation (empty/NONE ⇒ bootstrap mode): !`git log -1 --format=%H -- roadmap-data.yml 2>/dev/null || echo NONE`

## Overview

Keeps a project's `ROADMAP.md` (narrative prose) and `roadmap-data.yml` (structured sidecar) in sync. Runs at session wrap-up or on demand. Infers most changes from session memory + git history and presents them as concrete proposals ("I'm going to flip this to shipped, OK?") rather than interrogating field by field.

**The sidecar is usually LIVE.** In most projects `roadmap-data.yml` drives a partner/stakeholder-facing roadmap page that ships on every `git push` — so its accuracy is public, and staleness is visible to exactly the people the roadmap is meant to impress. Run this **every session that did real work**, with detailed edits. **Internal / infra / pre-launch / dormant work still counts as progress and must be surfaced** — the point is to show what's *moving*; hidden movement reads as a stalled project. "It was just internal plumbing, nothing to surface" is the rationalization that drifts roadmaps for dozens of sessions; the Step 2.5 health audit exists to catch what that excuse buried.

The sidecar is self-describing: a `$config` block at its top declares paths, status vocabulary, and how prose section headings map to status buckets. Projects with non-default conventions edit `$config` and this skill adapts on next run — no code change needed.

## When to use

**Use when:**
- Called from the `wrap-up` skill's roadmap step (the common case).
- User invokes `/auto-roadmap` standalone to sync without a full wrap-up.

**Do NOT use when:**
- The user just saved `ROADMAP.md` mid-session. Mid-session edits are reasoning, not commitments. Never run this skill automatically on save.
- The project has no `ROADMAP.md`. This skill doesn't create roadmaps from nothing — it syncs against an existing narrative.

## Files managed

In the target project, this skill reads and writes:

- `ROADMAP.md` — narrative prose. Path configurable via sidecar `$config.narrative`.
- `roadmap-data.yml` — structured sidecar at the repo root by default.

Both paths default to the repo root. The skill reads `$config` from the sidecar to learn the actual paths on each run.

## The `$config` contract

The sidecar begins with a `$config` block that describes project conventions:

```yaml
$config:
  narrative: ROADMAP.md
  threads: project-threads.md   # working-set tracker; omit if project has none
  now: false                    # true only after the roadmap page's schema accepts a per-feature now: field
  epics: false                  # true only after the page renders epic tags; epic data may ship earlier if the page's schema strips unknown keys
  validate: ""                  # project validator command (e.g. "npx tsx scripts/validate-roadmap.ts"); empty ⇒ this skill's bundled validator
  status_vocab: [in-progress, next-up, shipped, later, parked]
  sub_state_vocab: [todo, doing, done]
  narrative_sections:
    "Shipped": shipped
    "In progress": in-progress
    "Near-term": next-up
    "Planned": later
    "Parked": parked
    "Out of scope": parked
  id_prefix: f-
```

**Epics (the hierarchy layer).** An optional top-level `epics:` block names finite multi-card initiatives; features join one via an `epic:` field. Epic ids carry the `e-` prefix:

```yaml
epics:
  - { id: e-lantern, title: Lantern }   # optional desc: one-liner
features:
  - id: f-earnings-intel
    epic: e-lantern
    ...
```

**Epics are born in the project's `project-threads.md` `## Epics` registry** (contract owned by the `project-threads` skill); this sidecar block is the partner-facing **projection** — display naming, page presentation — reconciled from the registry in Step 2.7. Never invent an epic sidecar-first. Epics group cards (and, via the tracker's matching `epic:` header field, threads) into one legible arc — the answer to "how much of X shipped?" after a Decompose splits an initiative across many cards. Epics are *finite* and eventually close; the permanent product-area grouping is `streams`. Epic progress is **derived** by consumers (mean of member cards: shipped = 100, else `progress`) — never stored. When proposing a Decompose (Step 3) on an initiative that will span 2+ cards, also propose an epic to hold the pieces — registered in the tracker's registry first, then projected here.

Read `$config` on every run and use its values, not hardcoded defaults. If `$config` is missing from an existing sidecar, offer to add it using the defaults above (user approves before any other reconciliation begins).

**Canonical starter:** `templates/roadmap-data.yml` in this skill directory holds the default `$config` plus a commented example stream/feature. Bootstrap starts from it; projects adopting the convention copy it. If defaults change, that template is the single copy to edit.

## Flow

Execute these steps in order, tracking each one as a task.

### Step 1 — Detect scope and trigger mode

The anchor is pre-computed at the top of this skill via dynamic injection — use it directly. Fall back to running the command only if the injected value is missing (e.g. shell execution disabled) or the sidecar lives at a non-default path per `$config`:

```bash
git log -1 --format=%H -- roadmap-data.yml 2>/dev/null
```

- If the command returns a SHA → that is `$ANCHOR`. Proceed to normal reconciliation flow (Step 2).
- If the command returns nothing (sidecar never committed, or file absent) → **enter bootstrap mode** (Step 6). Do not run the rest of the normal flow.

### Step 2 — Gather signals since `$ANCHOR`

Run these three commands:

```bash
git log $ANCHOR..HEAD --oneline
git log $ANCHOR..HEAD -- ROADMAP.md
git diff $ANCHOR..HEAD -- ROADMAP.md
```

You now have three inputs to cross-reference:

1. **Session memory** — this conversation's changes. Strongest signal; you lived through the session.
2. **Narrative diff** — features added / removed / moved between prose sections; subs mentioned as done in the diff.
3. **Commit messages since `$ANCHOR`** — catches prior sessions where wrap-up was skipped.

Read the current `roadmap-data.yml` in full. Hold the `$config` values in mind for the rest of the flow.

### Step 2.5 — Audit the EXISTING in-flight set for health (staleness + accretion)

**This step exists because the signal-driven flow above has a blind spot: a card that no session touched produces no signal, so it rots in `in-progress` forever, and a long-running initiative accretes onto one ever-growing card that never visibly ships anything.** Both are silent failures the reactive flow cannot catch. So, INDEPENDENT of the since-anchor signals, walk EVERY card whose status is `in-progress` or `next-up` and assess the health checks below. Each finding becomes a proposal in Step 3.

**When `$config.threads` names a tracker that exists, skip check 1** — thread liveness owns staleness detection there (Step 2.7 rule 3 catches every card with no live thread), and running both produces duplicate questions. Checks 2 and 3 are about the shape of the published card itself, which threads can't see — they run every time.

1. **Staleness (no-activity rot) — tracker-less projects only.** Does this card's topic appear *anywhere* in recent activity — the last ~K sessions of commit subjects (`git log --oneline -50`), the recent handoff docs, or this session's memory? If a card has been `in-progress`/`next-up` with **zero topical activity across K+ sessions** (K ≈ 10, or "many sessions" by judgment), it is presumed stale. It almost certainly either (a) quietly SHIPPED and was never flipped, or (b) was ABANDONED/superseded. **Propose a flip — ship / park / delete — as a real question** (the skill can't know which; ask, citing "no activity since ~sN"). Derive N from the per-project session-numbering convention (counter owned by `wrap-up`): the tracker's `session:` file header, thread `last-touched` `(sN)` stamps, or handoff `Session:` lines — keep the `~`, since skipped wrap-ups make N approximate by design. A project with no counter yet loses this citation precision; suggest the next wrap-up seed it, without blocking. Do NOT leave it rotting as `in-progress`.

2. **Stuck progress.** Has `progress` not moved across many sessions, especially if pinned high (90–99%)? A card stuck at 99% for 20 sessions is a lie — it either shipped (→ `shipped`, `progress: 100`) or it's genuinely not 99%. Flag it; propose the honest status.

3. **Accretion / stale-content (the mega-card smell).** Is the `desc` over budget (see the desc budget in Step 3) OR does it contain **multiple "Phase X SHIPPED / done" claims**, OR does its newest content trail the current session by many sessions? That card is a multi-phase blob masquerading as one feature. **Propose DECOMPOSITION** (Step 3's Decompose class): promote each shipped phase to its own customer-readable `shipped` card, shrink the parent to only the genuinely-remaining work, and refresh the parent's content to the CURRENT state. The roadmap should show N discrete shipped capabilities (momentum), not one perpetual 99% card.

If all in-flight cards pass all three checks, note "in-flight set healthy" and proceed. This step is mandatory every run — it is the proactive counterpart to the reactive Step 2.

### Step 2.7 — Project the thread tracker onto the cards (the lockstep step)

**This step exists because Steps 2–2.5 are backward-looking: they reconcile what already happened, so "what we're doing now and what's next" only changes when a delta happens to imply it.** If `$config.threads` names a tracker file that exists (default `project-threads.md`), read every thread header (`id` / `status` / `card` / `epic` / `next` / `last-touched` — format owned by the `project-threads` skill) and derive proposals by these projection rules:

1. A thread with `status: active` → its `card` must be `in-progress`. If it isn't, propose the flip.
2. A thread with `status: next` → its `card` must be `next-up` (unless another active thread already holds it at `in-progress`).
3. A card sitting at `in-progress` or `next-up` with **no live thread** (`active`/`next`/`blocked`) pointing at it — and no Step 2 signal touching it — is a confirmed staleness case: feed it to the Step 2.5 flip question with the citation "no thread points here."
4. Threads with `status: done` or `parked` project nothing — their cards are governed by the reactive flow (a `done` thread's card typically flipped to `shipped` when it shipped). `card: none` is the explicit no-card sentinel, never an orphan.
5. A thread whose `card` id doesn't exist in the sidecar → flag the orphan; ask whether it maps to an existing card, deserves a new card, or should be `card: none`.
6. **Epic reconciliation (registry → sidecar).** The tracker's `## Epics` registry is the working source of epic definitions; the sidecar `epics:` block is its partner-facing projection. Registry epic referenced by any card-joined thread but missing from the sidecar block → propose adding it (draft a partner-facing title; the registry one-liner is working language, not display copy). Registry epic flipped to `status: closed` → propose retiring its sidecar presentation per the page's convention. Sidecar epic missing from the registry → contradiction; ask (the registry is canonical — usually add it to the registry or drop it from the sidecar). A thread carrying `epic:` whose `card` lacks the matching `epic:` field → propose tagging the card (mechanical). A thread or card `epic:` id missing from the registry → flag it (typo, or an unregistered epic; fix registry-side). Conflicting epics between a thread and its card → contradiction; ask. Only write `epic:` fields to the sidecar when `$config.epics: true` OR the project's consuming page is known to strip unknown keys (note which applies in the proposal).
7. **`now:` refresh (only when `$config.now: true`):** every `in-progress` card gets a one-line `now:` in customer-capability terms, derived from its active threads' current work ("currently: wiring earnings-call ingestion"). A `now:` describing completed work is a hard fail — refresh every run. Never write `now:` when `$config.now` is false or absent: the live page's schema validates the sidecar, and an unknown field can break the deploy.

Projection proposals are **mechanical** — thread state is ground truth the user already maintains. Present them as one grouped block with a single y/n (see Step 4), not per-item. Only genuinely ambiguous outcomes (orphaned card ids, thread-vs-session-memory contradictions, staleness ship/park/delete choices) join the per-item interview.

If the project has no tracker file, skip this step and note it — the roadmap then depends entirely on the reactive flow, which is exactly the configuration that historically drifted.

### Step 3 — Build the proposal set

Walk every delta you detect (from Step 2 signals), every health finding (from Step 2.5), AND every projection result (from Step 2.7). For each, classify it as one of exactly six proposal types:

| Class | Trigger | Proposed sidecar edit |
|---|---|---|
| **Status flip** | Feature moved between prose sections, or session shipped it, or Step-2.5 staleness/stuck-progress | Update `status`; if shipping, also `progress: 100` and clear `subs` |
| **New feature** | Bullet / session work with no sidecar entry | New `features[]` entry, broad-stroke (no `subs`); ask stream if ambiguous |
| **Stale** | Sidecar feature the prose no longer mentions, OR Step-2.5 no-activity rot (in-progress K+ sessions, zero topical activity) | Propose `shipped` / `parked` / deletion — **ask, citing "no activity since ~sN."** Never auto-delete; never leave rotting in `in-progress`. |
| **Sub flip** | Explicit session or commit mention of a phase completing | Flip that sub's state. **Never infer from prose tone alone.** |
| **Contradiction** | Sidecar, prose, and session memory disagree | Ask which is truth. **Never silently pick.** |
| **Decompose** | Step-2.5 accretion: a multi-phase card whose `desc` is over budget or carries multiple "Phase X SHIPPED" claims, or whose content trails the current session by many sessions | Propose splitting: **each shipped phase → its own customer-readable `shipped` `features[]` card**; the parent shrinks to only genuinely-remaining work and its `desc` is refreshed to the CURRENT state. **Propose an epic to hold the resulting card set** — registered in the tracker's `## Epics` registry first, then projected here — so the initiative stays legible as one arc. **This is a multi-line restructure — state that explicitly (per Step 5's restructure handling) and present the resulting card set for approval before applying.** |

**Granularity rule for NEW features:** default to broad stroke — one top-level `features[]` entry, no `subs[]`. Only propose `subs[]` when (a) the feature is actively in-flight with distinct phases observed in the session, or (b) the user explicitly asked to track phases. When a feature ships, clear its `subs[]`.

**Counter-rule for LONG-RUNNING multi-phase initiatives (the anti-mega-card rule):** the broad-stroke default is for *small new* features — it must NOT let a multi-session initiative accrete onto one perpetual card. When an initiative has **shipped ≥2 discrete phases**, do NOT keep piling them into one `in-progress` card's `desc`. Instead: each *shipped* phase becomes its **own `shipped` card** (so the roadmap shows momentum — N capabilities delivered, not one card stuck at 99%), and the still-in-progress remainder is a *separate, current* `in-progress` card. A partner reading the roadmap should see what SHIPPED, named as capabilities — not one blob that's been "almost done" for months.

**Customer-readable naming (this is a partner-facing roadmap).** Shipped cards are titled + described in **customer-capability terms** ("SEC filing analysis", "earnings-call intelligence", "prompt-cache cost reduction"), NOT internal mechanics ("Phase E PR 9", "G2a v2 7b", "sub-PR 3.3"). The internal phase/PR/session detail lives in handoffs + the working-set tracker; the roadmap card says what the *user* gets. When promoting a shipped phase to its own card during Decompose, translate the internal phase name into the capability it delivered.

**`desc` budget (accretion guard).** A feature's `desc` is ≤ ~80 words / ~6 lines. If a `desc` is growing phase-by-phase past this, that's the accretion smell Step 2.5 catches → it's a Decompose candidate, not a longer `desc`. The roadmap is a *shape*, not a changelog; per-phase detail belongs in handoffs.

If you detect zero deltas → skip to Step 7 with "Nothing to reconcile since `$ANCHOR`." Do not run the interview.

### Step 4 — Present proposals

Show the full proposal set at the top of your message, then walk them one at a time. Format:

```
Reconciling since <short-SHA> (<N commits across M sessions>).

1/<total>: <feature-id> — <one-line rationale>.
          Propose: <concrete edit>. [y/n/edit]
2/<total>: New feature in prose: "<title>". Which stream? [<stream-ids>, or "new"]
3/<total>: <feature-id> — sidecar says <A>, prose says <B>, session silent.
          Propose: leave as-is. [y/n]
```

- **Mechanical projections first, as one block.** Step 2.7's projection proposals (status flips from thread state, `now:` refreshes) are presented as a single grouped block with one y/n for the whole block — they're reads of state the user already maintains, not judgment calls. The per-item pass below is for everything else.
- Each numbered proposal is a single-line **statement** with y/n/edit, not an open question — unless it is genuinely ambiguous (new feature stream, subs granularity, rename ambiguity, contradiction). Real questions are the exception.
- "edit" means "yes with one change" (e.g. "yes shipped but progress 95 not 100"). Accept free-form one-liner edits and re-state the updated proposal for confirmation.
- If the proposal list has more than 5 items, chunk into groups of ~5 per presentation pass. User can y/n a whole chunk or drill into items individually.

### Step 5 — Show YAML diff and apply

Once every proposal has a resolution:

1. Compute the full set of edits to `roadmap-data.yml`.
2. Show them as a single unified diff in a code block.
3. Ask: "Apply these edits? [y/n]"
4. On approval, apply via the Edit tool using **targeted replacements** — single `status:` line, single `progress:` number, single `- { txt: ..., state: ... }` sub item. Never rewrite the whole file. This preserves comments and existing key order.
5. If any edit requires restructuring (inserting a new `features[]` entry, reordering a list), state that explicitly before applying: "this is a multi-line rewrite, not a targeted edit."
6. Also update `ROADMAP.md` in the same approval pass when proposals imply narrative changes: bump the "Last updated" date, move bullets between prose sections to match status flips, append new feature bullets under the right section. Keep narrative prose-voice — do not generate from the sidecar mechanically.
7. **Validate — mandatory after every apply.** The sidecar usually feeds a LIVE page; never end a run leaving it unverified. Run `$config.validate` if set (the project's own validator — e.g. the page's actual zod schema — is always the stronger check), else the bundled floor:

   ```bash
   python3 ~/.claude/skills/auto-roadmap/scripts/validate-sidecar.py roadmap-data.yml
   ```

   Non-zero exit → fix the errors and re-validate before reporting; warnings are surfaced in Step 7 but don't block.

Skip to Step 7.

### Step 6 — Bootstrap mode

Triggered when `roadmap-data.yml` has never been committed or does not exist.

1. Announce: "No sidecar found. I'll extract one from `ROADMAP.md`."
2. Read the full narrative.
3. Identify section headings. Map them to the default `narrative_sections` config (Shipped → shipped, In progress → in-progress, Near-term → next-up, Planned → later, Parked / Out of scope → parked). If the narrative uses different section names, ask once which bucket each maps to.
4. Extract a draft `features[]`. Default heuristic: one feature per capability-area heading (e.g. "§2.1 Account research pipeline"), with that section's bullets becoming the `desc` text. Do NOT expand every bullet into its own feature — broad-stroke by default.
5. Infer `streams[]` from section / subsection headings. Present the inferred list; ask user to confirm or edit.
6. Present the full draft sidecar as a diff against an empty file. Start from `templates/roadmap-data.yml` (this skill's directory): keep its `$config` block, replace the example stream/feature with the extracted set.
7. User reviews, edits, approves.
8. Write `roadmap-data.yml` via the Write tool.
9. Note: the user is responsible for committing the new file. Do not run `git add` or `git commit` automatically.

After bootstrap completes, the skill exits. The next invocation runs the normal flow.

### Step 7 — Report

Print a one-line summary:

```
roadmap-data.yml synced: <N> updated, <N> added, <N> parked. <N> unreconciled. Validation: PASS (<N> warnings).
```

If applicable, append:
- Deferred contradictions the user chose to leave untouched.
- Proposals the user rejected.
- Any `$config` additions made this run.

## Edge cases

| Case | Behavior |
|---|---|
| Empty session, no deltas detected | Print "Nothing to reconcile since `$ANCHOR`." and exit. No interview. |
| Renamed feature, id inferable from context | Propose title update only. |
| Renamed feature, id unclear | Ask user which sidecar entry this rename corresponds to. |
| Feature missing from prose, present in sidecar | Propose parked vs. delete. User picks. Never auto-delete. |
| Contradiction (sidecar ≠ prose ≠ session memory) | Ask which is truth. Flag in final report. |
| `$config` block absent from existing sidecar | Offer to add it using defaults. Get approval before any other reconciliation. |
| Prose section heading not in `narrative_sections` map | Ask: add mapping to `$config`, or treat as unmapped? |
| Large catch-up (20+ proposals) | Chunk into groups of ~5 per pass. |
| Sidecar file exists but is empty / malformed | Treat as bootstrap mode — re-extract from narrative, overwrite with approval. |

## Hard boundaries

**Never:**
- Run automatically on `ROADMAP.md` save. Mid-session edits are reasoning, not commitments.
- Auto-delete features. "Parked" and "delete" are always user-chosen.
- Silently resolve contradictions between sidecar, prose, and session memory.
- Generate narrative prose from the sidecar (reverse sync is out of scope).
- Hand-roll YAML parsing in-session. All reads / writes go through Read and Edit (targeted replacements); well-formedness is proven by the Step 5 validation gate (`$config.validate` or `scripts/validate-sidecar.py`), never asserted by eyeball.
- Finish a run with the sidecar failing validation.
- Touch multi-repo setups. One narrative + one sidecar per project.
- Touch historical / phased roadmap files (e.g. `<project-name>-roadmap.md`). Those are frozen.
- Run `git add` / `git commit` on behalf of the user.

## Integration with `wrap-up`

When this skill runs as step 6 of the `wrap-up` skill, wrap-up has already synced auto-memory and the second brain (steps 1–5). This skill owns every roadmap file update for the session. After it completes, wrap-up proceeds to handoff doc generation (step 7).

When this skill runs standalone via `/auto-roadmap`, none of wrap-up's other steps run. Session memory is still available because the skill reads the current conversation context.

## Related skills

- `project-threads` — owns the thread tracker this skill projects from in Step 2.7, including the `## Epics` registry where epics are born; threads join to cards via the `card:` header field, and to initiatives via the shared `e-` prefixed `epic:` id (registry → sidecar `epics:` block is a projection, reconciled in Step 2.7 rule 6).
- `wrap-up` — the common caller.
- `claude-md-management:revise-claude-md` — adjacent wrap-up sync skill; similar reflect → propose → approve → apply shape.
