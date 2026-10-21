"""Save a snapshot of every signed-in channel's numbers and print what changed since the last one.

    python -X utf8 tools/yt/stats.py             # all channels that have a token
    python -X utf8 tools/yt/stats.py mystery

Snapshots append to tools/yt/data/<channel>.jsonl, one line per run: subscribers, total views, and per
video views/likes/comments. Reads cost a few quota units per channel.
"""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

import yaml

import plan
from auth import credentials, youtube

HERE = Path(__file__).parent
DATA = HERE / "data"
CHANNELS = yaml.safe_load((HERE / "channels.yaml").read_text(encoding="utf-8"))


def snapshot(key: str) -> dict:
    yt = youtube(key)
    ch = yt.channels().list(part="snippet,statistics,contentDetails", mine=True).execute()["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while True:
        page = yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50, pageToken=token).execute()
        ids += [i["contentDetails"]["videoId"] for i in page["items"]]
        token = page.get("nextPageToken")
        if not token:
            break
    videos = []
    for k in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet,statistics,contentDetails,status", id=",".join(ids[k:k + 50])).execute()["items"]:
            s = v["statistics"]
            videos.append({
                "id": v["id"], "title": v["snippet"]["title"],
                "published": v["status"].get("publishAt") or v["snippet"]["publishedAt"],
                "publish_at": v["status"].get("publishAt"),
                "privacy": v["status"]["privacyStatus"], "duration": v["contentDetails"]["duration"],
                "views": int(s.get("viewCount", 0)), "likes": int(s.get("likeCount", 0)), "comments": int(s.get("commentCount", 0)),
            })
    st = ch["statistics"]
    return {
        "at": dt.datetime.now().isoformat(timespec="seconds"), "channel": ch["snippet"]["title"],
        "subscribers": int(st.get("subscriberCount", 0)), "views": int(st.get("viewCount", 0)), "videos": videos,
    }


def last(path: Path) -> dict | None:
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    return json.loads(lines[-1]) if lines else None


def diff(n: int, before: int | None) -> str:
    return "" if before is None or n == before else f" ({n - before:+,})"


def report(new: dict, old: dict | None):
    o = {v["id"]: v for v in (old or {}).get("videos", [])}
    print(f"\n{new['channel']}  구독자 {new['subscribers']:,}{diff(new['subscribers'], old and old['subscribers'])}"
          f" · 조회수 {new['views']:,}{diff(new['views'], old and old['views'])}" + (f"   (지난 기록 {old['at']})" if old else "   (첫 기록)"))
    live = [v for v in new["videos"] if v["privacy"] == "public"]
    for v in sorted(live, key=lambda v: v["published"], reverse=True):
        p = o.get(v["id"], {})
        print(f"  {v['published'][:10]}  {v['views']:>7,}{diff(v['views'], p.get('views')):<8}  ♥{v['likes']:<4} 💬{v['comments']:<4} {v['title'][:60]}")
    waiting = len(new["videos"]) - len(live)
    if waiting:
        print(f"  (비공개·예약 {waiting}개)")


def sync(key: str, snap: dict) -> list[str]:
    """Set uploads.yaml status from what the channel actually has: public -> published, private with a publish time -> scheduled."""
    by_title = {v["title"]: v for v in snap["videos"]}
    changes = []
    for it in plan.load():
        if it.get("channel") != key or it.get("status") == "published":
            continue
        v = by_title.get(str(it.get("title")))
        if not v:
            continue
        new = "published" if v["privacy"] == "public" else "scheduled" if v.get("publish_at") else None
        if not new or new == it.get("status"):
            continue
        f = it["_dir"] / "uploads.yaml"
        text = f.read_text(encoding="utf-8")
        m = re.search(r'^- id: "?' + re.escape(str(it["id"])) + r'"?\n.*?(?=^- id: |\Z)', text, re.S | re.M)
        block = m.group(0)
        text = text[:m.start()] + re.sub(r"^(\s*status:\s*).*$", r"\g<1>" + new, block, count=1, flags=re.M) + text[m.end():]
        f.write_text(text, encoding="utf-8")
        changes.append(f"{it['id']}: {it.get('status')} -> {new}")
    return changes


def main():
    p = argparse.ArgumentParser()
    p.add_argument("channels", nargs="*", help="keys from channels.yaml; default: every channel with a token")
    a = p.parse_args()
    keys = a.channels or [k for k in CHANNELS if credentials(k)]
    if not keys:
        print("로그인한 채널이 없음: python -X utf8 tools/yt/auth.py <channel>")
        return
    DATA.mkdir(exist_ok=True)
    for key in keys:
        path = DATA / f"{key}.jsonl"
        old, new = last(path), snapshot(key)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(new, ensure_ascii=False) + "\n")
        report(new, old)
        for c in sync(key, new):
            print(f"  uploads.yaml {c}")


if __name__ == "__main__":
    main()
