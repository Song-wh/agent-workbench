# Agent Workbench

Code from the **Agent Workbench** YouTube channel: real builds with Claude Code and AI agents, one working thing per video, including what broke.

Everything here was actually run on screen. If something only worked after a fix, the fix is written down.

| Video | Folder | What you can copy |
|---|---|---|
| 001 · Claude Code Skills in 6 Minutes (Build One From Scratch) | [videos/001-claude-code-skills](videos/001-claude-code-skills) | The 17-line `/standup` skill |
| 002 · Build a Real MCP Server With Claude Code | [videos/002-mcp-server](videos/002-mcp-server) | The upload-calendar MCP server (86 lines) and the checker it wraps |
| 003 · 8 Days of Real Numbers From a Channel Claude Code Made | [videos/003-7-days-channel](videos/003-7-days-channel) | The scripts that read the numbers: sign-in, stats, analytics, upload checks |
| 004 · Claude Code Hooks in 7 Minutes: Block a Bad Commit | [videos/004-claude-code-hooks](videos/004-claude-code-hooks) | A PreToolUse hook that blocks commits with AI attribution lines, plus the version Claude wrote first |
| 005 · Claude Code Ignoring Your CLAUDE.md? I Tested 8 Files | [videos/005-claude-md-loading](videos/005-claude-md-loading) | Eight instruction files with one codeword each, the commands to see which ones Claude Code loads, and the @AGENTS.md fix |

## YouTube skill pack

[skills/youtube](skills/youtube) is the YouTube skill pack this channel runs on (the original eleven skills plus `yt-voicecheck`), forked from
[Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill) (MIT).
Changes from the original are listed in [skills/youtube/CHANGES.md](skills/youtube/CHANGES.md).

## License

MIT for the code in this repo ([LICENSE](LICENSE)). The skill pack keeps its original MIT license and copyright notice ([skills/youtube/LICENSE](skills/youtube/LICENSE)).
