# Wrap-up anti-patterns (rationalization table)

Consult when tempted to skip or shortcut a step. Every row is a failure that actually happened.

| Pattern | Reality |
|---|---|
| Skipping memory sync because "auto-memory will pick it up" | Auto-memory only captures what's written. Silent drift happens. |
| Skipping doc-drift fixes because "this session didn't cause it" | If the session surfaced the drift, this session fixes it. Pre-existing drift compounds until something forces it visible — that something is now. |
| Trusting prior audit reports for schema facts | Audits are syntheses; they misattribute. Re-verify constraints/enums/indexes against the schema file directly. |
| Updating CLAUDE.md without the architecture doc (or vice versa) | They describe the same systems; divergence creates contradictions. |
| Writing the handoff next session instead of now | Context is fresh now. Later-you misses details. |
| Batching multiple sessions' wrap-ups | Each session's context dilutes. Per-session, always. |
| Assuming the user will remember open loops | They won't. Capture explicitly in docs + memory. |
| Deleting MEMORY.md content outright | Lessons and topic detail have recovery value when decisions get re-litigated; move them to topic files. The session log is different: past the recent lines, the handoff index holds the sequence. |
| Updating the threads at-a-glance state without reconciling active-thread bodies | The bodies are where future sessions get working context. (This one made a real session unable to answer "where are we.") Delegated to project-threads Reconcile — don't declare that step done on header updates alone. |
| Keeping the previous session's status as a "collapsed" line in CLAUDE.md | That is how CLAUDE.md grew a stack of per-session blocks. The slot is replaced whole; the old status already lives in its handoff and the index row. |
| Adding a status paragraph "for completeness" without removing the prior session's | 4× redundancy compounds linearly. The handoff is canonical; everything else points. |
| Letting a collapsed summary balloon because the phase "shipped a lot" | Collapse-on-ship is the highest-leverage move. ≤150 words, actively, the session it ships. |
| Restating design-spec locks in Status blocks / summaries / headers | Locks live in the spec. Four copies = four things that desync. Reference by number. |
| Skipping the bloat audit because "this session didn't add much" | The audit checks accreted bloat from prior sessions. Same word count to fix at s+10 as s+1, but you operated with it the whole time. |
| "Internal infra / not user-facing, so skip the roadmap" | This exact excuse silently drifted a real partner-facing roadmap for ~90 sessions (one card pinned at 99% while a dozen shipped capabilities stayed invisible). Internal progress IS progress; a wrap-up reporting "no roadmap changes" after a session that shipped code has missed something, so re-run auto-roadmap Steps 2.5 + 2.7. |
| Roadmap edits committed only to a feature branch | If the live page reads a different branch, the edits never go live (this froze a real partner page for ~90 sessions). Land sidecar + narrative on the branch the page reads, every session. |
| "No code changed, so the canonical-docs check is clean by construction" | Backwards: the path diff catches code that outran a doc; it cannot catch a doc this session *proved* wrong. A design/spec/audit session changes no code and can invalidate several documents at once. Real incident (s360): zero `src/` files touched, Pass A correctly clean, three live falsehoods left standing. Run Step 5 Pass B (*"what did I learn that makes an existing doc untrue?"*), hardest on exactly the low-diff sessions. |
| Declaring supersession only in the NEW doc | The old doc is the one already linked from threads, handoffs and other specs, and it still reads as authoritative to anyone who opens it. The `⚠ SUPERSEDED` banner goes **on the old doc** (Step 5b). A banner is a dated pointer, not an edit to the record. |
| Reconciling thread headers but leaving the bodies | A body still prescribing a superseded plan under a `SUPERSEDED` header is worse than no update — it reads as current guidance. Step 3.6's completion condition exists for this and has often been reported done on headers alone. |
