import json
import urllib.request

class MCPClient:
    def __init__(self, sse_url):
        self.sse_url = sse_url
        self.request_id = 0
        self.message_url = None
        self.sse_response = None
        self.tools = {}
        
    def connect(self):
        """Connect to MCP SSE endpoint"""
        print(f"Connecting to {self.sse_url}...")
        self.sse_response = urllib.request.urlopen(self.sse_url)
        
        # Read session/message URL
        for line in self.sse_response:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                path = line[6:]
                # Handle both JSON and plain string responses
                try:
                    data = json.loads(path)
                    if 'endpoint' in data:
                        self.message_url = data['endpoint']
                    elif 'url' in data:
                        self.message_url = data['url']
                except:
                    # Plain string path - construct full URL
                    if path.startswith('http'):
                        self.message_url = path
                    elif path.startswith('/'):
                        # Extract base URL from SSE URL
                        from urllib.parse import urlparse
                        parsed = urlparse(self.sse_url)
                        base = f"{parsed.scheme}://{parsed.netloc}"
                        self.message_url = base + path
                    else:
                        self.message_url = path
                
                if self.message_url:
                    print(f"Message URL: {self.message_url}")
                    break
                
        if not self.message_url:
            raise Exception("Could not get message URL from SSE stream")
    
    def send_request(self, method, params=None):
        """Send request with ID"""
        self.request_id += 1
        
        msg = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.request_id,
            "params": params or {}
        }
        
        req = urllib.request.Request(
            self.message_url,
            data=json.dumps(msg).encode(),
            headers={"Content-Type": "application/json"}
        )
        
        urllib.request.urlopen(req)
        return self.request_id
    
    def send_notification(self, method, params=None):
        """Send notification without ID"""
        msg = {
            "jsonrpc": "2.0",
            "method": method
        }
        
        if params is not None:
            msg["params"] = params
        
        req = urllib.request.Request(
            self.message_url,
            data=json.dumps(msg).encode(),
            headers={"Content-Type": "application/json"}
        )
        
        urllib.request.urlopen(req)
    
    def initialize(self):
        """Initialize MCP connection and get tools"""
        # Initialize
        init_id = self.send_request("initialize", {
            "protocolVersion": "0.1.0",
            "capabilities": {},
            "clientInfo": {
                "name": "python-mcp-client",
                "version": "1.0.0"
            }
        })
        
        # Send initialized notification
        self.send_notification("notifications/initialized")
        
        # List tools
        tools_id = self.send_request("tools/list", {})
        
        # Process responses
        responses = {}
        for line in self.sse_response:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if 'id' in data:
                        responses[data['id']] = data
                        
                        # Process tools response
                        if data['id'] == tools_id and 'result' in data and 'tools' in data['result']:
                            self._parse_tools(data['result']['tools'])
                            break
                except:
                    pass
        
        return responses.get(init_id), self.tools
    
    def _parse_tools(self, tools_list):
        """Parse tools into structured format"""
        for tool in tools_list:
            name = tool['name']
            
            # Parse input schema
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
        """Run a tool and return the result"""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Validate required parameters
        tool = self.tools[tool_name]
        missing = []
        for param_name, param_info in tool['parameters'].items():
            if param_info['required'] and (not arguments or param_name not in arguments):
                missing.append(param_name)
        
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
        
        # Send tool call
        call_id = self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments or {}
        })
        
        print(f"\nCalling tool '{tool_name}' with ID {call_id}...")
        
        # Wait for response
        for line in self.sse_response:
            line = line.decode('utf-8').strip()
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if data.get('id') == call_id:
                        if 'error' in data:
                            print(f"Error: {data['error']}")
                        elif 'result' in data:
                            print(f"Success!")
                        return json.loads(data)
                except:
                    pass
    
    def interactive_run(self):
        """Interactive tool runner"""
        while True:
            print("\n" + "="*60)
            print("AVAILABLE TOOLS:")
            print("="*60)
            
            tool_names = list(self.tools.keys())
            for i, name in enumerate(tool_names, 1):
                print(f"{i}. {name} - {self.tools[name]['description']}")
            
            print("\n0. Exit")
            
            try:
                choice = input("\nSelect tool number: ").strip()
                if choice == '0':
                    break
                    
                idx = int(choice) - 1
                if 0 <= idx < len(tool_names):
                    tool_name = tool_names[idx]
                    tool = self.tools[tool_name]
                    
                    print(f"\n--- {tool_name} ---")
                    print(f"Description: {tool['description']}")
                    
                    # Collect arguments
                    arguments = {}
                    
                    # Required parameters first
                    for param_name, param_info in tool['parameters'].items():
                        if param_info['required']:
                            value = input(f"\n{param_name} ({param_info['type']}) [REQUIRED]: ").strip()
                            if param_info['type'] in ['integer', 'number']:
                                try:
                                    arguments[param_name] = int(value) if param_info['type'] == 'integer' else float(value)
                                except:
                                    print(f"Invalid {param_info['type']}, using string")
                                    arguments[param_name] = value
                            elif param_info['type'] == 'object':
                                try:
                                    arguments[param_name] = json.loads(value)
                                except:
                                    print("Invalid JSON, using string")
                                    arguments[param_name] = value
                            else:
                                arguments[param_name] = value
                    
                    # Optional parameters
                    for param_name, param_info in tool['parameters'].items():
                        if not param_info['required']:
                            default = param_info.get('default', '')
                            value = input(f"\n{param_name} ({param_info['type']}) [optional, default: {default}]: ").strip()
                            if value:
                                if param_info['type'] in ['integer', 'number']:
                                    try:
                                        arguments[param_name] = int(value) if param_info['type'] == 'integer' else float(value)
                                    except:
                                        arguments[param_name] = value
                                elif param_info['type'] == 'object':
                                    try:
                                        arguments[param_name] = json.loads(value)
                                    except:
                                        arguments[param_name] = value
                                else:
                                    arguments[param_name] = value
                    
                    # Run tool
                    print(f"\nRunning {tool_name}...")
                    result = self.run_tool(tool_name, arguments)
                    
                    print("\n--- RESULT ---")
                    print(json.dumps(result, indent=2))
                    
                    if 'result' in result:
                        print("\n--- PARSED RESULT ---")
                        print(json.dumps(result['result'], indent=2))
                    
            except ValueError as e:
                print(f"\nError: {e}")
            except KeyboardInterrupt:
                print("\nCancelled")
                continue


# Example usage
if __name__ == "__main__":
    import sys
    
    # Get full SSE URL
    sse_url = sys.argv[1] if len(sys.argv) > 1 else input("Enter full SSE URL: ")
    
    # Create client
    client = MCPClient(sse_url)
    
    try:
        # Connect and initialize
        client.connect()
        
        print("\nInitializing...")
        init_response, tools = client.initialize()
        
        # Print server info
        if init_response and 'result' in init_response:
            server_info = init_response['result'].get('serverInfo', {})
            print(f"\nConnected to: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
            print(f"Found {len(tools)} tools")
        
        # Interactive mode
        client.interactive_run()
        
    except Exception as e:
        print(f"Error: {e}")
