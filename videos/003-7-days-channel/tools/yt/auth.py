"""OAuth for the YouTube APIs, one token per channel.

    python -X utf8 tools/yt/auth.py mystery      # opens a browser: sign in, pick the Blank Spot Files channel

The client comes from tools/yt/client_secret.json (Desktop app, never committed). Tokens are saved to
tools/yt/tokens/<channel>.json (never committed) and refreshed automatically. The scopes cover everything
the roadmap needs (stats, analytics, comments, uploads) so a channel only has to sign in once.
"""
import argparse
import json
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import yaml

HERE = Path(__file__).parent
SECRET = HERE / "client_secret.json"
TOKENS = HERE / "tokens"
CHANNELS = yaml.safe_load((HERE / "channels.yaml").read_text(encoding="utf-8"))
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def credentials(channel: str) -> Credentials | None:
    """Saved credentials for a channel, refreshed if needed; None if it never signed in."""
    path = TOKENS / f"{channel}.json"
    if not path.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(path), SCOPES)
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
        path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def youtube(channel: str):
    creds = credentials(channel)
    if not creds:
        sys.exit(f"'{channel}' has no token yet: python -X utf8 tools/yt/auth.py {channel}")
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("channel", choices=list(CHANNELS), help="key from channels.yaml")
    a = p.parse_args()
    if not SECRET.exists():
        sys.exit("tools/yt/client_secret.json is missing (Google Cloud → OAuth client ID → Desktop app → download JSON)")
    flow = InstalledAppFlow.from_client_secrets_file(str(SECRET), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline",
                                  authorization_prompt_message="Sign in and choose the channel '{}' in the browser: {{url}}".format(a.channel))
    me = build("youtube", "v3", credentials=creds, cache_discovery=False).channels().list(part="snippet", mine=True).execute()
    got = [(c["snippet"]["title"], c["snippet"].get("customUrl", "")) for c in me.get("items", [])]
    want = str(CHANNELS[a.channel].get("handle") or "").lower()
    if want and not any(u.lower() == want for _, u in got):
        sys.exit(f"wrong channel: signed in as {got}, expected {want}. Run again and pick that channel in the browser.")
    TOKENS.mkdir(exist_ok=True)
    (TOKENS / f"{a.channel}.json").write_text(creds.to_json(), encoding="utf-8")
    print(json.dumps({"channel": a.channel, "signed_in_as": got}, ensure_ascii=False))


if __name__ == "__main__":
    main()
