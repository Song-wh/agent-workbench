# 003 · 8 Days of Real Numbers From a Channel Claude Code Made

The scripts that printed every number in the video. Claude Code wrote them; I read them and run them on my own channels.

| Script | What it does |
|---|---|
| [`tools/yt/auth.py`](tools/yt/auth.py) | Google sign-in, one token per channel. Refuses to save if you pick a different channel than `channels.yaml` says |
| [`tools/yt/stats.py`](tools/yt/stats.py) | YouTube Data API: subscribers, views, likes, comments per video. Appends to `data/<channel>.jsonl` and shows the change since the last run |
| [`tools/yt/analytics.py`](tools/yt/analytics.py) | YouTube Analytics API: watch time, average view duration and percentage, traffic sources, retention (videos over 60 s). Reporting API: impressions and click-through rate |
| [`tools/yt/plan.py`](tools/yt/plan.py) | Upload calendar and pre-upload checks for every `uploads.yaml` (title length, tags, AI voice disclosure, thumbnail…) |

The output messages are in Korean (I'm Korean). The numbers and column order match the video.

## Set up (once)

1. Google Cloud console → new project → enable **YouTube Data API v3**, **YouTube Analytics API**, **YouTube Reporting API**.
2. OAuth consent screen: External, add yourself as a test user (or publish it to production so the sign-in does not expire every 7 days).
3. Credentials → OAuth client ID → **Desktop app** → download the JSON to `tools/yt/client_secret.json`. It is in `.gitignore`. Never commit it.
4. Edit [`tools/yt/channels.yaml`](tools/yt/channels.yaml): your channel's name and `@handle`.

## Run it

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt      # macOS/Linux: .venv/bin/python
.venv/Scripts/python -X utf8 tools/yt/auth.py dev             # browser opens: pick your channel
.venv/Scripts/python -X utf8 tools/yt/stats.py
.venv/Scripts/python -X utf8 tools/yt/analytics.py
```

Two things I saw that you will probably see too:

- **The two APIs can disagree.** On the same day, the Data API said my long video had 8 views and the Analytics API said 5. I don't know which one is right, so I show both.
- **Impressions and CTR show up a day late.** They only exist in Reporting API bulk reports. The first `analytics.py` run creates the daily job, and files appear about a day later.

Tokens go to `tools/yt/tokens/` and numbers to `tools/yt/data/`. Both stay on your computer and are in `.gitignore`.
