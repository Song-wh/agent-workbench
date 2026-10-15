"""MCP server over the upload calendar in plan.py.

    .venv/Scripts/python -X utf8 tools/yt/mcp_server.py

Exposes three tools: list_uploads, check_upload, get_upload_text. All checks and
loading are done by plan.py; this file only shapes the output for MCP clients.
"""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan  # noqa: E402

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("yt-upload-calendar")

STATUS_LABEL = {
    "published": "✅ published",
    "scheduled": "⏰ scheduled",
    "ready": "📦 ready",
    "draft": "✏️ draft",
}


def _find(items, id: str):
    it = next((i for i in items if str(i["id"]) == str(id)), None)
    if it is None:
        raise ValueError(f"no upload with id '{id}'")
    return it


@mcp.tool()
def list_uploads(days_ahead: int = 7) -> list[dict]:
    """What is going up on each channel in the next `days_ahead` days, with status."""
    items = plan.load()
    ids = {str(i["id"]) for i in items}
    now = dt.datetime.now()
    until = now + dt.timedelta(days=days_ahead)
    rows = sorted(
        (it for it in items if it["_when"] and now <= it["_when"] <= until),
        key=lambda it: it["_when"],
    )
    out = []
    for it in rows:
        ch = plan.CHANNELS.get(it["channel"])
        out.append(
            {
                "id": str(it["id"]),
                "channel": ch["name"] if ch else it["channel"],
                "type": it["type"],
                "title": it["title"],
                "publish": it["_when"].strftime("%Y-%m-%d %H:%M"),
                "status": it.get("status"),
                "status_label": STATUS_LABEL.get(it.get("status"), it.get("status") or "?"),
                "problems": len(plan.check(it, ids)),
            }
        )
    return out


@mcp.tool()
def check_upload(id: str) -> list[str]:
    """The problems plan.py finds for one upload, by id. Empty list means it's clean."""
    items = plan.load()
    ids = {str(i["id"]) for i in items}
    it = _find(items, id)
    return plan.check(it, ids)


@mcp.tool()
def get_upload_text(id: str) -> dict:
    """Title, description and tags for one upload, ready to paste into YouTube Studio."""
    items = plan.load()
    it = _find(items, id)
    return {
        "id": str(it["id"]),
        "title": it.get("title") or "",
        "description": plan.description(it) or "",
        "tags": it.get("tags") or [],
    }


if __name__ == "__main__":
    mcp.run()
