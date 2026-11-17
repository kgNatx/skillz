#!/usr/bin/env bash
# Registers the threads-board SessionStart hook in ~/.claude/settings.json.
# Idempotent: re-running updates the path if the skill moved, no-ops otherwise.
# Override target with CLAUDE_SETTINGS=/path/to/settings.json for testing.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$SKILL_DIR/scripts/threads-board.py"
SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"

[ -f "$SCRIPT" ] || { echo "error: $SCRIPT not found" >&2; exit 1; }
command -v python3 >/dev/null || { echo "error: python3 required (the board script runs on it)" >&2; exit 1; }

python3 - "$SCRIPT" "$SETTINGS" <<'PYEOF'
import json, sys

script, settings_path = sys.argv[1], sys.argv[2]
cmd = f"python3 {script}"
try:
    with open(settings_path) as f:
        cfg = json.load(f)
except FileNotFoundError:
    cfg = {}

entries = cfg.setdefault("hooks", {}).setdefault("SessionStart", [])
for group in entries:
    for h in group.get("hooks", []):
        if "threads-board.py" in h.get("command", ""):
            if h["command"] == cmd:
                print("threads-board hook already installed; nothing to do")
                sys.exit(0)
            h["command"] = cmd
            with open(settings_path, "w") as f:
                json.dump(cfg, f, indent=2)
                f.write("\n")
            print(f"updated existing threads-board hook -> {cmd}")
            sys.exit(0)

entries.append({"hooks": [{
    "type": "command",
    "command": cmd,
    "timeout": 10,
    "statusMessage": "Rendering project threads board...",
}]})
with open(settings_path, "w") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")
print(f"installed SessionStart hook -> {cmd}")
PYEOF

echo "Done. New sessions render the board in any repo with a project-threads.md."
echo "If a running session doesn't pick it up, open /hooks once (or restart)."
