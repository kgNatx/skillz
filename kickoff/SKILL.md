---
name: kickoff
description: Use when the user types /kickoff to start a fresh session after a wrap-up — re-orients from the latest handoff doc and threads board, states understanding, and waits for confirmation before any work.
user-invocable: true
disable-model-invocation: true
---

# kickoff

Newest handoff docs (most recent first): !`ls -1 docs/superpowers/plans/*handoff*.md docs/plans/*handoff*.md 2>/dev/null | sort -r | head -3`

Current threads board: !`THREADS_BOARD_PLAIN=1 python3 ~/.claude/skills/project-threads/scripts/threads-board.py 2>/dev/null`

## Purpose

A fresh session has zero working memory; this skill loads the load-bearing state deterministically and proves it loaded correctly before touching anything.

## Steps

1. **Announce your sources first** — name the handoff file you are about to read (the newest from the injected list above) in your first sentence, **and the session number**: the handoff's `Session: sN` line (or its kickoff section's `Starting s<N+1>`) makes this session `s<N+1>` — say so ("this is s216"). If the handoff carries no session number, note once that this project isn't numbering sessions yet and the next wrap-up can seed the counter (per-project convention, owned by `wrap-up`) — don't block on it. If no handoff was found, say so plainly and ask what to read — never guess or substitute other docs silently.
2. **Read that handoff in full, then branch on its final section:**
   - **If the handoff ends with a `## Next session kickoff` section, that section IS your session-starting prompt.** Execute it as written: read its numbered list in its order (items already covered by the handoff itself count as done), then state your understanding per *its* bullets. It encodes the previous session's judgment about what is load-bearing — it overrides the generic lists below.
   - **If the section is absent** (older handoff, or none warranted), fall back to the generic reads: (a) the `active` / `blocked` / `next` thread bodies in `project-threads.md` (the board above shows which); (b) the project CLAUDE.md's session-start ritual section, if one exists — follow any additional reads it mandates.
2.5. **Note which docs are trustworthy.** If the project has a canonical-docs registry (`docs/canonical-docs.yml`, or the path its CLAUDE.md names), skim it — not the docs, just the registry. It tells you which documents are **maintained current-state**, which are **conventions**, which are **decision records that describe a past moment and were never meant to track reality**, and which are **archived**. Reasoning about today's system from a decision record or an archived doc is a top source of confident wrong answers, and the registry is the cheapest possible guard against it. If no registry exists, treat undated architecture prose as suspect and verify against code before relying on it.

⚠️ **Two things the registry cannot tell you, both of which have cost real sessions:**
- **`current-state` means "someone committed to maintaining this," not "every sentence is true."** A doc can be registered, in-budget, recently touched, and still assert a code path that no longer runs. If you are about to build on a specific claim, verify *that claim* against code — the class tells you how much to trust the doc, not the sentence.
- **A superseded spec does not always announce itself.** The discipline is that the `⚠ SUPERSEDED` banner goes on the OLD doc, but it gets forgotten, and a stale design reads as authoritative right up until you have built from it. **If two specs cover the same subsystem, establish which is the record before reading either** — check dates, check for a successor naming it, and prefer the one the tracker or the newest handoff points at.

3. **State your understanding** — per the kickoff section's bullets when one exists; otherwise:
   - Where the work sits — the state we're in relative to the next concrete action, not a recap of what's done.
   - The next concrete action, specific enough that the user can validate it's right.
   - The load-bearing locks / conventions / directives that govern the work.
   - Any cross-cutting state that's easy to forget (deferred directives, prod scope, frozen test benches, etc.).
4. **Wait for the user's confirmation before doing anything else.** Non-negotiable — the user is the gate for a session with no working memory. Do not start work, propose plans, or open files beyond step 2's list until confirmed.

## Anti-patterns

- Summarizing what's been done instead of stating the current state — that's a memory exercise, not state-loading.
- Treating the `## Next session kickoff` section as informational instead of executing it — reading it and then doing the generic flow anyway discards the previous session's tailored judgment.
- Reading beyond step 2's list "for context" before confirmation. The handoff names what matters; trust it or flag a gap.
- Skipping the announcement in step 1. If the user can't see which handoff drove the orientation, a stale or wrong file goes undetected.

## Related skills

- `wrap-up` — writes the handoff this skill reads, including the `## Next session kickoff` section (its Step 7.5).
- `project-threads` — owns the board and thread bodies read in step 2.
