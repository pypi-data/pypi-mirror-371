import sys
import json
import time
import asyncio
import threading
from urllib.parse import urlparse
import urllib.request

__version__ = "0.0.8"

IS_PYODIDE = (sys.platform == "emscripten")
if IS_PYODIDE:
    from pyodide.http import pyfetch
    from js import AbortController, TextDecoder  # JS APIs

def _cookie_header_from_dict(cookies: dict[str, str] | None) -> str | None:
    if not cookies:
        return None
    return "; ".join(f"{k}={v}" for k, v in cookies.items())

class MCPClient:
    def __init__(
        self,
        sse_url: str,
        *,
        credentials: str | None = None,   # Pyodide only: None | 'include' | 'same-origin'
        open_method: str | None = None,   # Force 'GET' or 'POST' to open SSE; None tries GET then POST
        headers: dict | None = None,      # Extra HTTP headers (desktop + Pyodide)
        cookies: dict[str, str] | None = None,  # Desktop: converted to Cookie header; Pyodide ignored
        connect_timeout: float = 15.0      # Seconds to wait for message_url discovery
    ):
        self.sse_url = sse_url
        self.credentials = credentials
        self.open_method = open_method
        self.extra_headers = headers or {}
        self.cookies = cookies or {}
        self.connect_timeout = connect_timeout

        self.message_url: str | None = None
        self.request_id = 0
        self.pending: dict[int, asyncio.Future] = {}
        self.tools: dict[str, dict] = {}

        # Shared
        self._open_fut: asyncio.Future | None = None

        # Pyodide
        self._stream_res = None
        self._reader_task = None
        if IS_PYODIDE:
            self._abort = None
            self._decoder = TextDecoder.new("utf-8")

        # Desktop
        self._thread = None
        self._stop_evt = threading.Event()
        self._resp_fp = None
        self._loop = None

    async def connect(self):
        self._open_fut = asyncio.get_event_loop().create_future()
        if IS_PYODIDE:
            await self._connect_pyodide()
        else:
            await self._connect_desktop()

        # Don’t hang forever: enforce connect timeout
        try:
            await asyncio.wait_for(self._open_fut, timeout=self.connect_timeout)
        except asyncio.TimeoutError:
            await self.close()
            raise TimeoutError(
                "Timed out waiting for message_url on SSE stream. "
                "If this only happens on desktop, you likely need to pass cookies or auth headers."
            )

    # ---------------- Pyodide path ----------------
    async def _connect_pyodide(self):
        methods = [self.open_method] if self.open_method else ["GET", "POST"]
        methods = [m for m in methods if m is not None]

        last_err = None
        self._abort = AbortController.new()

        for method in methods:
            try:
                headers = {
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    **self.extra_headers,
                }
                kwargs = dict(
                    method=method,
                    headers=headers,
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
                self._reader_task = asyncio.create_task(self._read_loop_pyodide(reader))
                return
            except Exception as e:
                last_err = f"{method} -> {e}"

        raise RuntimeError(f"Failed to open SSE stream. Tried {methods}. Last error: {last_err}")

    async def _read_loop_pyodide(self, reader):
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
                        continue

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
        finally:
            for fut in list(self.pending.values()):
                if not fut.done():
                    fut.set_exception(RuntimeError("SSE stream closed"))
            self.pending.clear()

    # ---------------- Desktop path ----------------
    async def _connect_desktop(self):
        self._loop = asyncio.get_event_loop()
        self._stop_evt.clear()
        self._thread = threading.Thread(target=self._thread_read_sse, daemon=True)
        self._thread.start()

    def _thread_read_sse(self):
        methods = [self.open_method] if self.open_method else ["GET", "POST"]
        methods = [m for m in methods if m is not None]

        def open_with_method(method: str):
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                **self.extra_headers,
            }
            cookie_header = _cookie_header_from_dict(self.cookies)
            if cookie_header:
                headers["Cookie"] = cookie_header

            data = None
            if method == "POST":
                data = b""

            req = urllib.request.Request(
                self.sse_url,
                headers=headers,
                method=method,
                data=data,
            )
            return urllib.request.urlopen(req, timeout=60)

        last_err = None
        for m in methods:
            try:
                self._resp_fp = open_with_method(m)
                break
            except Exception as e:
                last_err = f"{m} -> {e}"
                self._resp_fp = None
        if self._resp_fp is None:
            if self._open_fut and not self._open_fut.done():
                self._loop.call_soon_threadsafe(
                    self._open_fut.set_exception,
                    RuntimeError(f"Failed to open SSE stream (desktop). Tried {methods}. Last error: {last_err}")
                )
            return

        buffer_lines = []
        try:
            while not self._stop_evt.is_set():
                line = self._resp_fp.readline()
                if not line:
                    break
                s = line.decode("utf-8", errors="replace").rstrip("\r\n")

                if s == "":
                    if buffer_lines:
                        data_text = "\n".join(buffer_lines)
                        buffer_lines.clear()
                        self._loop.call_soon_threadsafe(self._handle_event_data, data_text)
                    continue

                if s.startswith(":"):
                    continue

                if ":" in s:
                    field, value = s.split(":", 1)
                    if value.startswith(" "):
                        value = value[1:]
                else:
                    field, value = s, ""

                if field == "data":
                    buffer_lines.append(value)

            if buffer_lines:
                data_text = "\n".join(buffer_lines)
                buffer_lines.clear()
                self._loop.call_soon_threadsafe(self._handle_event_data, data_text)

        finally:
            try:
                if self._resp_fp:
                    self._resp_fp.close()
            except Exception:
                pass
            def fail_all():
                for fut in list(self.pending.values()):
                    if not fut.done():
                        fut.set_exception(RuntimeError("SSE stream closed"))
                self.pending.clear()
            self._loop.call_soon_threadsafe(fail_all)

    # ---------------- Shared: handle events ----------------
    def _handle_event_data(self, data_text: str):
        if self.message_url is None:
            target = None
            try:
                obj = json.loads(data_text)
                if isinstance(obj, dict):
                    target = obj.get("endpoint") or obj.get("url")
            except Exception:
                pass

            if not target:
                target = data_text

            if target:
                if target.startswith("http"):
                    self.message_url = target
                elif target.startswith("/"):
                    parsed = urlparse(self.sse_url)
                    base = f"{parsed.scheme}://{parsed.netloc}"
                    self.message_url = base + target
                else:
                    base = self.sse_url.rsplit("/sse-mcp/", 1)[0]
                    self.message_url = base + "/" + target.lstrip("/")

            if self.message_url:
                if self._open_fut and not self._open_fut.done():
                    self._open_fut.set_result(True)
                return

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
        # Notifications could be handled here

    # ---------------- Requests ----------------
    async def send_request(self, method: str, params=None, timeout: float | None = None):
        if not self.message_url:
            raise RuntimeError("Not connected (message_url not discovered yet)")

        self.request_id += 1
        rid = self.request_id
        payload = {"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}}

        fut = asyncio.get_event_loop().create_future()
        self.pending[rid] = fut

        try:
            if IS_PYODIDE:
                headers = {"Content-Type": "application/json", **self.extra_headers}
                kwargs = dict(
                    method="POST",
                    headers=headers,
                    body=json.dumps(payload),
                    mode="cors",
                    cache="no-store",
                )
                if self.credentials:
                    kwargs["credentials"] = self.credentials
                res = await pyfetch(self.message_url, **kwargs)
                if not res.ok:
                    raise RuntimeError(f"send_request POST failed: {res.status} {res.status_text}")
            else:
                await asyncio.to_thread(self._post_desktop, self.message_url, payload)

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

        if IS_PYODIDE:
            headers = {"Content-Type": "application/json", **self.extra_headers}
            kwargs = dict(
                method="POST",
                headers=headers,
                body=json.dumps(payload),
                mode="cors",
                cache="no-store",
            )
            if self.credentials:
                kwargs["credentials"] = self.credentials
            res = await pyfetch(self.message_url, **kwargs)
            if not res.ok:
                raise RuntimeError(f"send_notification POST failed: {res.status} {res.status_text}")
        else:
            await asyncio.to_thread(self._post_desktop, self.message_url, payload)

    def _post_desktop(self, url: str, json_body: dict):
        data = json.dumps(json_body).encode("utf-8")
        headers = {"Content-Type": "application/json", **self.extra_headers}
        cookie_header = _cookie_header_from_dict(self.cookies)
        if cookie_header:
            headers["Cookie"] = cookie_header
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60):
            pass

    # ---------------- High-level API ----------------
    def _parse_tools(self, tools_list):
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
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        tool = self.tools[tool_name]
        arguments = arguments or {}
        missing = [p for p, info in tool["parameters"].items() if info.get("required") and p not in arguments]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
        resp = await self.send_request("tools/call", {"name": tool_name, "arguments": arguments}, timeout=timeout)
        return resp

    async def close(self):
        if IS_PYODIDE:
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
        else:
            self._stop_evt.set()
            try:
                if self._resp_fp:
                    self._resp_fp.close()
            except Exception:
                pass
            if self._thread:
                self._thread.join(timeout=1.5)

        for fut in list(self.pending.values()):
            if not fut.done():
                fut.set_exception(RuntimeError("Client closed"))
        self.pending.clear()