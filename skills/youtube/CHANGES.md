# Changes from the original

Forked from [Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill) at commit "The YouTube agent skill: eleven skills, six tools" (2026-09-16). Original license and copyright notice are kept in [LICENSE](LICENSE).

## 2026-10-16

Found by running two channels with the pack for a week.

- **Per-channel voice profile.** `yt-audit`, `yt-comment`, `yt-package`, `yt-plan`, `yt-script` and `yt-seo` now use the nearest `voice.md` walking up from the folder you are working in, then `~/.claude/youtube/voice.md`. One project can hold two channels with two voices.
- **`hookscore.py` reads spelled-out numbers.** Scripts for a TTS voice spell numbers out ("eighty-six", "twenty twelve", "one hundred and three"); they now score the same as digits. A lone "one" stays a word. Checked against 71 hooks scored with the old version: only the 7 that spelled numbers changed. `test_hookscore.py` covers it.
- **`yt-viral/collect.py`.** Builds `swipe.py`'s input from public channel listings with yt-dlp (long-form tab, newest first), or saves search results to find channels in a niche. Prints the channel each handle resolved to.
- **`yt-seo/desclint.py`.** Lints a description: 5,000 characters, `<` or `>` (Studio refuses them - watch for `->` in code), chapter rules (00:00 first, at least 3, each at least 10 s), more than 60 hashtags, required phrases such as an AI-voice disclosure, and non-clickable links in Shorts.
- **New skill: `yt-voicecheck`.** Transcribes a TTS narration sentence by sentence with faster-whisper and lists only the lines that came out differently. Numbers, British/American spelling and spelled-out acronyms are normalised; names in `--ignore` match whatever was heard. On an 8-minute narration it flagged 5 of 106 sentences.

## 2026-10-15

- **Windows:** the six skills that run a script (`yt-chapters`, `yt-edit`, `yt-package`, `yt-retention`, `yt-script`, `yt-viral`) call `python3`, which does not exist on a standard Windows install. Each of those `SKILL.md` files now has a note above the command: use `python` on Windows. The commands themselves still say `python3`, so macOS and Linux work as before.
- Added `voice.template.md` (the original `templates/voice.md`) next to the skills.

## Install

Python tools need: `pip install yt-dlp` (yt-viral/collect.py), `pip install faster-whisper soundfile` (yt-voicecheck). Copy the skill folders into `~/.claude/skills/` (every project) or `<your project>/.claude/skills/` (one project). Then copy `voice.template.md` to `~/.claude/youtube/voice.md` and fill it in - most skills read it.
