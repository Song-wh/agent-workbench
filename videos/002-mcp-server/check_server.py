# Starts the MCP server over stdio (the way Claude Code does) and calls all three tools once.
import asyncio, sys, json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    p = StdioServerParameters(command=sys.executable, args=["-X", "utf8", "tools/yt/mcp_server.py"])
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print("tools:", [t.name for t in (await s.list_tools()).tools])
            for name, args in [("list_uploads", {"days_ahead": 7}), ("check_upload", {"id": "002"}), ("get_upload_text", {"id": "001"})]:
                res = await s.call_tool(name, args)
                print(f"\n## {name}({args})"); [print(c.text) for c in res.content]
asyncio.run(main())
