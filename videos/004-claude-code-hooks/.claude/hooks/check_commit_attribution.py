#!/usr/bin/env python3
"""PreToolUse hook: block git commits containing AI attribution lines."""
import json
import os
import re
import shlex
import sys

# Matches lines like "Co-Authored-By: Claude ..." or "Generated with Claude Code"
ATTRIBUTION_PATTERNS = [
    re.compile(r"co-authored-by:.*claude", re.IGNORECASE),
    re.compile(r"generated with\s+\[?claude code", re.IGNORECASE),
    re.compile(r"generated with\s+claude", re.IGNORECASE),
]


def is_git_commit(command: str) -> bool:
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        tokens = command.split()
    for i, tok in enumerate(tokens):
        if tok == "git" and i + 1 < len(tokens) and tokens[i + 1] == "commit":
            return True
    return False


def extract_commit_messages(command: str, cwd: str) -> list[str]:
    """Best-effort extraction of -m/--message values, -F/--file files and heredoc bodies."""
    messages = []

    for match in re.finditer(r"(?:-m|--message)(?:=|\s+)(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|\S+)", command):
        raw = match.group(1)
        try:
            messages.append(shlex.split(raw)[0] if raw[0] not in "\"'" else shlex.split(raw, posix=True)[0])
        except (ValueError, IndexError):
            messages.append(raw)

    for match in re.finditer(r"(?:-F|--file)(?:=|\s+)(\S+)", command):
        path = os.path.join(cwd, match.group(1).strip("\"'"))
        try:
            with open(path, encoding="utf-8") as f:
                messages.append(f.read())
        except OSError:
            pass

    heredoc_match = re.search(r"<<[-~]?['\"]?(\w+)['\"]?\n(.*?)\n\1", command, re.DOTALL)
    if heredoc_match:
        messages.append(heredoc_match.group(2))

    return messages


def find_violation(messages: list[str]) -> str | None:
    for msg in messages:
        for pattern in ATTRIBUTION_PATTERNS:
            if pattern.search(msg):
                return msg
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name != "Bash":
        return 0

    command = payload.get("tool_input", {}).get("command", "")
    if not command or not is_git_commit(command):
        return 0

    messages = extract_commit_messages(command, payload.get("cwd", "."))
    violation = find_violation(messages)
    if violation:
        output = {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked: commit message contains an AI attribution line "
                "(e.g. 'Co-Authored-By: Claude ...' or 'Generated with Claude Code'). "
                "This repository's policy forbids AI attribution in commit messages. "
                "Remove that line and retry the commit."
            ),
        }}
        print(json.dumps(output))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
