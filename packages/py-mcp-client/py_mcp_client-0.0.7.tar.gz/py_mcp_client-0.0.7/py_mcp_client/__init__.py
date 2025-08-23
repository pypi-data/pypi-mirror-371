# Pyodide-only MCP client over SSE + POST
# - Opens a maintained SSE stream (GET) to receive JSON-RPC responses/notifications
# - Sends requests/notifications via POST to the advertised message_url
# - Parses tools and supports run_tool()

import asyncio
import json
from urllib.parse import urlparse
from js import AbortController, TextDecoder
from pyodide.http import pyfetch

class MCPClient:
    def __init__(self, sse_url: str, credentials: str | None = None, open_method: str | None = None):
        # credentials: None | "include" | "same-origin"
        # open_method: force "GET" or "POST"; if None, try GET then POST
        self.sse_url = sse_url
        self.credentials = credentials
        self.open_method = open_method

        self.message_url: str | None = None
        self.request_id = 0
        self.pending: dict[int, asyncio.Future] = {}

        self.tools: dict[str, dict] = {}

        self._stream_res = None
        self._reader_task = None
        self._open_fut = None
        self._closed_evt = asyncio.Event()
        self._abort = None  # AbortController
        self._decoder = TextDecoder.new("utf-8")

    async def connect(self):
        self._open_fut = asyncio.get_event_loop().create_future()
        self._abort = AbortController.new()

        methods = [self.open_method] if self.open_method else ["GET", "POST"]
        methods = [m for m in methods if m is not None]

        last_err = None
        for method in methods:
            try:
                kwargs = dict(
                    method=method,
                    headers={"Accept": "text/event-stream"},
                    signal=self._abort.signal,
                    mode="cors",
                    cache="no-store",
                )
                if self.credentials:
                    kwargs["credentials"] = self.credentials

                res = await pyfetch(self.sse_url, **kwargs)
                if not res.ok:
                    if res.status == 405:
                        last_err = f"{method} -> 405 Method Not Allowed"
                        continue
                    res.raise_for_status()

                self._stream_res = res
                reader = res.js_response.body.getReader()
                self._reader_task = asyncio.create_task(self._read_loop(reader))
                await self._open_fut  # wait until message_url discovered
                return
            except Exception as e:
                last_err = f"{method} -> {e}"

        raise RuntimeError(f"Failed to open SSE stream. Tried {methods}. Last error: {last_err}")

    async def _read_loop(self, reader):
        # Minimal SSE parser
        buffer = ""
        event_data_lines = []

        def dispatch_event():
            nonlocal event_data_lines
            if not event_data_lines:
                return
            data_text = "\n".join(event_data_lines)
            event_data_lines = []
            self._handle_event_data(data_text)

        try:
            while True:
                chunk = await reader.read()
                if chunk.done:
                    break
                text = self._decoder.decode(chunk.value, {"stream": True})
                buffer += text

                while True:
                    idx = buffer.find("\n")
                    if idx == -1:
                        break
                    line, buffer = buffer[:idx], buffer[idx + 1:]
                    line = line.rstrip("\r")

                    if line == "":
                        dispatch_event()
                        continue
                    if line.startswith(":"):
                        continue  # comment

                    if ":" in line:
                        field, value = line.split(":", 1)
                        if value.startswith(" "):
                            value = value[1:]
                    else:
                        field, value = line, ""

                    if field == "data":
                        event_data_lines.append(value)

            if event_data_lines:
                dispatch_event()
        except Exception as e:
            for fut in list(self.pending.values()):
                if not fut.done():
                    fut.set_exception(e)
            self.pending.clear()
            raise
        finally:
            self._closed_evt.set()

    def _handle_event_data(self, data_text: str):
        # First event usually carries the message URL (string or JSON with "endpoint"/"url")
        if self.message_url is None:
            # Try JSON first
            target = None
            try:
                obj = json.loads(data_text)
                if isinstance(obj, dict):
                    target = obj.get("endpoint") or obj.get("url")
            except Exception:
                pass

            if not target:
                # Fallback: plain string path/URL
                target = data_text

            if target:
                if target.startswith("http"):
                    self.message_url = target
                elif target.startswith("/"):
                    parsed = urlparse(self.sse_url)
                    base = f"{parsed.scheme}://{parsed.netloc}"
                    self.message_url = base + target
                else:
                    # relative or opaque; use simple base from known pattern
                    base = self.sse_url.rsplit("/sse-mcp/", 1)[0]
                    self.message_url = base + "/" + target.lstrip("/")

            if self.message_url:
                if not self._open_fut.done():
                    self._open_fut.set_result(True)
                return

        # Otherwise, expect JSON-RPC payloads
        try:
            msg = json.loads(data_text)
        except Exception:
            return

        if isinstance(msg, dict) and "id" in msg:
            rid = msg.get("id")
            fut = self.pending.pop(rid, None)
            if fut and not fut.done():
                if "error" in msg and msg["error"] is not None:
                    fut.set_exception(RuntimeError(json.dumps(msg["error"])))
                else:
                    fut.set_result(msg)
            return

        # Notifications can be handled here if needed

    async def send_request(self, method: str, params=None, timeout: float | None = None):
        if not self.message_url:
            raise RuntimeError("Not connected (message_url not discovered yet)")

        self.request_id += 1
        rid = self.request_id
        payload = {"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}}

        fut = asyncio.get_event_loop().create_future()
        self.pending[rid] = fut

        kwargs = dict(
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(payload),
            mode="cors",
            cache="no-store",
        )
        if self.credentials:
            kwargs["credentials"] = self.credentials

        res = await pyfetch(self.message_url, **kwargs)
        if not res.ok:
            self.pending.pop(rid, None)
            raise RuntimeError(f"send_request POST failed: {res.status} {res.status_text}")

        try:
            if timeout is not None:
                return await asyncio.wait_for(fut, timeout=timeout)
            return await fut
        finally:
            self.pending.pop(rid, None)

    async def send_notification(self, method: str, params=None):
        if not self.message_url:
            raise RuntimeError("Not connected (message_url not discovered yet)")

        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params

        kwargs = dict(
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(payload),
            mode="cors",
            cache="no-store",
        )
        if self.credentials:
            kwargs["credentials"] = self.credentials

        res = await pyfetch(self.message_url, **kwargs)
        if not res.ok:
            raise RuntimeError(f"send_notification POST failed: {res.status} {res.status_text}")

    def _parse_tools(self, tools_list):
        """Parse tools into structured format similar to your original client."""
        parsed = {}
        for tool in tools_list or []:
            if not isinstance(tool, dict) or "name" not in tool:
                continue
            name = tool["name"]
            input_schema = tool.get("inputSchema", {}) or {}
            properties = input_schema.get("properties", {}) or {}
            required = input_schema.get("required", []) or []

            params = {}
            for param_name, param_info in properties.items():
                pinfo = param_info or {}
                params[param_name] = {
                    "type": pinfo.get("type", "string"),
                    "required": param_name in required,
                    "default": pinfo.get("default", None),
                    "description": pinfo.get("title", pinfo.get("description", "")) or "",
                    "schema": pinfo,
                }

            parsed[name] = {
                "name": name,
                "description": (tool.get("description", "") or "").split("\n")[0],
                "full_description": tool.get("description", "") or "",
                "parameters": params,
                "output_schema": tool.get("outputSchema", {}) or {},
                "metadata": tool.get("_meta", {}) or {},
                "input_schema": input_schema,
            }
        self.tools = parsed

    async def initialize(self):
        init_resp = await self.send_request("initialize", {
            "protocolVersion": "0.1.0",
            "capabilities": {},
            "clientInfo": {"name": "python-mcp-client", "version": "1.0.0"},
        })
        await self.send_notification("notifications/initialized")

        tools_resp = await self.send_request("tools/list", {})
        tools = (tools_resp.get("result") or {}).get("tools") or []
        self._parse_tools(tools)
        return init_resp, self.tools

    async def run_tool(self, tool_name: str, arguments: dict | None = None, timeout: float | None = None):
        """Validate parameters, call the tool, and return the JSON-RPC response dict."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool = self.tools[tool_name]
        arguments = arguments or {}

        # Validate required parameters
        missing = [
            p for p, info in tool["parameters"].items()
            if info.get("required") and p not in arguments
        ]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")

        # Send request; result arrives on the SSE stream and resolves via id
        resp = await self.send_request("tools/call", {"name": tool_name, "arguments": arguments}, timeout=timeout)
        return resp

    async def close(self):
        if self._abort:
            try:
                self._abort.abort("client closing")
            except Exception:
                pass
        if self._reader_task:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
        for fut in list(self.pending.values()):
            if not fut.done():
                fut.set_exception(RuntimeError("Client closed"))
        self.pending.clear()

# Example usage in Pyodide:
# async def main():
#     client = MCPClient("https://qbo-mcp.briskdata.com/sse-mcp/")
#     await client.connect()
#     init_response, tools = await client.initialize()
#     print("Tools:", list(tools.keys()))
#     # Example: run a tool (replace "tool_name" and args)
#     # result = await client.run_tool("tool_name", {"param1": "value"})
#     # print("tool result:", json.dumps(result, indent=2))
#     await client.close()
# 
# await main()