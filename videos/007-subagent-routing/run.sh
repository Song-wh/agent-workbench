#!/bin/bash
# usage: bash run.sh <docs|short|trigger|none> ["prompt"] [fix]
#   bash run.sh docs                      # "Review my last commit." with the docs-style description
#   bash run.sh docs "Use the code-reviewer subagent to review my last commit."
#   bash run.sh docs "@agent-code-reviewer review my last commit."
#   bash run.sh docs "Review my last commit." fix   # adds fix/CLAUDE.md
# Each run builds a fresh two-commit repo in a temp folder and logs every event to <temp>/stream.jsonl.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
VARIANT=${1:-docs}; PROMPT=${2:-"Review my last commit."}
T="$(mktemp -d)"; R="$T/invoice-app"; mkdir -p "$R/src"
cp -r "$HERE/invoice-app/test" "$HERE/invoice-app/package.json" "$HERE/invoice-app/README.md" "$R/"
cp "$HERE/invoice-app/before/src/invoice.js" "$R/src/"
cd "$R"; git init -q
git add -A; git -c user.name=demo -c user.email=demo@example.com commit -qm "Invoice totals with tests"
cp "$HERE/invoice-app/after/src/invoice.js" src/
git add -A; git -c user.name=demo -c user.email=demo@example.com commit -qm "Add percent discount"
if [ "$VARIANT" != none ]; then mkdir -p .claude/agents; cp "$HERE/agents/$VARIANT.md" .claude/agents/code-reviewer.md; fi
[ "$3" = fix ] && cp "$HERE/fix/CLAUDE.md" CLAUDE.md
claude -p "$PROMPT" --permission-mode default \
  --allowedTools "Bash(git *)" "Bash(npm test)" "Read" "Grep" "Glob" "Agent" "Task" \
  --setting-sources project --output-format stream-json --verbose > "$T/stream.jsonl"
echo "log: $T/stream.jsonl"
# who did the review: first Skill/Agent call in the main thread
python3 - "$T/stream.jsonl" <<'PY' || python - "$T/stream.jsonl" <<'PY2'
import json, sys
for l in open(sys.argv[1], encoding="utf8"):
    e = json.loads(l)
    if e.get("type") == "assistant" and not e.get("parent_tool_use_id"):
        for c in e["message"]["content"]:
            if c["type"] == "tool_use" and c["name"] in ("Skill", "Agent", "Task"):
                print("route:", c["name"], c["input"].get("skill") or c["input"].get("subagent_type"))
    if e.get("type") == "result":
        print("cost: $%.2f" % e.get("total_cost_usd", 0))
PY
import json, sys
for l in open(sys.argv[1], encoding="utf8"):
    e = json.loads(l)
    if e.get("type") == "assistant" and not e.get("parent_tool_use_id"):
        for c in e["message"]["content"]:
            if c["type"] == "tool_use" and c["name"] in ("Skill", "Agent", "Task"):
                print("route:", c["name"], c["input"].get("skill") or c["input"].get("subagent_type"))
    if e.get("type") == "result":
        print("cost: $%.2f" % e.get("total_cost_usd", 0))
PY2
