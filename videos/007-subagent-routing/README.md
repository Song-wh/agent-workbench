# 007 · Claude Code Subagent Not Running? I Tested 26 Reviews

A `code-reviewer` subagent in `.claude/agents/`, and one request: `claude -p "Review my last commit."`. Does Claude Code hand the review to the subagent?

The repo is a tiny invoice library. Its last commit adds a percent discount and also changes the subtotal loop to `i < items.length - 1`, so every invoice drops its last line. Both tests fail.

| Setup | Who did the review |
|---|---|
| [`agents/docs.md`](agents/docs.md): description written like the docs example | my subagent **0/5** · built-in `code-review` skill 5/5 |
| [`agents/short.md`](agents/short.md): `Reviews code.` | my subagent **0/5** · skill 4/5 · no delegation 1/5 (in one skill run, the skill launched my subagent twice as its helper) |
| [`agents/trigger.md`](agents/trigger.md): a trigger that names "review my last commit" | my subagent **3/5** · skill 2/5 |
| prompt names it: `Use the code-reviewer subagent to review my last commit.` | my subagent 3/3 |
| `@agent-code-reviewer review my last commit.` | my subagent 3/3 |
| `agents/docs.md` + [`fix/CLAUDE.md`](fix/CLAUDE.md) | my subagent **5/5** |

All 26 runs found the bug. Skill runs averaged $0.31 (11 runs); runs that used my subagent averaged $0.17 (14 runs). Total $6.00. Claude Code 2.1.270, claude-sonnet-5, 2026-11-16.

`code-review` ships with Claude Code: it was in the starting skill list of every run, and I never installed it.

## The line

```markdown
When I ask for a code review, use the code-reviewer subagent. Do not use the code-review skill.
```

Before you write a subagent, check whether a built-in skill already has the same job. If one does, name the route in `CLAUDE.md`.

## Run it

Needs git, Node 18+ and Claude Code. Each run builds a fresh two-commit repo in a temp folder.

```bash
bash run.sh docs
bash run.sh short
bash run.sh trigger
bash run.sh docs "Use the code-reviewer subagent to review my last commit."
bash run.sh docs "@agent-code-reviewer review my last commit."
bash run.sh docs "Review my last commit." fix
```

`--setting-sources project` keeps your own `~/.claude` settings out of the run. Run it from a folder outside your home directory: a `CLAUDE.md` in a parent folder (including `~/.claude/CLAUDE.md`) is still loaded.

## My results

[`results/summary.md`](results/summary.md) has route, tool calls, turns and cost for every run. Each `results/<run>.log` lists the run's tool calls (indented = inside a skill or subagent) and its final message.

What I'd change: one tiny repo, one model, five runs per setup. I only tested a reviewer; a subagent with no built-in rival may route fine on its description.
