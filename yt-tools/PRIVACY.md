# yt-tools — Privacy Policy

Last updated: 2026-10-20

yt-tools is a private command-line tool used by one person to manage their own YouTube channels
(Agent Workbench, Blank Spot Files, Filed and Granted). It is not offered to the public and has no
other users.

## What it accesses
Through the YouTube Data API, YouTube Analytics API and YouTube Reporting API, with the channel
owner's own OAuth consent:
- the owner's channel and video statistics (views, likes, comment counts, subscribers),
- the owner's channel analytics (watch time, audience retention, traffic sources, impressions, click-through rate),
- uploading the owner's own videos, thumbnails and captions, and scheduling them.

## What it stores, and where
Statistics and analytics are saved as files on the owner's own computer and in the owner's private
Git repository. OAuth tokens are stored only on the owner's computer and are never shared or committed.
No data about other YouTube users is collected, stored, sold or shared. Nothing is sent to any third party.

## Data retention and deletion
- Statistics and analytics data of the owner's channels are kept only as long as the owner keeps the files.
  They are deleted by deleting the `data/` folder (and its Git history) on the owner's computer.
- OAuth tokens are deleted by deleting the `tokens/` folder. YouTube API data is refreshed or deleted at
  least every 30 days, as required by the YouTube API Services Developer Policies.
- No data about any other person is ever collected, so there is nothing else to delete.

## Revoking access
The owner can revoke yt-tools' access at any time at https://myaccount.google.com/permissions
(security settings page for third-party apps). Deleting the local token files also stops all access.

## YouTube API Services and Google
yt-tools uses YouTube API Services. By using yt-tools you agree to be bound by the YouTube Terms of Service. See the YouTube Terms of Service (https://www.youtube.com/t/terms)
and the Google Privacy Policy (https://policies.google.com/privacy).

## Contact
Open an issue at https://github.com/Song-wh/agent-workbench/issues
