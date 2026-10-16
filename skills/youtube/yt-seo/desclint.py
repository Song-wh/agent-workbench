#!/usr/bin/env python3
"""desclint.py - check a YouTube description before you paste it.

    python3 desclint.py description.txt
    python3 desclint.py description.txt --require "AI voice" --duration 503 --short

Checks the things YouTube rejects or silently ignores:
  - over 5,000 characters, or contains < or > (Studio refuses to save it)
  - chapters that will not render: first must be 00:00, at least 3, each at least 10 seconds,
    in order, and (with --duration) none past the end of the video
  - more than 60 hashtags (YouTube then ignores all of them); only the first 3 show above the title
  - a phrase you promised to include (--require, repeatable), e.g. an AI disclosure
It also prints the first two lines, which is all most viewers see before "...more".
--short: links in Shorts descriptions are not clickable, so it says so if it finds any.
Windows: use `python` instead of `python3`.
"""
import argparse, re, sys

TS = re.compile(r"^\s*(?:(\d{1,2}):)?(\d{1,2}):(\d{2})\s+\S")

def seconds(m):
    h, mnt, s = int(m.group(1) or 0), int(m.group(2)), int(m.group(3))
    return h * 3600 + mnt * 60 + s

def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--require", action="append", default=[])
    p.add_argument("--duration", type=float, help="video length in seconds")
    p.add_argument("--short", action="store_true")
    a = p.parse_args()
    text = open(a.file, encoding="utf-8").read().strip()
    problems, notes = [], []

    if len(text) > 5000:
        problems.append(f"{len(text)} characters - the limit is 5,000")
    bad = sorted(set(re.findall(r"[<>]", text)))
    if bad:
        line = next(i for i, l in enumerate(text.splitlines(), 1) if "<" in l or ">" in l)
        problems.append(f"contains {' and '.join(bad)} (first on line {line}) - Studio will not save it")

    chapters = [(seconds(m), l.strip()) for l in text.splitlines() if (m := TS.match(l))]
    if chapters:
        times = [t for t, _ in chapters]
        if times[0] != 0:
            problems.append(f"first chapter is {chapters[0][1][:20]!r}, it must start at 00:00")
        if len(chapters) < 3:
            problems.append(f"{len(chapters)} chapters - YouTube needs at least 3")
        if any(b <= x for x, b in zip(times, times[1:])):
            problems.append("chapter times are not in increasing order")
        ends = times[1:] + ([a.duration] if a.duration else [])
        for (t, label), e in zip(chapters, ends):
            if e - t < 10:
                problems.append(f"chapter {label[:30]!r} is {e - t:.0f}s - each must be at least 10s")
        if a.duration and times[-1] >= a.duration:
            problems.append("last chapter starts after the video ends")
        notes.append(f"{len(chapters)} chapters" + ("" if a.duration else " (pass --duration to check the last one)"))

    tags = re.findall(r"(?<!\w)#\w+", text)
    if len(tags) > 60:
        problems.append(f"{len(tags)} hashtags - over 60 and YouTube ignores all of them")
    elif tags:
        notes.append(f"hashtags shown above the title: {' '.join(tags[:3])}")

    for phrase in a.require:
        if phrase.lower() not in text.lower():
            problems.append(f"missing required phrase {phrase!r}")

    links = re.findall(r"https?://\S+", text)
    if a.short and links:
        notes.append(f"{len(links)} link(s): not clickable in a Shorts description - use the related-video field")

    first = text.splitlines()[:2]
    print("\n  first two lines (what shows before ...more):")
    for l in first:
        print(f"    {l[:140]}{'...' if len(l) > 140 else ''}")
    print(f"\n  {len(text)} characters" + "".join(f" · {n}" for n in notes))
    for pr in problems:
        print(f"  x  {pr}")
    print("  ok, nothing YouTube will reject" if not problems else f"  {len(problems)} problem(s)")
    sys.exit(1 if problems else 0)

if __name__ == "__main__":
    main()
