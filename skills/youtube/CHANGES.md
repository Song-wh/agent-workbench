# Changes from the original

Forked from [Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill) at commit "The YouTube agent skill: eleven skills, six tools" (2026-09-16). Original license and copyright notice are kept in [LICENSE](LICENSE).

## 2026-10-15

- **Windows:** the six skills that run a script (`yt-chapters`, `yt-edit`, `yt-package`, `yt-retention`, `yt-script`, `yt-viral`) call `python3`, which does not exist on a standard Windows install. Each of those `SKILL.md` files now has a note above the command: use `python` on Windows. The commands themselves still say `python3`, so macOS and Linux work as before.
- Added `voice.template.md` (the original `templates/voice.md`) next to the skills.

## Install

Copy the skill folders into `~/.claude/skills/` (every project) or `<your project>/.claude/skills/` (one project). Then copy `voice.template.md` to `~/.claude/youtube/voice.md` and fill it in - most skills read it.
