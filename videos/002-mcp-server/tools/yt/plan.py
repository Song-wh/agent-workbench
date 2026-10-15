"""Upload calendar + pre-flight checks for every channel.

Reads tools/yt/channels.yaml and every uploads.yaml under the repo, prints one calendar across all
channels, and flags what would go wrong in YouTube Studio before you get there.

    python -X utf8 tools/yt/plan.py            # from 7 days ago onward
    python -X utf8 tools/yt/plan.py --all      # everything
    python -X utf8 tools/yt/plan.py --id 001-s2   # print the copy-paste block for one upload
"""
import argparse, datetime as dt, pathlib, re, sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHANNELS = yaml.safe_load((ROOT / "tools/yt/channels.yaml").read_text(encoding="utf-8"))
WEEK = "월화수목금토일"
LIVE = {"scheduled", "published"}  # already in YouTube Studio


def load():
    items = []
    for f in sorted(ROOT.glob("**/uploads.yaml")):
        if "node_modules" in f.parts:
            continue
        for it in yaml.safe_load(f.read_text(encoding="utf-8")) or []:
            it["_dir"] = f.parent
            it["_when"] = dt.datetime.strptime(str(it["publish"]), "%Y-%m-%d %H:%M") if it.get("publish") else None
            items.append(it)
    return items


def section(path: pathlib.Path, key: str) -> str:
    """Text of the first ``` block after a line reading **KEY** in a Markdown file."""
    lines = path.read_text(encoding="utf-8").splitlines()
    i = lines.index(f"**{key}**")
    start = next(j for j in range(i + 1, len(lines)) if lines[j].startswith("```")) + 1
    end = next(j for j in range(start, len(lines)) if lines[j].startswith("```"))
    return "\n".join(lines[start:end])


def description(it) -> str | None:
    d = it["_dir"]
    if it.get("description"):
        return it["description"]
    try:
        if it.get("description_file"):
            return (d / it["description_file"]).read_text(encoding="utf-8").strip()
        if it.get("description_section"):
            f, key = it["description_section"].split("#")
            return section(d / f, key)
    except (FileNotFoundError, ValueError, StopIteration):
        return None
    return None


def check(it, ids) -> list[str]:
    ch = CHANNELS.get(it["channel"])
    if not ch:
        return [f"알 수 없는 채널 '{it['channel']}'"]
    out, d, live = [], it["_dir"], it.get("status") in LIVE
    dur = it.get("duration_s") or 0
    title = str(it.get("title") or "")
    desc = description(it) or ""

    if not (d / it["file"]).exists() and not live:
        out.append(f"영상 파일 없음: {it['file']}")
    if not title:
        out.append("제목 없음")
    if len(title) > 100:
        out.append(f"제목 {len(title)}자 (한도 100)")
    if re.search(r"[<>]", title + desc):
        out.append("제목/설명에 < 또는 > (YouTube가 거부함)")
    if not desc:
        out.append("설명 없음")
    if len(desc) > 5000:
        out.append(f"설명 {len(desc)}자 (한도 5000)")
    if desc and ch["disclosure"].lower() not in desc.lower():
        out.append(f"AI 음성 공개 문구 없음 (\"{ch['disclosure']}\" 포함해야 함)")
    tags = it.get("tags") or []
    if sum(len(t) for t in tags) + 2 * len(tags) > 500:
        out.append("태그 합계 500자 초과")
    if it["type"] == "long":
        if dur > 15 * 60 and not ch["verified"]:
            out.append(f"{dur // 60}분 영상인데 채널 인증 전 (15분 초과 업로드 불가)")
        if not it.get("thumbnail"):
            out.append("썸네일 지정 안 됨")
        elif not (d / it["thumbnail"]).exists() and not live:
            out.append(f"썸네일 파일 없음: {it['thumbnail']}")
        elif not ch["verified"]:
            out.append("채널 인증 전이라 맞춤 썸네일 불가")
    if it["type"] == "short" and dur > 180:
        out.append(f"Short가 {dur}초 (한도 180초)")
    if it.get("related") and it["related"] not in ids:
        out.append(f"관련 동영상 '{it['related']}'이 목록에 없음")
    if it["_when"] and it["_when"] < dt.datetime.now() and not live:
        out.append("공개 시각이 지났는데 아직 Studio에 안 올라감")
    if not it["_when"]:
        out.append("공개 시각 없음")
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true")
    p.add_argument("--id")
    a = p.parse_args()
    items = load()
    ids = {str(i["id"]) for i in items}

    if a.id:
        it = next(i for i in items if str(i["id"]) == a.id)
        print(f"[{CHANNELS[it['channel']]['name']}] {it['_when']:%Y-%m-%d %H:%M} KST")
        print(f"파일: {it['_dir'] / it['file']}")
        if it.get("thumbnail"):
            print(f"썸네일: {it['_dir'] / it['thumbnail']}")
        print(f"\n제목:\n{it['title']}\n\n설명:\n{description(it)}")
        if it.get("tags"):
            print("\n태그:\n" + ", ".join(it["tags"]))
        if it.get("related"):
            print(f"\n관련 동영상: {it['related']} (Studio에서 직접 연결)")
        return

    since = dt.datetime.min if a.all else dt.datetime.now() - dt.timedelta(days=7)
    rows = sorted((i for i in items if not i["_when"] or i["_when"] >= since), key=lambda i: i["_when"] or dt.datetime.max)
    problems, day = 0, None
    for it in rows:
        w = it["_when"]
        if w and w.date() != day:
            day = w.date()
            print(f"\n{day:%m-%d} ({WEEK[day.weekday()]})")
        mark = {"published": "✅", "scheduled": "⏰", "ready": "📦", "draft": "✏️"}.get(it.get("status"), "?")
        print(f"  {w:%H:%M} {mark} {CHANNELS[it['channel']]['name'][:16]:16} {it['type']:5} {str(it['id']):8} {it['title'][:60]}")
        for msg in check(it, ids):
            problems += 1
            print(f"         ⚠ {msg}")
    print(f"\n{len(rows)}개, 문제 {problems}개  (✅ 공개됨 ⏰ 예약됨 📦 준비됨 ✏️ 작성 중)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
