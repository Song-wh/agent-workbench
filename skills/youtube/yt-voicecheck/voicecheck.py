#!/usr/bin/env python3
"""voicecheck.py - transcribe a TTS narration sentence by sentence and list the sentences that did
not come out as written.

    python3 voicecheck.py narration.wav narration.json
    python3 voicecheck.py narration.wav narration.json --ignore names.txt --model small

narration.json is the sentence timeline: [{"text": "...", "start": 0.0, "end": 3.2}, ...]
(tools like speak.py write it next to the WAV). Windows: use `python` instead of `python3`.

Needs faster-whisper and soundfile: `pip install faster-whisper soundfile`.

Numbers are compared as numbers ("eighty-six" == "86"), British and American spellings are treated
as the same, and punctuation is ignored. Words in --ignore (one per line, e.g. place names Whisper
cannot spell) match whatever Whisper heard in their place - listen to those yourself.
WHAT THIS CAN AND CANNOT TELL YOU: Whisper is a second listener, not a judge. A flagged sentence is
worth listening to; a clean pass does not prove a name was pronounced well.
"""
import argparse, json, re, sys

UNITS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve "
         "thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split())}
TENS = {w: 10 * i for i, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "_"}
SCALES = {"hundred": 100, "thousand": 1000, "million": 10**6}
ORDINALS = {w: i for i, w in enumerate("_ first second third fourth fifth sixth seventh eighth ninth tenth eleventh "
            "twelfth thirteenth fourteenth fifteenth sixteenth seventeenth eighteenth nineteenth".split()) if w != "_"}
ORDINALS.update({"twentieth": 20, "thirtieth": 30})
UNITS.update(ORDINALS)
NUMBER_WORDS = set(UNITS) | set(TENS) | set(SCALES)
BRIT_STEMS = r"(rum|fav|col|behavi|hon|lab|neighb|hum|flav)our"
BRIT = {"centre": "center", "organise": "organize", "realise": "realize", "analyse": "analyze",
        "licence": "license", "programme": "program", "travelled": "traveled", "grey": "gray"}

def value(tokens):
    groups, total, cur = [], 0, 0
    for w in tokens:
        if w in UNITS or w in TENS:
            n = UNITS.get(w, TENS.get(w))
            joins = cur >= 20 and cur % 10 == 0 and cur < 100 and n < 10
            if cur and cur < 100 and not joins:
                groups.append(cur); cur = 0
            cur += n
        elif w == "hundred":
            cur = (cur or 1) * 100
        else:
            total += (cur or 1) * SCALES[w]; cur = 0
    if groups and not total:
        groups.append(cur)
        return groups[0] * 100 + groups[1] if len(groups) == 2 and all(g < 100 for g in groups) else groups[-1]
    return total + cur

def spoken_number(toks):
    """Words of one number -> digits. Handles 'two point six seven million'."""
    if "point" in toks:
        i = toks.index("point")
        head, tail = toks[:i], toks[i + 1:]
        scale = tail.pop() if tail and tail[-1] in SCALES else None
        num = f"{value(head) if head else 0}." + "".join(str(UNITS[w]) for w in tail if w in UNITS)
        return [num] + ([scale] if scale else [])
    return [str(value(toks))]

def normalize(text, ignore):
    t = text.lower().replace("-", " ").replace("%", " percent")
    t = re.sub(r"(\d),(\d)", r"\1\2", t)                 # 1,000 -> 1000
    t = re.sub(r"(\d)\s*million", r"\1 million", t)
    t = re.sub(r"(\w)\s+dot\s+(\w)", r"\1.\2", t)          # "plan dot py" is written "plan.py"
    out = []
    for chunk in re.split(r"[,;:!?]|\.(?!\d)", t):       # a number never runs across punctuation
        run = []
        for w in re.findall(r"[a-z0-9.']+", chunk) + [""]:
            w = w.strip(".'")
            if w and (w in NUMBER_WORDS or (w in ("and", "point") and run)):
                run.append(w)
                continue
            trailing_and = bool(run) and run[-1] == "and"
            toks = [x for x in run if x != "and"]
            if len(toks) == 1 and toks[0] in SCALES and out and out[-1].replace(".", "").isdigit():
                out.append(toks[0])                       # '2.67 million': the scale word stays a word
            elif toks:
                out.extend(spoken_number(toks))
            if trailing_and:
                out.append("and")
            run = []
            if not w:
                continue
            w = re.sub(r"^" + BRIT_STEMS + r"(s|ed|ing|ite|ites|able)?$", lambda m: m.group(1) + "or" + (m.group(2) or ""), w)
            w = BRIT.get(w, w)
            out.append("*" if w in ignore else w)
    # spelled-out letters ("M C P") and the acronym ("MCP") are the same word
    joined, letters = [], []
    for w in out + [""]:
        if len(w) == 1 and w.isalpha() and w not in ("a", "i"):
            letters.append(w)
            continue
        if letters:
            joined.append("".join(letters)); letters = []
        if w:
            joined.append(w)
    out = joined
    # a spoken "a thousand" is written "1000": drop the article in front of a bare number
    out = [w for i, w in enumerate(out) if not (w == "a" and i + 1 < len(out) and out[i + 1].replace(".", "").isdigit())]
    return out

def matches(want, got):
    """Equal, except that each '*' (an ignored word, usually a name) may be heard as one or two words."""
    import difflib
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=want, b=got, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        if op == "replace" and all(w == "*" for w in want[i1:i2]) and (j2 - j1) <= 2 * (i2 - i1):
            continue
        return False
    return True

def main():
    p = argparse.ArgumentParser()
    p.add_argument("wav")
    p.add_argument("timeline")
    p.add_argument("--ignore", help="file with words to skip (one per line)")
    p.add_argument("--model", default="small")
    p.add_argument("--lang", default="en")
    a = p.parse_args()
    import numpy as np
    import soundfile as sf
    from faster_whisper import WhisperModel

    ignore = set()
    if a.ignore:
        ignore = {l.strip().lower() for l in open(a.ignore, encoding="utf-8") if l.strip()}
    audio, sr = sf.read(a.wav, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    timeline = json.load(open(a.timeline, encoding="utf-8"))
    model = WhisperModel(a.model, device="cpu", compute_type="int8")

    bad = 0
    for i, s in enumerate(timeline):
        seg = audio[int(s["start"] * sr): int(s["end"] * sr) + int(0.1 * sr)]
        seg16 = np.interp(np.linspace(0, len(seg) - 1, int(len(seg) * 16000 / sr)), np.arange(len(seg)), seg).astype(np.float32)
        heard = " ".join(x.text.strip() for x in model.transcribe(seg16, language=a.lang)[0])
        want, got = normalize(s["text"], ignore), normalize(heard, ignore)
        if not matches(want, got):
            bad += 1
            m, ss = divmod(s["start"], 60)
            print(f"\n  #{i}  {int(m):02d}:{ss:04.1f}")
            print(f"    written  {s['text'].strip()}")
            print(f"    heard    {heard}")
    print(f"\n  {len(timeline)} sentences, {bad} to listen to" + ("" if bad else " - none flagged"))

if __name__ == "__main__":
    sys.exit(main())
