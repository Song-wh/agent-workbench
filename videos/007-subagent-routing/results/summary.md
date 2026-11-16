# 007 runs (2026-11-16, Claude Code 2.1.270, claude-sonnet-5)

Command: `claude -p "<prompt>" --permission-mode default --allowedTools "Bash(git *)" "Bash(npm test)" Read Grep Glob Agent Task --setting-sources project --output-format stream-json --verbose`, fresh copy of `repo/` (2 commits; HEAD "Add percent discount" changes the subtotal loop to `i < items.length - 1`).
Prompt "Review my last commit." unless noted. route = first Skill/Agent call in the main thread; "self" = no delegation. bug = final answer names the `length - 1` line.
Note: my runs were in a folder under my home directory, so my own `~/.claude/CLAUDE.md` (an unrelated note) was loaded as a parent-folder file in every run. Same in all setups. Run from a folder outside your home to avoid this.

## docs description (Anthropic docs style)

| run | route | main tool calls | delegated tool calls | turns | cost | bug found |
|---|---|---|---|---|---|---|
| d1 | skill:code-review | 2 | 9 | 3 | $0.30 | yes |
| d2 | skill:code-review | 2 | 12 | 3 | $0.34 | yes |
| d3 | skill:code-review | 2 | 10 | 3 | $0.29 | yes |
| d4 | skill:code-review | 2 | 12 | 3 | $0.31 | yes |
| d5 | skill:code-review | 2 | 11 | 3 | $0.28 | yes |

## short description "Reviews code."

| run | route | main tool calls | delegated tool calls | turns | cost | bug found |
|---|---|---|---|---|---|---|
| s1 | skill:code-review | 3 | 17 | 3 | $0.45 | yes |
| s2 | skill:code-review | 1 | 13 | 2 | $0.29 | yes |
| s3 | skill:code-review | 4 | 10 | 5 | $0.32 | yes |
| s4 | skill:code-review | 5 | 6 | 6 | $0.30 | yes |
| s5 | self | 8 | 0 | 9 | $0.18 | yes |

## trigger description (names "review my last commit")

| run | route | main tool calls | delegated tool calls | turns | cost | bug found |
|---|---|---|---|---|---|---|
| t1 | skill:code-review | 1 | 9 | 2 | $0.24 | yes |
| t2 | agent:code-reviewer | 2 | 5 | 2 | $0.18 | yes |
| t3 | agent:code-reviewer | 2 | 5 | 2 | $0.19 | yes |
| t4 | agent:code-reviewer | 1 | 5 | 1 | $0.15 | yes |
| t5 | skill:code-review | 2 | 12 | 3 | $0.27 | yes |

## prompt names the subagent

| run | route | main tool calls | delegated tool calls | turns | cost | bug found |
|---|---|---|---|---|---|---|
| e1 | agent:code-reviewer | 2 | 8 | 3 | $0.19 | yes |
| e2 | agent:code-reviewer | 2 | 5 | 1 | $0.19 | yes |
| e3 | agent:code-reviewer | 1 | 5 | 1 | $0.15 | yes |

## @agent-code-reviewer mention

| run | route | main tool calls | delegated tool calls | turns | cost | bug found |
|---|---|---|---|---|---|---|
| m1 | agent:code-reviewer | 2 | 5 | 3 | $0.15 | yes |
| m2 | agent:code-reviewer | 3 | 5 | 4 | $0.17 | yes |
| m3 | agent:code-reviewer | 2 | 5 | 1 | $0.18 | yes |

## docs description + CLAUDE.md routing line

| run | route | main tool calls | delegated tool calls | turns | cost | bug found |
|---|---|---|---|---|---|---|
| f1 | agent:code-reviewer | 1 | 5 | 1 | $0.16 | yes |
| f2 | agent:code-reviewer | 2 | 5 | 1 | $0.17 | yes |
| f3 | agent:code-reviewer | 2 | 7 | 1 | $0.18 | yes |
| f4 | agent:code-reviewer | 3 | 5 | 2 | $0.19 | yes |
| f5 | agent:code-reviewer | 3 | 6 | 4 | $0.18 | yes |

## Totals

- Description only (15 runs): own subagent 3 (all trigger), built-in `code-review` skill 11, no delegation 1.
- s1: the `code-review` skill itself launched `code-reviewer` twice as helper reviewers (nested).
- Naming it: prompt 3/3, @-mention 3/3, CLAUDE.md line 5/5.
- Cost by route: skill 11 runs avg $0.31 (0.24–0.45), avg 11 delegated tool calls; own subagent 14 runs avg $0.17 (0.15–0.19), avg 5.4; self 1 run $0.18.
- Bug found in 26/26. Total 26 runs $6.00 (+ pilot $0.52, not counted).
- `code-review` is a bundled skill in 2.1.270 (init event `skills`, `plugins: []`).
