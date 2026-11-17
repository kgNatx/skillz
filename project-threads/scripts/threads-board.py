#!/usr/bin/env python3
"""SessionStart hook: render an ASCII board from project-threads.md thread headers.

Silent no-op (exit 0, no output) when the project has no tracker.
Header contract is defined in ~/.claude/skills/project-threads/SKILL.md.
"""
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime

IDLE_DAYS = 21
# Triage-due threshold (SKILL.md Triage operation): a parked+backlog pile
# bigger than this is presumed to need a triage pass even if dates are clean.
TRIAGE_PILE_CAP = 15
LANES = ["active", "blocked", "next", "backlog", "parked"]
LIVE_LANES = ("active", "blocked", "next")
LANE_LABEL = {"active": "ACTIVE", "blocked": "BLOCKED", "next": "NEXT",
              "backlog": "BACKLOG", "parked": "PARKED"}
# Injected into model context every session start — keep the board bounded.
LANE_CAP = {"active": 10, "blocked": 10, "next": 5, "backlog": 3, "parked": 3}
MISSING_CAP = 5
# Contract (SKILL.md): heading titles are stable names — lifecycle annotations
# ("✅", "(NEW s294)", "SHIPPED s294") belong in the status/last-touched fields.
# Bare uppercase words are NOT flagged (titles like "make the PARKED lane
# wider" are legitimate) — only annotation shapes: marker emoji, session refs,
# or a lifecycle word adjacent to annotation punctuation.
_LIFECYCLE = r"(?:NEW|SHIPPED|CLOSED|FIXED|MERGED|EXECUTED|COMPLETE|DONE|RESOLVED|GRADUATED|RULED|ABORTED)"
TITLE_DECORATION = re.compile(
    r"✅|✔|🚀|\bs\d{2,4}\b"
    rf"|[(—–;·]\s*{_LIFECYCLE}\b"
    rf"|\b{_LIFECYCLE}\s*[);]"
)
# card:/epic: are join keys — a bare id, nothing else (`none` is card-only).
ID_VALUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*$")
# Session counter mirror (SKILL.md file-header contract): a bare `session: s215`
# line above any ## section — the last WRAPPED session, bumped by wrap-up.
SESSION_LINE = re.compile(r"^session:\s*s?(\d+)\s*$")
# ## Epics registry (SKILL.md): epics are born in the threads file; entries are
# `- <e-id> — <one-line working description> — status: live | closed`.
EPICS_HEADING = re.compile(r"^#{2,3}\s+Epics\s*$")
EPIC_ENTRY = re.compile(
    r"^-\s+(e-[A-Za-z0-9-]+)\s+[—–-]+\s+(.+?)\s+[—–-]+\s+status:\s*(live|closed)\s*$"
)
# Header contract (SKILL.md): `next` is one line, ≤ this many chars; detail
# belongs in the thread body. The board flags drift so it self-corrects.
NEXT_CONTRACT_MAX = 160
# Display clipping for the user-facing board — keeps lines from hard-wrapping
# in the terminal, which destroys the column layout.
TITLE_MAX = 70
NEXT_MAX = 90
FLAG_MAX = 70

MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
WIKI_LINK = re.compile(r"\[\[([^\]]+)\]\]")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
CODE = re.compile(r"`([^`]+)`")


def clip(text, cap):
    """Markdown doesn't render in the hook's systemMessage surface — strip it,
    then truncate at a word boundary so long fields can't wall-of-text the board."""
    for pat in (MD_LINK, WIKI_LINK, BOLD, CODE):
        text = pat.sub(r"\1", text)
    if len(text) <= cap:
        return text
    return text[:cap].rsplit(" ", 1)[0].rstrip(" ,;:·—-(") + " …"


