# The next-session kickoff prompt (Step 7.5)

Generate the kickoff prompt and deliver it to **two places, same content**:

1. **The handoff doc** — as its final section, headed exactly `## Next session kickoff`. This is the canonical copy: `/kickoff` in the next session reads the newest handoff and treats this section as its session-starting prompt.
2. **The wrap-up chat message** — the full prompt, prefaced with one line noting it's written into the handoff and `/kickoff` will pick it up automatically.

Why both: a new session starts with zero working memory. The previous session knows exactly which docs matter, which loops carry forward, and the next concrete action — the handoff section makes that survive `/clear` (chat doesn't), and the chat copy gives the user immediate visibility to sanity-check the reading list while context is fresh.

Don't worry that an embedded prompt "goes stale": `/kickoff` always reads the *newest* handoff, so the section is only ever consumed alongside the doc it was generated with — it can't be staler than the handoff itself.

## Template

```
Starting s<N+1> — <one-line scope statement>.

Before doing anything else, read in this order:

1. CLAUDE.md § "Current state" + § "Session-start ritual" (if the project has one)
2. The threads board (renders automatically) + project-threads.md active-thread bodies — <one-line current state>
3. <load-bearing spec or master design doc + specific section refs>
4. <playbook / convention doc + specific section>
5. <relevant memory files — name them explicitly>
6. <reference implementation or precedent doc>
7. <directory walk if implementation is needed>
8. docs/superpowers/plans/<this-handoff-doc-filename>

Then state your understanding of:
- <where the work sits — the state we're in for the next concrete action, not "what's done">
- <the next concrete action — specific enough that the user can validate it>
- <the load-bearing locks / conventions / directives that govern the work>
- <cross-cutting state that's easy to forget — worker-stopped doctrine, deferred directives, prod scope, etc.>

Wait for my confirmation before doing more.
```

`s<N+1>` is a **literal number**, computed at generation time: this session's number (SKILL.md step 1.5) plus one. Write `Starting s216`, not a placeholder — the next session inherits its number from this line and the handoff's `Session:` line without hunting.

In the handoff copy, item 8 refers to the handoff doc the section lives in — keep it in the list anyway (self-reference is fine; `/kickoff` reads the doc body before the section, so the item is already satisfied by the time it executes the list).

## Calibration

- READ FIRST list: 5–10 items. Fewer is too thin; more won't get read.
- The understanding-statement bullets are the confabulation check — the user must be able to spot a wrong reading immediately.
- Keep "Wait for my confirmation": the user is the gate for a session with no working memory, and the understanding statement is only useful if someone checks it.
- The `## Next session kickoff` section sits below the handoff's 750-word standalone budget line (budgets.md rule 5) — it is exempt from that budget, like the appendix.

## Anti-patterns

- Presenting the prompt in chat only. Chat dies at `/clear`; the handoff section is what `/kickoff` consumes. A wrap-up whose handoff lacks the section has not completed Step 7.5.
- Divergent copies — editing one after generating both. Generate once, place twice, verbatim.
- Using a different section heading. `/kickoff` keys on `## Next session kickoff` exactly.
- Listing every doc the session *might* want — pick the load-bearing ones.
- Asking the new session to "summarize what's been done" — that's a memory exercise, not state-loading; ask for specific load-bearing facts.
- Skipping it for "minor" sessions: if the work earned a handoff, it earns a kickoff section. If no handoff was warranted, a one-paragraph MEMORY.md Current Status note serves instead.
