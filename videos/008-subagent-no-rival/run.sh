#!/bin/bash
# usage: bash run.sh <agent file in agents/ | none> "<prompt>"
#   bash run.sh c-docs.md "Add a changelog entry for my last commit."
#   bash run.sh s-docs.md "Simplify my last commit."
# Builds a fresh two-commit repo in a temp folder, runs Claude Code headless, then prints who did the work,
# whether the last commit was rewritten, and what changed. Run it from a folder outside your home directory:
# a CLAUDE.md in any parent folder (including ~/.claude/CLAUDE.md) is still loaded.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
AGENT=${1:-none}; PROMPT=${2:-"Simplify my last commit."}
T="$(mktemp -d)"; R="$T/invoice-app"; mkdir -p "$R/src" "$R/test"
cp "$HERE/invoice-app/package.json" "$HERE/invoice-app/README.md" "$HERE/invoice-app/CHANGELOG.md" "$R/"
cp "$HERE/invoice-app/before/src/invoice.js" "$R/src/"; cp "$HERE/invoice-app/before/invoice.test.js" "$R/test/"
cd "$R"; git init -q
git add -A; git -c user.name=demo -c user.email=demo@example.com commit -qm "Invoice totals with tests"
cp "$HERE/invoice-app/after/src/invoice.js" src/; cp "$HERE/invoice-app/test/invoice.test.js" test/
git add -A; git -c user.name=demo -c user.email=demo@example.com commit -qm "Add percent discount"
BEFORE=$(git rev-parse --short HEAD)
if [ "$AGENT" != none ]; then
  mkdir -p .claude/agents
  NAME=$(grep -m1 '^name:' "$HERE/agents/$AGENT" | cut -d' ' -f2)
  cp "$HERE/agents/$AGENT" ".claude/agents/$NAME.md"
fi
claude -p "$PROMPT" --permission-mode acceptEdits \
  --allowedTools "Bash(git *)" "Bash(npm test)" "Read" "Grep" "Glob" "Edit" "Write" "Agent" "Task" \
  --setting-sources project --output-format stream-json --verbose > "$T/stream.jsonl"
echo "log: $T/stream.jsonl"
grep -o '"name":"\(Skill\|Agent\|Task\)","input":{[^}]*' "$T/stream.jsonl" | head -3 || echo "no Skill/Agent call: Claude did it itself"
AFTER=$(git rev-parse --short HEAD)
[ "$BEFORE" = "$AFTER" ] && echo "last commit: unchanged ($BEFORE)" || echo "last commit: REWRITTEN ($BEFORE -> $AFTER)"
git status --short
