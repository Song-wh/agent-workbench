#!/usr/bin/env bash
# Runs the four checks from the video against ./workspace/notes-app.
# Needs: Claude Code (`claude`) on PATH. Each run is one headless session; expect a few cents each.
set -u
cd "$(dirname "$0")/workspace/notes-app"
Q='List every codeword your instructions give you, one per line. Nothing else.'

echo "== run 1: project root";              claude -p "$Q" --allowedTools Read
echo "== run 2: read a file in src/api first"
claude -p "Read src/api/notes.js. Then list every codeword your instructions give you, one per line. Nothing else." --allowedTools Read
echo "== run 3: start inside src/api";      (cd src/api && claude -p "$Q" --allowedTools Read)
echo "== run 4: --setting-sources project"; claude -p "$Q" --allowedTools Read --setting-sources project
echo
echo "Run 5: copy ../../fix/CLAUDE.md over workspace/notes-app/CLAUDE.md (it adds @AGENTS.md), then run 1 again."
