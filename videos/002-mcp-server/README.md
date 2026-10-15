# 002 · Build a Real MCP Server With Claude Code

An MCP server that lets Claude read my YouTube upload calendar. Claude Code wrote [`tools/yt/mcp_server.py`](tools/yt/mcp_server.py) from one prompt (plus one permission fix that was my mistake). It wraps [`tools/yt/plan.py`](tools/yt/plan.py), which reads every `uploads.yaml` and checks for things YouTube Studio would reject.

The checker's messages are in Korean (I'm Korean). In the video, Claude kept the Korean and added English next to each one.

## Tools

| Tool | Returns |
|---|---|
| `list_uploads(days_ahead)` | What is going up in the next N days, with status and problem count |
| `check_upload(id)` | The problems `plan.py` finds for one upload (empty = clean) |
| `get_upload_text(id)` | Title, description and tags, ready to paste |

## Run it

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt      # macOS/Linux: .venv/bin/python
.venv/Scripts/python -X utf8 tools/yt/plan.py --all          # the calendar + checks
.venv/Scripts/python -X utf8 check_server.py                  # start the server and call all three tools
```

**Version note:** this code uses `mcp` 1.x (the video used 1.30.0). `mcp` 2.x renamed `FastMCP` to `MCPServer`, so `requirements.txt` pins `mcp<2`.

## Register it with Claude Code

```bash
claude mcp add yt-calendar -- <full path>/.venv/Scripts/python.exe -X utf8 <full path>/tools/yt/mcp_server.py
claude mcp list
```

Then ask: *"What's going up on my channels in the next 7 days? Is anything not ready?"*

## Your own data

Put an `uploads.yaml` in each video folder (see [`example/uploads.yaml`](example/uploads.yaml)) and list your channels in [`tools/yt/channels.yaml`](tools/yt/channels.yaml). `plan.py` searches for `uploads.yaml` files under this folder.

## The prompt Claude Code got

```
Build an MCP server for my upload calendar.

- File: tools/yt/mcp_server.py, using the official Python MCP SDK (FastMCP). It is already installed in .venv.
- Reuse tools/yt/plan.py. Import its functions. Do not copy the checks.
- Three tools:
  1. list_uploads(days_ahead) - what is going up on each channel, with status.
  2. check_upload(id) - the problems plan.py finds for one upload.
  3. get_upload_text(id) - title, description and tags, ready to paste into YouTube Studio.
- Test it by calling each tool once from Python, not just by reading the code.
- At the end, give me the exact command to register it with Claude Code.
```

## What broke

The first headless run (`claude -p`) stopped after writing the server: my allow rule was `Bash(.venv/Scripts/python:*)`, and Claude ran `./.venv/Scripts/python.exe`. Permission rules match the text of the command, not the program. On Windows, write the rule after you see the exact command.
