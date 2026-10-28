# 004 · Claude Code Hooks in 7 Minutes: Block a Bad Commit

A Claude Code `PreToolUse` hook that blocks any `git commit` whose message has an AI attribution line (`Co-Authored-By: ... Claude ...` or `Generated with Claude Code`). Claude Code wrote the first version from [one prompt](prompt.txt). I fixed three things by hand afterwards. Both versions are here.

| File | What it is |
|---|---|
| [`.claude/settings.json`](.claude/settings.json) | Registers the hook: `PreToolUse`, matcher `Bash` |
| [`.claude/hooks/check_commit_attribution.py`](.claude/hooks/check_commit_attribution.py) | The hook (96 lines, the fixed version) |
| [`original/`](original/) | What Claude Code wrote (86 lines), unchanged |
| [`tests/`](tests/) | Sample hook input: one commit that passes, one blocked, one `git commit -F` blocked |

## Use it

Copy `.claude/` into your project root, or merge the `hooks` block into your existing `.claude/settings.json`. The command uses `python`. Change it to `python3` if that's what your system has.

Test it without Claude:

```bash
python .claude/hooks/check_commit_attribution.py < tests/pass_commit.json      # no output = allowed
python .claude/hooks/check_commit_attribution.py < tests/blocked_commit.json   # prints a "deny" decision
python .claude/hooks/check_commit_attribution.py < tests/file_commit.json      # reads tests/msg.txt, denies
```

## What I changed from Claude's version

1. **`git commit -F file` went straight through.** The original only read `-m` and heredocs. The fix reads the message file too, relative to the `cwd` in the hook input.
2. **Output format.** The original printed `{"decision": "block", "reason": ...}`. That still blocked on Claude Code 2.1.270, but the [hooks docs](https://code.claude.com/docs/en/hooks) list `hookSpecificOutput.permissionDecision: "deny"` for `PreToolUse`, so the fixed version uses that.
3. **Path.** The settings file now runs the script through `$CLAUDE_PROJECT_DIR` instead of a relative path.

Diff: compare [`original/check_commit_attribution.py`](original/check_commit_attribution.py) with the fixed one.

## What I saw in the video (October 28, 2026, Claude Code 2.1.270)

- **Claude Code would not write into `.claude/` in headless mode** (`claude -p`). Allowing `Write` wasn't enough, and neither was `--permission-mode acceptEdits`. Claude Code flags `.claude/` as a sensitive path. Replying "approved" in the prompt didn't help either. I had Claude write the files to `hook-draft/`, read them, and copied them in myself.
- **A blocked command blocks every part of it.** Claude ran `git add greet.py && git commit ...` as one command. The hook denied it, so `git add` never ran either. Claude's retry was `git commit` alone, which failed with "no changes added to commit". The third try worked. The same thing happened in both runs.
- **If that one line is all you want gone, there's a setting for it:** `attribution.commit` (see the [settings reference](https://code.claude.com/docs/en/settings-reference.md)). With the hook off and `--settings '{"attribution":{"commit":""}}'`, the commit came out without the trailer. The hook is for rules no setting covers.

Not tested yet: telling Claude, in the deny reason, to run `git add` again before retrying.