def find_tracker():
    candidates = [os.path.join(os.getcwd(), "project-threads.md")]
    try:
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        if root:
            candidates.append(os.path.join(root, "project-threads.md"))
    except Exception:
        pass
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def parse(path):
    threads = []
    epics = {}
    session = None
    current = None
    in_epics = False
    seen_section = False
    for line in open(path, encoding="utf-8", errors="replace"):
        if not seen_section:
            if re.match(r"^#{2,}\s", line):
                seen_section = True
            else:
                m = SESSION_LINE.match(line.strip())
                if m:
                    session = int(m.group(1))
                    continue
        if EPICS_HEADING.match(line):
            in_epics = True
            current = None
            continue
        if line.startswith("#"):
            in_epics = False
        if in_epics:
            m = EPIC_ENTRY.match(line.strip())
            if m:
                epics[m.group(1)] = {"desc": m.group(2), "status": m.group(3)}
            continue
        m = re.match(r"^#{2,3}\s+(t-[A-Za-z0-9][A-Za-z0-9.-]*)\s+[—–-]+\s+(.+?)\s*$", line)
        if m:
            current = {"id": m.group(1), "title": m.group(2)}
            threads.append(current)
            continue
        if current is not None:
            f = re.match(r"^-\s+([a-z-]+):\s*(.*?)\s*(?:<!--.*-->)?\s*$", line)
            if f:
                current[f.group(1)] = f.group(2)
            elif line.strip() and not line.startswith("-"):
                current = None  # header block ended; prose or next section
    return threads, epics, session


def idle_days(thread):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", thread.get("last-touched", ""))
    if not m:
        return None
    try:
        return (date.today() - datetime.strptime(m.group(1), "%Y-%m-%d").date()).days
    except ValueError:
        return None


