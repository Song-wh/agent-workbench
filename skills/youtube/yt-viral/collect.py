#!/usr/bin/env python3
"""collect.py - build swipe.py's input from public channel listings with yt-dlp.

    python3 collect.py @Nexpo @LEMMiNO https://www.youtube.com/channel/UC... -o collected.json
    python3 collect.py --file channels.txt --limit 40 -o collected.json
    python3 collect.py --search "unsolved mystery japan" --search "korean unsolved case" -o search.json

Reads the public /videos tab only (long-form; Shorts are a different tab and a different game),
newest first, up to --limit per channel. No login, no cookies, no account. Needs yt-dlp:
`pip install yt-dlp`. Windows: use `python` instead of `python3`.

--search writes the raw search results (channel, channel_url, title, views, duration) per query
instead - useful for finding channels in a niche before collecting them.
"""
import argparse, concurrent.futures as cf, json, shutil, subprocess, sys

def ytdlp():
    exe = shutil.which("yt-dlp")
    if exe:
        return [exe]
    return [sys.executable, "-m", "yt_dlp"]

def run(args):
    r = subprocess.run(ytdlp() + args, capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None

def channel_url(h):
    if h.startswith("http"):
        return h.rstrip("/") + "/videos"
    return f"https://www.youtube.com/@{h.lstrip('@')}/videos"

def one_channel(h, limit):
    d = run(["--flat-playlist", "-J", "--playlist-end", str(limit), channel_url(h)])
    if not d:
        return h, None, []
    name = d.get("channel") or d.get("uploader") or h
    vids = [{"channel": name, "title": e.get("title"), "views": e.get("view_count"),
             "url": e.get("url"), "duration": e.get("duration")}
            for e in d.get("entries", []) if e.get("view_count")]
    return h, name, vids

def one_search(q, limit):
    d = run(["--flat-playlist", "-J", f"ytsearch{limit}:{q}"])
    rows = [{"channel": e.get("channel"), "channel_url": e.get("channel_url"), "title": e.get("title"),
             "views": e.get("view_count"), "duration": e.get("duration")} for e in (d or {}).get("entries", [])]
    return q, rows

def main():
    p = argparse.ArgumentParser()
    p.add_argument("channels", nargs="*", help="@handle, handle, or channel URL")
    p.add_argument("--file", help="one channel per line")
    p.add_argument("--search", action="append", default=[], help="a search query (repeatable)")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("-o", "--out", default="collected.json")
    a = p.parse_args()

    if a.search:
        out = {}
        with cf.ThreadPoolExecutor(6) as ex:
            for q, rows in ex.map(lambda q: one_search(q, a.limit), a.search):
                out[q] = rows
                print(f"  {len(rows):3d} results  {q}", file=sys.stderr)
        json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"wrote {a.out}", file=sys.stderr)
        return

    chans = list(a.channels)
    if a.file:
        chans += [l.strip() for l in open(a.file, encoding="utf-8") if l.strip() and not l.startswith("#")]
    if not chans:
        p.print_help(); sys.exit(1)
    allv = []
    with cf.ThreadPoolExecutor(6) as ex:
        for h, name, vids in ex.map(lambda h: one_channel(h, a.limit), chans):
            note = "" if vids else "  <- nothing collected (wrong handle, or yt-dlp missing/blocked)"
            if vids and len(vids) < 4:
                note = "  <- under 4 videos, swipe.py will skip it"
            print(f"  {len(vids):3d}  {h}  ({name}){note}", file=sys.stderr)
            allv += vids
    json.dump(allv, open(a.out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"wrote {len(allv)} videos to {a.out}. Check the channel names above: a handle can belong to someone else.", file=sys.stderr)

if __name__ == "__main__":
    main()
