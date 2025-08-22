import json
import sys
import queue
import threading

# Conditional imports
if sys.platform == 'emscripten':
    import asyncio
    from pyodide.http import pyfetch
    from js import EventSource, JSON, console
else:
    import urllib.request
    from urllib.parse import urlparse

class MCPClient:
    def __init__(self, sse_url):
        self.sse_url = sse_url
        self.request_id = 0
        self.message_url = None
        self.tools = {}
        
        self.is_pyodide = sys.platform == 'emscripten'
        
        if self.is_pyodide:
            self.event_source = None
            self.pending_responses = {}
            self.connect_future = asyncio.Future()
            self._start_sse_pyodide()  # Kick off SSE in init
        else:
            self.sse_response = None
            self.response_queue = queue.Queue()
            self.reader_thread = None
            self.running = False
    
    def _start_sse_pyodide(self):
        """Kick off SSE connection in background"""
        async def setup():
            self.event_source = EventSource.new(self.sse_url)
            
            def handle_event(event_type, event):
                data = event.data
                print(f"Received event: {event_type}, Data: {data}")
                
                if not self.connect_future.done():
                    # Parse for message URL
                    if data.startswith('/sse-mcp/messages/'):
                        parts = self.sse_url.split('/sse-mcp/')
                        base = parts[0]
                        self.message_url = base + data
                        print(f"Message URL: {self.message_url}")
                        self.connect_future.set_result(True)
                else:
                    # Handle responses
                    try:
                        parsed = JSON.parse(data)
                        msg_id = parsed.id if hasattr(parsed, 'id') else None
                        if msg_id in self.pending_responses:
                            self.pending_responses[msg_id].set_result(parsed)
                    except:
                        pass
            
            self.event_source.onmessage = lambda event: handle_event('message', event)
            self.event_source.addEventListener('endpoint', lambda event: handle_event('endpoint', event))
            self.event_source.addEventListener('message', lambda event: handle_event('message', event))
            
            def on_error(event):
                console.error("SSE Error:", event)
                if not self.connect_future.done():
                    self.connect_future.set_exception(Exception("SSE connection error"))
            
            self.event_source.onerror = on_error
        
        asyncio.create_task(setup())
    
    def connect(self):
        """Connect to MCP SSE endpoint (sync call)"""
        print(f"Connecting to {self.sse_url}...")
        
        if self.is_pyodide:
            # Wait for the background task to complete connect
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait_for(self.connect_future, timeout=10))
        else:
            self._connect_cpython()
    
    # CPython connect
    def _connect_cpython(self):
        self.sse_response = urllib.request.urlopen(self.sse_url)
        self.running = True
        self.reader_thread = threading.Thread(target=self._read_sse_cpython)
        self.reader_thread.start()
        
        # Wait for message URL
        while not self.message_url:
            try:
                event_type, data = self.response_queue.get(timeout=10)
                if event_type == 'endpoint':
                    if data.startswith('/'):
                        parsed = urlparse(self.sse_url)
                        base = f"{parsed.scheme}://{parsed.netloc}"
                        self.message_url = base + data
                    else:
                        self.message_url = data
                    print(f"Message URL: {self.message_url}")
            except queue.Empty:
                raise Exception("Timeout waiting for message URL")
    
    def _read_sse_cpython(self):
        event_type = 'message'
        data_lines = []
        
        for line in iter(self.sse_response.readline, b''):
            if not self.running:
                break
            line = line.decode('utf-8').strip()
            if not line:
                if data_lines:
                    data = '\n'.join(data_lines)
                    self.response_queue.put((event_type, data))
                    data_lines = []
                event_type = 'message'
                continue
            if line.startswith('event: '):
                event_type = line[7:]
            elif line.startswith('data: '):
                data_lines.append(line[6:])
            # Ignore pings and other
    
    def send_request(self, method, params=None):
        self.request_id += 1
        
        msg = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.request_id,
            "params": params or {}
        }
        
        if self.is_pyodide:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._send_request_pyodide(msg))
        else:
            return self._send_request_cpython(msg)
    
    def _send_request_cpython(self, msg):
        req = urllib.request.Request(
            self.message_url,
            data=json.dumps(msg).encode(),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req)
        
        while True:
            event_type, data = self.response_queue.get()
            try:
                parsed = json.loads(data)
                if parsed.get('id') == msg['id']:
                    return parsed
            except json.JSONDecodeError:
                pass
    
    async def _send_request_pyodide(self, msg):
        response_future = asyncio.Future()
        self.pending_responses[msg['id']] = response_future
        
        await pyfetch(
            self.message_url,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(msg)
        )
        
        result_js = await asyncio.wait_for(response_future, timeout=60)
        del self.pending_responses[msg['id']]
        return json.loads(JSON.stringify(result_js))
    
    def send_notification(self, method, params=None):
        msg = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params is not None:
            msg["params"] = params
        
        if self.is_pyodide:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._send_notification_pyodide(msg))
        else:
            req = urllib.request.Request(
                self.message_url,
                data=json.dumps(msg).encode(),
                headers={"Content-Type": "application/json"}
            )
            urllib.request.urlopen(req)
    
    async def _send_notification_pyodide(self, msg):
        await pyfetch(
            self.message_url,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(msg)
        )
    
    def initialize(self):
        init_response = self.send_request("initialize", {
            "protocolVersion": "0.1.0",
            "capabilities": {},
            "clientInfo": {
                "name": "python-mcp-client",
                "version": "1.0.0"
            }
        })
        
        self.send_notification("notifications/initialized")
        
        tools_response = self.send_request("tools/list", {})
        
        if 'result' in tools_response and 'tools' in tools_response['result']:
            self._parse_tools(tools_response['result']['tools'])
        
        return init_response, self.tools
    
    def _parse_tools(self, tools_list):
        for tool in tools_list:
            name = tool['name']
            input_schema = tool.get('inputSchema', {})
            properties = input_schema.get('properties', {})
            required = input_schema.get('required', [])
            
            params = {}
            for param_name, param_info in properties.items():
                params[param_name] = {
                    'type': param_info.get('type', 'string'),
                    'required': param_name in required,
                    'default': param_info.get('default', None),
                    'description': param_info.get('title', param_info.get('description', '')),
                    'schema': param_info
                }
            
            self.tools[name] = {
                'name': name,
                'description': tool.get('description', '').split('\n')[0],
                'full_description': tool.get('description', ''),
                'parameters': params,
                'output_schema': tool.get('outputSchema', {}),
                'metadata': tool.get('_meta', {}),
                'input_schema': input_schema
            }
    
    def run_tool(self, tool_name, arguments=None):
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool = self.tools[tool_name]
        missing = [p for p, info in tool['parameters'].items() if info['required'] and (not arguments or p not in arguments)]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
        
        return self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments or {}
        })
    
    def close(self):
        if self.is_pyodide:
            if self.event_source:
                self.event_source.close()
        else:
            self.running = False
            if self.reader_thread:
                self.reader_thread.join()
            if self.sse_response:
                self.sse_response.close()

# Example usage
def main():
    client = MCPClient("https://qbo-mcp-api.synclogicsoftware.com/sse-mcp/")
    client.connect()
    init_response, tools = client.initialize()
    print(f"Found {len(tools)} tools")
    client.close()

if __name__ == "__main__":
    main()
