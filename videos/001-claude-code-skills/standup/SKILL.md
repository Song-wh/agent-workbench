---
name: standup
description: >-
  Write my daily standup from this repo's git history. Use when I say
  "standup", "what did I do yesterday", or "write my update".
---

# standup

1. Run `git log --since=yesterday --author="$(git config user.name)" --pretty="%h %s"`.
2. Group the commits by what they changed, not one line per commit.
3. Write exactly three sections:
   - **Yesterday:** what the commits show I finished.
   - **Today:** ask me. Do not guess.
   - **Blockers:** ask me. Do not guess.
4. Never invent work that is not in the log. If the log is empty, say so.
5. Keep the whole update under 80 words.
