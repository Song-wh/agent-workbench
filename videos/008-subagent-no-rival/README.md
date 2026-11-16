# 008 · I Said Simplify. Claude Code Amended My Commit 5 of 5 Times

Follow-up to [007](../007-subagent-routing/), where a `code-reviewer` subagent lost to the built-in `code-review` skill. This time: one subagent with **no rival** (`changelog-writer`) and one with a **rival** (`simplifier`, next to the built-in `simplify` skill). Same tiny invoice repo, two commits; the last one adds a percent discount in more lines than it needs. 25 headless runs, a fresh copy each time.

| Setup | Request | Result |
|---|---|---|
| [`agents/c-docs.md`](agents/c-docs.md) docs-style | "Add a changelog entry for my last commit." | subagent 3/5 · Claude itself 2/5 |
| [`agents/c-short.md`](agents/c-short.md) `Writes changelogs.` | same | subagent 2/5 · Claude itself 3/5 |
| [`agents/c-trig.md`](agents/c-trig.md) trigger | same | subagent **5/5** (one of them reported an edit it never made, see below) |
| [`agents/s-docs.md`](agents/s-docs.md) docs-style | "Simplify my last commit." | subagent 0/5 · `simplify` skill 0/5 · Claude itself 5/5, **`git commit --amend` 5/5** |
| [`agents/s-trig.md`](agents/s-trig.md) trigger | same | subagent **4/5**, no amends · Claude itself 1/5 (stopped to ask permission to run the tests) |

**The edit that never happened (run ct3):** the subagent's report said it added a `1.1.0` heading and printed the new file; the main session told me the entry was added. `CHANGELOG.md` was unchanged. The subagent called Bash and Read, never Edit. 1 run in 15.

**The amends (sd1–sd5):** every run said it amended. Four said it was safe because the commit was not pushed; one said that is what "simplify my last commit" asked for. My simplifier's instructions say nothing about git, and in the runs where it did the work nothing was committed.

Cost: changelog without the subagent averaged $0.10 a run, with it $0.13. All 25 runs $3.35. Claude Code 2.1.270, claude-sonnet-5, 2026-11-16.

## Three rules

1. Write the subagent description as a trigger, in the words you actually type.
2. After any request about your last commit, check `git log`.
3. Check the diff, not the report.

## Run it

Needs git, Node 18+ and Claude Code. Run from a folder outside your home directory (a parent-folder `CLAUDE.md` is still loaded with `--setting-sources project`).

```bash
bash run.sh c-docs.md "Add a changelog entry for my last commit."
bash run.sh c-trig.md "Add a changelog entry for my last commit."
bash run.sh s-docs.md "Simplify my last commit."
bash run.sh s-trig.md "Simplify my last commit."
```

The script prints any Skill/Agent call, whether the last commit hash changed, and `git status`.

## My results

[`results/summary.md`](results/summary.md) has route, subagent tool calls, changed files, amend and cost for every run. Each `results/<run>.log` lists the tool calls, the git log after the run, the subagent's report and the final message.

What I'd change: one tiny repo, one model, five runs per setup, two jobs. I did not test a CLAUDE.md routing line this time (it fixed routing in 007).
