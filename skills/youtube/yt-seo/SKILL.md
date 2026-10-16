---
name: yt-seo
description: >-
  Write the description, tags and search-facing text for a YouTube video,
  aimed at the query a real person types. Use for "write my description",
  "tags", "SEO", "help this video get found", "nobody is finding this".
---

# yt-seo

Search is a smaller lever than packaging and a bigger one than people think for evergreen videos.
For a video aimed at the subscriber feed, say so and spend the effort on `/yt-package` instead.

## Before you write

1. Find the voice profile and read it. Use the first `voice.md` you find walking up from the folder
   you are working in to the project root (a channel folder such as `mystery/voice.md` overrides),
   then `~/.claude/youtube/voice.md`. With more than one channel, say which profile you used.
   That is the user's voice profile for this channel: how they talk
   on camera, the words they never use, who they are talking to, what they will not claim. If it
   does not exist, ask for **three of their own videos**, read or transcribe them, infer the voice,
   and write the file. A script in the wrong voice is worse than no script, because they have to
   read it out loud.
2. Never invent a number, a result or a source. If a figure would strengthen it and you do not have
   one, ask for it or write the line without it.

## The description

- **The first two lines are the only ones anyone reads.** They show above "...more" and they are
  the search snippet. Say what the video gives them, in the words they would have typed.
- Then the link or the resource, if there is one, so it is above the fold.
- Then chapters (`/yt-chapters` writes them).
- Then the long version: what is covered, who it is for, what it assumes.

## Lint it before handing it over

```bash
# Windows: there is no python3 command, use python instead
python3 desclint.py description.txt --require "AI voice" --duration 503
python3 desclint.py short-description.txt --short
```

It catches what Studio refuses or silently drops: over 5,000 characters, a `<` or `>` anywhere
(Studio will not save it - watch for `->` in code), chapters that will not render (00:00 first,
at least 3, each at least 10 seconds), more than 60 hashtags, and any phrase you promised to
include, such as an AI-voice disclosure. Links in a Shorts description are not clickable; use the
related-video field instead.

## Tags, honestly

Tags are a weak signal and YouTube has said so. Use them for disambiguation - spellings, the tool
names, the abbreviations people actually type - and stop. Fifteen is plenty. A wall of tags is not
a strategy and stuffing unrelated ones is against the terms.

## The query test

Before handing anything over, write the three search queries this video should win, and check the
title and first two description lines contain the words in those queries. If they do not, the
problem is the title, not the description.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
