#!/usr/bin/env bash
# Copy every skill named in SKILLS from ~/.claude/skills into this repo, then commit and push.
set -euo pipefail
cd "$(dirname "$0")"
while read -r s; do
  [ -n "$s" ] || continue
  rm -rf "./$s"
  rsync -a --exclude '__pycache__' --exclude '*.pyc' "$HOME/.claude/skills/$s/" "./$s/"
done < SKILLS
git add -A
git diff --cached --quiet && { echo "skillz: nothing changed"; exit 0; }
git commit -qm "sync: $(git diff --cached --name-only | cut -d/ -f1 | sort -u | tr '\n' ' ')"
git push -q origin main && echo "skillz: pushed"
