---
name: yt-voicecheck
description: >-
  Check an AI/TTS narration before it goes into a video - transcribe it sentence by sentence and
  list the lines that did not come out as written, with timestamps. Use for "check the narration",
  "did the voice say it right", "pronunciation check", after generating TTS audio, or before rendering.
---

# yt-voicecheck

A TTS voice will read a script you would never notice is wrong until a viewer does: a place name
turned into another word, "Claude said" heard as "clods at", a key phrase that sounds like its
opposite. Listening to eight minutes for that is how it gets missed. A second listener finds the
lines worth your ears.

```bash
# Windows: there is no python3 command, use python instead
python3 voicecheck.py narration.wav narration.json
python3 voicecheck.py narration.wav narration.json --ignore names.txt
```

`narration.json` is the sentence timeline next to the WAV: `[{"text", "start", "end"}, ...]`.

## Reading the output

Numbers are compared as numbers and British/American spellings as equal, so what is left is what
was actually heard differently. For every flagged line, decide which of three it is:

1. **Mispronounced** - rewrite the line or respell the word for the voice (keep the real spelling
   for captions), regenerate, check again.
2. **Whisper's mistake** - names it cannot spell, homophones ("Seoul" / "sole"). Listen once; if
   it is right, move on. Put recurring names in `--ignore`.
3. **Ambiguous for a human too** - a key phrase that Whisper hears as another word ("record stops"
   heard as "record starts") will be misheard by some viewers. Change the words, not the voice.

Never wave a flag through without listening. A clean run is not proof either: it means Whisper
heard the words, not that a name sounded natural.

## What to hand back

The flagged lines with timestamps, which of the three each one is, and the rewritten lines for
the ones that need regenerating. Then run it again on the new audio.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
