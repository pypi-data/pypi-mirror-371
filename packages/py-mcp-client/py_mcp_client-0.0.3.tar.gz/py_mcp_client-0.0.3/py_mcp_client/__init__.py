import json
import sys

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
        self.pending_responses = {}
        
        self.is_pyodide = sys.platform == 'emscripten'
        
        if self.is_pyodide:
            self.event_source = None
        else:
            self.sse_response = None
    
    def connect(self):
        """Connect to MCP SSE endpoint (sync call)"""
        print(f"Connecting to {self.sse_url}...")
        
        if self.is_pyodide:
            # Run async connect synchronously in Pyodide
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._connect_pyodide())
        else:
            self._connect_cpython()
    
    # CPython (sync) connect
    def _connect_cpython(self):
        self.sse_response = urllib.request.urlopen(self.sse_url)
        
        for line in self.sse_response:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                path = line[6:]
                try:
                    data = json.loads(path)
                    self.message_url = data.get('endpoint') or data.get('url')
                except json.JSONDecodeError:
                    if path.startswith('http'):
                        self.message_url = path
                    elif path.startswith('/'):
                        parsed = urlparse(self.sse_url)
                        base = f"{parsed.scheme}://{parsed.netloc}"
                        self.message_url = base + path
                    else:
                        self.message_url = path
                
                if self.message_url:
                    print(f"Message URL: {self.message_url}")
                    break
        
        if not self.message_url:
            raise Exception("Could not get message URL")
    
    # Pyodide (async) connect
    async def _connect_pyodide(self):
        self.event_source = EventSource.new(self.sse_url)
        
        message_url_future = asyncio.Future()
        
        def on_message(event):
            data = event.data
            if not self.message_url:
                try:
                    parsed = JSON.parse(data)
                    self.message_url = parsed.endpoint if hasattr(parsed, 'endpoint') else (parsed.url if hasattr(parsed, 'url') else None)
                except:
                    if data.startswith('http'):
                        self.message_url = data
                    elif data.startswith('/'):
                        parts = self.sse_url.split('/')
                        base = '/'.join(parts[:3])
                        self.message_url = base + data
                    else:
                        self.message_url = data
                
                if self.message_url:
                    print(f"Message URL: {self.message_url}")
                    message_url_future.set_result(self.message_url)
            else:
                try:
                    parsed = JSON.parse(data)
                    msg_id = parsed.id if hasattr(parsed, 'id') else None
                    if msg_id in self.pending_responses:
                        self.pending_responses[msg_id].set_result(parsed)
                except:
                    pass
        
        def on_error(event):
            console.error("SSE Error:", event)
            if not message_url_future.done():
                message_url_future.set_exception(Exception("SSE connection error"))
        
        self.event_source.onmessage = on_message
        self.event_source.onerror = on_error
        
        await message_url_future
    
    def send_request(self, method, params=None):
        """Send request with ID (sync call)"""
        self.request_id += 1
        
        msg = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.request_id,
            "params": params or {}
        }
        
        if self.is_pyodide:
            # Run async send synchronously
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._send_request_pyodide(msg))
        else:
            return self._send_request_cpython(msg)
    
    # CPython (sync) send
    def _send_request_cpython(self, msg):
        req = urllib.request.Request(
            self.message_url,
            data=json.dumps(msg).encode(),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req)
        
        # Read response from SSE
        for line in self.sse_response:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if data.get('id') == msg['id']:
                        return data
                except:
                    pass
        raise Exception("No response received")
    
    # Pyodide (async) send
    async def _send_request_pyodide(self, msg):
        response_future = asyncio.Future()
        self.pending_responses[msg['id']] = response_future
        
        await pyfetch(
            self.message_url,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(msg)
        )
        
        result_js = await response_future
        del self.pending_responses[msg['id']]
        
        return json.loads(JSON.stringify(result_js))
    
    def send_notification(self, method, params=None):
        """Send notification without ID (sync call)"""
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
        """Initialize MCP connection and get tools (sync call)"""
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
        # Same as before
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
        """Run a tool and return the result (sync call)"""
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
        """Close the connection"""
        if self.is_pyodide:
            if self.event_source:
                self.event_source.close()
        else:
            if self.sse_response:
                self.sse_response.close()

# Example usage (sync in both)
def main():
    client = MCPClient("https://qbo-mcp-api.synclogicsoftware.com/sse-mcp/")
    client.connect()
    init_response, tools = client.initialize()
    print(f"Found {len(tools)} tools")
    client.close()

if __name__ == "__main__":
    main()