# 005 · Claude Code Ignoring Your CLAUDE.md? I Tested 8 Files

Eight instruction files, one codeword in each. Ask Claude Code to list every codeword it was given, and you see which files are in its context.

| File | Codeword | Loaded at start (run 1)? |
|---|---|---|
| [`workspace/CLAUDE.md`](workspace/CLAUDE.md) (folder above the project) | GRAPE | yes |
| [`notes-app/CLAUDE.md`](workspace/notes-app/CLAUDE.md) | APPLE | yes |
| [`notes-app/CLAUDE.local.md`](workspace/notes-app/CLAUDE.local.md) | BANANA | yes |
| [`notes-app/.claude/CLAUDE.md`](workspace/notes-app/.claude/CLAUDE.md) | CHERRY | yes |
| [`.claude/rules/style.md`](workspace/notes-app/.claude/rules/style.md) (no `paths`) | KIWI | yes |
| [`.claude/rules/api.md`](workspace/notes-app/.claude/rules/api.md) (`paths: src/api/**`) | FIG | no, only after a file in `src/api` is read |
| [`src/api/CLAUDE.md`](workspace/notes-app/src/api/CLAUDE.md) | DATE | no, only after a file in `src/api` is read, or when you start in `src/api` |
| [`notes-app/AGENTS.md`](workspace/notes-app/AGENTS.md) | LEMON | no, until `@AGENTS.md` is added to CLAUDE.md |

## Run it

```bash
bash run-tests.sh
```

Or one command, from `workspace/notes-app`:

```bash
claude -p "List every codeword your instructions give you, one per line. Nothing else." --allowedTools Read
```

Run 5 (the AGENTS.md fix): replace `workspace/notes-app/CLAUDE.md` with [`fix/CLAUDE.md`](fix/CLAUDE.md), which adds one line, `@AGENTS.md`, and run the command again.

If you have a user-level `~/.claude/CLAUDE.md`, it may be in context too. It only changes the result if it also contains codewords.

## What I saw (November 9, 2026, Claude Code 2.1.270)

Full output: [`results/runs.txt`](results/runs.txt).

| Run | Setup | Codewords |
|---|---|---|
| 1 | project root | GRAPE APPLE CHERRY KIWI BANANA |
| 2 | read `src/api/notes.js` first | + DATE FIG |
| 3 | start inside `src/api` | + DATE (no FIG) |
| 4 | `--setting-sources project` | GRAPE APPLE CHERRY KIWI (no BANANA) |
| 5 | `@AGENTS.md` in CLAUDE.md | GRAPE APPLE LEMON CHERRY KIWI BANANA |

The session logs show one tool call across all five runs: the `Read` of `notes.js` in run 2. Claude never opened a CLAUDE.md file itself. All five runs: 22 seconds, $0.60.

Limits: this asks the model what it was told. It's a quick test, not a debugger, and I ran each setup once. Newer versions may behave differently.
