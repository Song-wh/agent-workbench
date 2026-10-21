"""Watch-time numbers from the YouTube Analytics API, and impressions/CTR from the Reporting API.

    python -X utf8 tools/yt/analytics.py                 # every signed-in channel, last 28 days
    python -X utf8 tools/yt/analytics.py mystery --days 7

Per video: views, watch minutes, average view duration and percentage, subscribers gained, and (for
videos over 60 s) the retention curve. Per channel: where views come from (traffic sources).
Impressions and click-through rate only exist in the Reporting API's bulk reports: the first run creates
a daily `channel_reach_basic_a1` job, and YouTube starts producing files about a day later. Each run
downloads any new ones to tools/yt/data/reach/<channel>/.
Analytics data lags by two to three days, so the newest uploads show up late.

Results go to tools/yt/data/analytics/<channel>.json (latest run, overwritten).
"""
import argparse
import csv
import datetime as dt
import io
import json
import re
from pathlib import Path

import yaml
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession

from auth import credentials

HERE = Path(__file__).parent
DATA = HERE / "data"
CHANNELS = yaml.safe_load((HERE / "channels.yaml").read_text(encoding="utf-8"))
REACH = "channel_reach_basic_a1"
METRICS = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,likes"


def seconds(iso: str) -> int:
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    d, h, mi, s = (int(x or 0) for x in m.groups()) if m else (0, 0, 0, 0)
    return d * 86400 + h * 3600 + mi * 60 + s


def table(r: dict) -> list[dict]:
    names = [h["name"] for h in r.get("columnHeaders", [])]
    return [dict(zip(names, row)) for row in r.get("rows", [])]


def watch(key: str, days: int) -> dict:
    creds = credentials(key)
    ya = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    end = dt.date.today()
    start = end - dt.timedelta(days=days)
    q = dict(ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat())

    rows = table(ya.reports().query(**q, metrics=METRICS, dimensions="video", sort="-views", maxResults=200).execute())
    info = {}
    ids = [r["video"] for r in rows]
    for k in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet,contentDetails", id=",".join(ids[k:k + 50])).execute()["items"]:
            info[v["id"]] = {"title": v["snippet"]["title"], "length_s": seconds(v["contentDetails"]["duration"])}
    for r in rows:
        r.update(info.get(r["video"], {}))
        if r.get("length_s", 0) > 60 and r["views"] >= 1:
            curve = table(ya.reports().query(**q, metrics="audienceWatchRatio", dimensions="elapsedVideoTimeRatio",
                                             filters=f"video=={r['video']}").execute())
            r["retention"] = [[c["elapsedVideoTimeRatio"], round(c["audienceWatchRatio"], 3)] for c in curve]
    sources = table(ya.reports().query(**q, metrics="views,estimatedMinutesWatched", dimensions="insightTrafficSourceType", sort="-views").execute())
    return {"at": dt.datetime.now().isoformat(timespec="seconds"), "from": q["startDate"], "to": q["endDate"], "videos": rows, "sources": sources}


def reach(key: str) -> list[dict]:
    """Make sure the daily reach job exists, download new report files, return per-video impressions/CTR."""
    creds = credentials(key)
    yr = build("youtubereporting", "v1", credentials=creds, cache_discovery=False)
    session = AuthorizedSession(creds)
    jobs = [j for j in yr.jobs().list().execute().get("jobs", []) if j["reportTypeId"] == REACH]
    job = jobs[0] if jobs else yr.jobs().create(body={"reportTypeId": REACH, "name": f"{key}-reach"}).execute()
    folder = DATA / "reach" / key
    folder.mkdir(parents=True, exist_ok=True)
    for rep in yr.jobs().reports().list(jobId=job["id"]).execute().get("reports", []):
        out = folder / f"{rep['startTime'][:10]}.csv"
        if out.exists():
            continue
        resp = session.get(rep["downloadUrl"])
        resp.raise_for_status()
        out.write_bytes(resp.content)
    totals: dict[str, dict] = {}
    for f in sorted(folder.glob("*.csv")):
        for row in csv.DictReader(io.StringIO(f.read_text(encoding="utf-8"))):
            t = totals.setdefault(row["video_id"], {"impressions": 0, "clicks": 0.0})
            imp = int(float(row.get("video_thumbnail_impressions") or 0))
            t["impressions"] += imp
            t["clicks"] += imp * float(row.get("video_thumbnail_impressions_ctr") or 0)
    return [{"video": v, "impressions": t["impressions"], "ctr": round(t["clicks"] / t["impressions"], 4) if t["impressions"] else None}
            for v, t in sorted(totals.items(), key=lambda kv: -kv[1]["impressions"])]


def report(name: str, w: dict, r: list[dict]):
    imp = {x["video"]: x for x in r}
    print(f"\n{name}  {w['from']} ~ {w['to']}")
    print(f"  {'조회':>5} {'시청(분)':>7} {'평균':>6} {'평균%':>6} {'노출':>6} {'CTR':>6}  제목")
    for v in w["videos"]:
        i = imp.get(v["video"], {})
        ctr = f"{i['ctr'] * 100:.1f}%" if i.get("ctr") is not None else "-"
        print(f"  {v['views']:>5} {v['estimatedMinutesWatched']:>7} {v['averageViewDuration']:>5}s {v['averageViewPercentage']:>5.1f}% "
              f"{i.get('impressions', '-'):>6} {ctr:>6}  {v.get('title', v['video'])[:56]}")
    if w["sources"]:
        print("  유입: " + " · ".join(f"{s['insightTrafficSourceType']} {s['views']}" for s in w["sources"][:6]))
    if not r:
        print("  노출수·CTR: 보고서 작업을 만들었거나 기다리는 중 (첫 파일은 하루쯤 뒤에 생김)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("channels", nargs="*")
    p.add_argument("--days", type=int, default=28)
    a = p.parse_args()
    keys = a.channels or [k for k in CHANNELS if credentials(k)]
    (DATA / "analytics").mkdir(parents=True, exist_ok=True)
    for key in keys:
        w = watch(key, a.days)
        r = reach(key)
        (DATA / "analytics" / f"{key}.json").write_text(json.dumps({**w, "reach": r}, ensure_ascii=False, indent=1), encoding="utf-8")
        report(CHANNELS[key]["name"], w, r)


if __name__ == "__main__":
    main()