def render(by_status, epics, condensed, session=None):
    header = "── project threads "
    if session is not None:
        header += f"· last wrap s{session} "
    lines = [header + "─" * max(4, 60 - len(header))]
    for lane in LANES:
        lane_threads = by_status.get(lane, [])
        cap = LANE_CAP[lane]
        for t in lane_threads[:cap]:
            flags = []
            if t.get("epic"):
                flags.append(f"[{t['epic']}]")
            d = idle_days(t)
            if d is not None and d >= IDLE_DAYS and lane in LIVE_LANES:
                flags.append(f"⚠ idle {d}d")
            blocked_on = t.get("blocked-on") if lane == "blocked" else None
            if blocked_on and not condensed:
                flags.append(f"blocked-on: {blocked_on}")
            flag_str = ("   " + " · ".join(flags)) if flags else ""
            title = clip(t["title"], TITLE_MAX) if condensed else t["title"]
            lines.append(f" {LANE_LABEL[lane]:<8} {t['id']:<22} {title}{flag_str}")
            if blocked_on and condensed:
                lines.append(f"          ↳ blocked-on: {clip(blocked_on, NEXT_MAX)}")
            if lane in ("active", "next") and t.get("next"):
                nxt = clip(t["next"], NEXT_MAX) if condensed else t["next"]
                lines.append(f"          ↳ next: {nxt}")
        overflow = len(lane_threads) - cap
        if overflow > 0:
            lines.append(f" {LANE_LABEL[lane]:<8} … +{overflow} more {lane} (see project-threads.md)")
    unknown = by_status.get("unknown", [])
    if unknown:
        ids = ", ".join(t["id"] for t in unknown[:MISSING_CAP])
        suffix = f", +{len(unknown) - MISSING_CAP} more" if len(unknown) > MISSING_CAP else ""
        lines.append(f" ⚠ {len(unknown)} thread(s) missing status ({ids}{suffix}) — run project-threads migration")

    drifted = [
        t["id"] for lane in LANES for t in by_status.get(lane, [])
        if len(t.get("next", "")) > NEXT_CONTRACT_MAX
    ]
    if drifted:
        ids = ", ".join(drifted[:3])
        suffix = f", +{len(drifted) - 3} more" if len(drifted) > 3 else ""
        lines.append(f" ⚠ {len(drifted)} thread(s) with next: over {NEXT_CONTRACT_MAX} chars ({ids}{suffix})")
        lines.append("   — next: is one line; move the detail into the thread body")

    # done threads are excluded from the drift nags — they're archive-bound;
    # cleaning them happens at archive time, not via a per-session warning.
    live_and_parked = [t for lane in LANES for t in by_status.get(lane, [])]
    decorated = [t["id"] for t in live_and_parked if TITLE_DECORATION.search(t["title"])]
    if decorated:
        ids = ", ".join(decorated[:3])
        suffix = f", +{len(decorated) - 3} more" if len(decorated) > 3 else ""
        lines.append(f" ⚠ {len(decorated)} decorated title(s) ({ids}{suffix})")
        lines.append("   — titles are stable names; lifecycle lives in status:/last-touched:")
    malformed = [
        f"{t['id']}({field})" for t in live_and_parked for field in ("card", "epic")
        if field in t and (not ID_VALUE.match(t[field])
                           or (field == "epic" and t[field] == "none"))
    ]
    if malformed:
        ids = ", ".join(malformed[:3])
        suffix = f", +{len(malformed) - 3} more" if len(malformed) > 3 else ""
        lines.append(f" ⚠ {len(malformed)} malformed card:/epic: value(s) ({ids}{suffix}) — bare id only")

    if epics:
        ghosts = [f"{t['id']}({t['epic']})" for t in live_and_parked
                  if t.get("epic") and t["epic"] not in epics]
        if ghosts:
            ids = ", ".join(ghosts[:3])
            suffix = f", +{len(ghosts) - 3} more" if len(ghosts) > 3 else ""
            lines.append(f" ⚠ {len(ghosts)} epic id(s) not in ## Epics registry ({ids}{suffix})")
            lines.append("   — epics are born in the registry; add the entry or fix the id")

    parked_backlog = by_status.get("parked", []) + by_status.get("backlog", [])
    undated = [t for t in parked_backlog if idle_days(t) is None]
    on_closed = [t for t in parked_backlog
                 if epics.get(t.get("epic"), {}).get("status") == "closed"]
    parked_on_live = [t for t in by_status.get("parked", [])
                      if epics.get(t.get("epic"), {}).get("status") == "live"]
    if (len(parked_backlog) > TRIAGE_PILE_CAP or undated
            or on_closed or parked_on_live):
        parts = [f"{len(parked_backlog)} parked/backlog"]
        if undated:
            parts.append(f"{len(undated)} missing dates")
        if on_closed:
            parts.append(f"{len(on_closed)} on closed epics")
        if parked_on_live:
            parts.append(f"{len(parked_on_live)} parked on live epics")
        lines.append(" ⚠ triage due: " + ", ".join(parts)
                     + " — run project-threads triage")

    live_counts = {}
    for lane in LIVE_LANES:
        for t in by_status.get(lane, []):
            if t.get("epic"):
                live_counts.setdefault(t["epic"], 0)
                live_counts[t["epic"]] += 1
    if live_counts:
        def epic_label(name):
            reg = epics.get(name)
            if not reg:
                return name
            desc = clip(reg["desc"], 40) if condensed else reg["desc"]
            return f"{name}: {desc}"
        rollup = " · ".join(f"{epic_label(name)} ({n} live)" for name, n in
                            sorted(live_counts.items(), key=lambda kv: -kv[1]))
        lines.append(f" epics: {rollup}")

    counts = " · ".join(
        f"{len(by_status.get(s, []))} {s}" for s in LANES + ["done"] if by_status.get(s)
    )
    lines.append(f" {counts}")
    lines.append("─" * 60)
    return "\n".join(lines)


def main():
    path = find_tracker()
    if not path:
        return
    threads, epics, session = parse(path)
    if not threads:
        return

    by_status = {}
    for t in threads:
        by_status.setdefault(t.get("status", "unknown"), []).append(t)

    if sys.stdout.isatty() or os.environ.get("THREADS_BOARD_PLAIN"):
        # Run by hand (or by a skill's dynamic injection): plain text, condensed —
        # anything printed to a terminal is for human eyes.
        print(render(by_status, epics, condensed=True, session=session))
    else:
        # Run as a SessionStart hook: systemMessage shows the board to the USER
        # in the terminal — condensed so long fields can't wrap into a wall of
        # text; additionalContext injects the full-fidelity board for the model.
        # Plain stdout alone reaches only the model — silent hook success is
        # never displayed, which hides the board from the human it was built for.
        print(json.dumps({
            "systemMessage": "\n" + render(by_status, epics, condensed=True, session=session),
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": render(by_status, epics, condensed=False, session=session),
            },
        }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)  # never break session start over a board render
