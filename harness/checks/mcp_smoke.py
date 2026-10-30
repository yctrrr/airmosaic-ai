"""Read-only stdio connectivity check; no personal roots or data are required."""

import asyncio
import json
import sys


async def check():
    from mcp import Client
    from mcp.client.stdio import StdioServerParameters

    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-I", "-B", "-X", "utf8", "-m", "runtime.mcp_server"],
    )
    async with Client(parameters, read_timeout_seconds=15) as client:
        tools = await client.list_tools()
        resources = await client.list_resources()
        datasets = await client.call_tool("airmosaic_list_datasets")
        if datasets.is_error:
            raise RuntimeError("metadata_query_failed")
        return {"connected": True, "read_only": True, "tool_count": len(tools.tools),
                "resource_count": len(resources.resources),
                "dataset_count": len(datasets.structured_content["result"])}


if __name__ == "__main__":
    try:
        print(json.dumps(asyncio.run(check())))
    except Exception:
        print('{"error":"mcp_smoke_failed"}', file=sys.stderr)
        raise SystemExit(2) from None
