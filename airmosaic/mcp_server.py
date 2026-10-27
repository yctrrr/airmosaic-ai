"""Local stdio MCP transport over the existing AirMosaic services."""

from __future__ import annotations

import argparse
import asyncio
from contextlib import asynccontextmanager
import json
import logging
import sys
import threading

from .services.mcp_gateway import MCPGateway, MCPGatewayError, MCPPolicy
from .services.tool_registry import ToolRegistryError


def create_server(gateway: MCPGateway | None = None):
    # Optional SDK: normal CLI/SDK imports and --help do not require MCP.
    import anyio
    from mcp.server import Server
    from mcp.types import (CallToolResult, ListResourcesResult, ListToolsResult,
                           ReadResourceResult, Resource, TextContent,
                           TextResourceContents, Tool, ToolAnnotations)

    gateway = gateway or MCPGateway()
    slots = asyncio.Semaphore(1)
    active: dict[threading.Event, asyncio.Task] = {}

    async def join_cancelled(event, worker):
        event.set()
        with anyio.CancelScope(shield=True):
            with anyio.move_on_after(30):
                await asyncio.shield(worker)

    @asynccontextmanager
    async def lifespan(server):
        try:
            yield
        finally:
            pending = list(active.items())
            for event, _ in pending:
                event.set()
            for event, worker in pending:
                await join_cancelled(event, worker)

    async def list_tools(context, params):
        return ListToolsResult(tools=[Tool(**{**item, "annotations": ToolAnnotations(**item["annotations"])})
                                      for item in gateway.tools()])

    async def call_tool(context, params):
        # Keep transport responsive while the runner monitors an owned process.
        # A cancelled call retains its slot until the worker finishes cleanup.
        await slots.acquire()
        event = threading.Event()
        worker = asyncio.create_task(asyncio.to_thread(gateway.call, params.name, params.arguments, event))
        active[event] = worker

        def finished(task):
            active.pop(event, None)
            slots.release()

        worker.add_done_callback(finished)
        try:
            payload, is_error = await asyncio.shield(worker)
        except asyncio.CancelledError:
            await join_cancelled(event, worker)
            raise
        return CallToolResult(
            content=[TextContent(type="text", text=gateway.serialize(payload))],
            structured_content=payload, is_error=is_error,
        )

    async def list_resources(context, params):
        return ListResourcesResult(resources=[Resource(**item) for item in gateway.resources()])

    async def read_resource(context, params):
        try:
            text, mime = gateway.read_resource(str(params.uri))
        except Exception:
            # The SDK converts this into a generic protocol error. No requested
            # URI, filesystem path or original exception is returned.
            raise ValueError("resource_unavailable") from None
        return ReadResourceResult(contents=[TextResourceContents(uri=str(params.uri), mime_type=mime, text=text)])

    return Server(
        "AirMosaic", version="0.1.0", lifespan=lifespan,
        instructions=("Use repository metadata to select implemented tools and read relevant skill resources. "
                      "Calculation tools default to dry-run. Real execution, network and browser grants "
                      "are selected by the operator at startup, not by call arguments. "
                      "Receipts do not establish scientific validation."),
        on_list_tools=list_tools, on_call_tool=call_tool,
        on_list_resources=list_resources, on_read_resource=read_resource,
    )


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, '{"error":"invalid_mcp_startup_arguments"}\n')


def build_parser():
    parser = _Parser(prog="airmosaic-mcp", description="Local stdio MCP server; preview by default.")
    parser.add_argument("--execute-tool", action="append", default=[], metavar="TOOL_ID",
                        help="Authorize a reviewed tool for real execution; repeat per tool.")
    parser.add_argument("--network-tool", action="append", default=[], metavar="TOOL_ID",
                        help="Authorize network access for a selected execution tool.")
    parser.add_argument("--browser-tool", action="append", default=[], metavar="TOOL_ID",
                        help="Attest the selected execution/network tool's authorized browser session.")
    parser.add_argument("--browser-port", type=int,
                        help="Bind browser tools to an operator-verified local CDP port.")
    parser.add_argument("--max-timeout", type=int, default=300, help="Maximum call timeout, 1–3600 seconds.")
    return parser


async def _serve(gateway):
    import anyio
    from dataclasses import replace
    from mcp.server.stdio import stdio_server
    from mcp.types import ErrorData, JSONRPCError

    server = create_server(gateway)
    async with stdio_server() as (reader, writer):
        class PrivateErrorStream(anyio.abc.ObjectSendStream):
            async def send(self, message):
                if isinstance(message.message, JSONRPCError):
                    code = message.message.error.code
                    messages = {-32700: "Parse error", -32600: "Invalid request",
                                -32601: "Method not found", -32602: "Invalid parameters",
                                -32603: "Internal server error"}
                    error = ErrorData(code=code, message=messages.get(code, "MCP request failed"))
                    message = replace(message, message=message.message.model_copy(update={"error": error}))
                await writer.send(message)

            async def aclose(self):
                await writer.aclose()

        await server.run(reader, PrivateErrorStream(), server.create_initialization_options())


def main():
    args = build_parser().parse_args()
    # Dependency diagnostics must not put request values or SDK tracebacks in
    # protocol stdout or raw logs. The application emits fixed codes on stderr.
    logger = logging.getLogger("mcp")
    logger.handlers[:] = [logging.NullHandler()]
    logger.propagate = False
    try:
        policy = MCPPolicy(execution_tools=frozenset(args.execute_tool), network_tools=frozenset(args.network_tool),
                           browser_tools=frozenset(args.browser_tool), max_timeout=args.max_timeout,
                           browser_port=args.browser_port)
        gateway = MCPGateway(policy=policy)
        asyncio.run(_serve(gateway))
    except ImportError:
        print(json.dumps({"error": "mcp_dependency_unavailable", "next_step": "Install the mcp optional extra."}),
              file=sys.stderr)
        raise SystemExit(2) from None
    except (MCPGatewayError, ToolRegistryError):
        print('{"error":"invalid_mcp_server_configuration"}', file=sys.stderr)
        raise SystemExit(2) from None
    except KeyboardInterrupt:
        raise SystemExit(130) from None
    except Exception:
        print('{"error":"mcp_server_failed"}', file=sys.stderr)
        raise SystemExit(3) from None


if __name__ == "__main__":
    main()
