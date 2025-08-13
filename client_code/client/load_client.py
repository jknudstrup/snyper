# client.py - Bidirectional Client module for Raspberry Pi Pico W
import network
import urequests
import time
import ujson
import _thread
from client.microdot import Microdot

class PicoClient:
    def __init__(self, client_id="pico_client", ssid="PicoServer", password="picopass123", 
                 server_ip="192.168.4.1", server_port=80, client_port=8080):
        """Initialize the Pico client
        
        Args:
            client_id (str): Unique identifier for this client
            ssid (str): WiFi network name to connect to
            password (str): WiFi network password
            server_ip (str): Server IP address
            server_port (int): Server port number
            client_port (int): Port for this client's mini-server
        """
        self.client_id = client_id
        self.ssid = ssid
        self.password = password
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_port = client_port
        self.wlan = None
        self.connected = False
        self.registered = False
        
        # Mini-server for receiving commands
        self.app = Microdot()
        self.server_thread = None
        self.server_running = False
        
        # Set up client routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up routes for the client's mini-server"""
        
        @self.app.route('/')
        def client_info(request):
            """Client info endpoint"""
            return {
                "client_id": self.client_id,
                "status": "online",
                "server_connected": self.connected,
                "registered": self.registered,
                "available_endpoints": ["/", "/execute", "/ping"]
            }
        
        @self.app.route('/execute', methods=['POST'])
        def execute_command(request):
            """Execute a command sent from the server"""
            try:
                data = request.json
                if not data:
                    return {"error": "No JSON data provided"}, 400
                
                command = data.get('command')
                sender = data.get('sender', 'unknown')
                
                if not command:
                    return {"error": "No command provided"}, 400
                
                print(f"\n>>> Received command from {sender}: {command}")
                
                # Execute the command safely
                result = self._safe_execute(command)
                
                response = {
                    "client_id": self.client_id,
                    "command": command,
                    "executed": True,
                    "result": result,
                    "timestamp": time.time()
                }
                
                print(f">>> Command executed successfully")
                return response
                
            except Exception as e:
                print(f"Command execution error: {e}")
                return {
                    "client_id": self.client_id,
                    "executed": False,
                    "error": str(e)
                }, 500
        
        @self.app.route('/ping')
        def ping(request):
            """Simple ping endpoint"""
            return {
                "client_id": self.client_id,
                "message": "pong",
                "timestamp": time.time()
            }
    
    def _safe_execute(self, command):
        """Safely execute a Python command
        
        Args:
            command (str): Python command to execute
            
        Returns:
            str: Result of execution or error message
        """
        try:
            # For safety, we'll restrict to simple print statements and basic operations
            if command.startswith('print('):
                # Execute print statements directly
                exec(command)
                return "Print command executed"
            elif '=' in command and not any(danger in command for danger in ['import', 'exec', 'eval', '__']):
                # Allow simple variable assignments
                exec(command)
                return "Assignment executed"
            else:
                # For other commands, just show what would be executed
                return f"Command received (not executed for safety): {command}"
        except Exception as e:
            return f"Execution error: {e}"
    
    def connect_to_wifi(self, timeout=10):
        """Connect to the server's WiFi access point
        
        Args:
            timeout (int): Connection timeout in seconds
            
        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            
            print(f"Connecting to WiFi network: {self.ssid}")
            self.wlan.connect(self.ssid, self.password)
            
            # Wait for connection
            max_wait = timeout
            while max_wait > 0:
                status = self.wlan.status()
                if status < 0 or status >= 3:
                    break
                max_wait -= 1
                print("Waiting for connection...")
                time.sleep(1)
            
            # Check connection status
            if self.wlan.status() != 3:
                print(f"Failed to connect to WiFi. Status: {self.wlan.status()}")
                self._print_status_meaning(self.wlan.status())
                self.connected = False
                return False
            else:
                status = self.wlan.ifconfig()
                print(f"✓ Connected to {self.ssid}")
                print(f"Client IP: {status[0]}")
                print(f"Subnet Mask: {status[1]}")
                print(f"Gateway IP: {status[2]}")
                print(f"DNS Server: {status[3]}")
                self.connected = True
                return True
                
        except Exception as e:
            print(f"WiFi connection error: {e}")
            self.connected = False
            return False
    
    def _print_status_meaning(self, status):
        """Print human-readable WiFi status"""
        status_meanings = {
            -3: "Connection failed (no AP found)",
            -2: "Connection failed (wrong password)",
            -1: "Connection failed (other error)",
            0: "Link down",
            1: "Link join",
            2: "Link no IP",
            3: "Link up"
        }
        meaning = status_meanings.get(status, "Unknown status")
        print(f"Status code {status}: {meaning}")
    
    def disconnect(self):
        """Disconnect from WiFi"""
        if self.wlan:
            self.wlan.disconnect()
            self.wlan.active(False)
            self.connected = False
            print("Disconnected from WiFi")
    
    def _make_request(self, endpoint, method="GET", data=None):
        """Make HTTP request to server
        
        Args:
            endpoint (str): API endpoint (e.g., "/hello")
            method (str): HTTP method
            data (dict): Data for POST requests
            
        Returns:
            dict: Response data or None if failed
        """
        if not self.connected:
            print("Not connected to WiFi")
            return None
        
        url = f"http://{self.server_ip}:{self.server_port}{endpoint}"
        
        try:
            print(f"Sending {method} request to: {url}")
            
            if method.upper() == "GET":
                response = urequests.get(url)
            elif method.upper() == "POST":
                headers = {'Content-Type': 'application/json'}
                response = urequests.post(url, json=data, headers=headers)
            else:
                print(f"HTTP method {method} not implemented")
                return None
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    response.close()
                    return data
                except:
                    # If JSON parsing fails, return raw text
                    text = response.text
                    response.close()
                    return {"raw_response": text}
            else:
                error_text = response.text
                response.close()
                print(f"Error: Received status code {response.status_code}")
                print(f"Response: {error_text}")
                return None
            
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def register_with_server(self):
        """Register this client with the server
        
        Returns:
            bool: True if registration successful, False otherwise
        """
        registration_data = {
            "client_id": self.client_id,
            "port": self.client_port
        }
        
        result = self._make_request("/register", "POST", registration_data)
        
        if result and "message" in result:
            print(f"✓ Successfully registered with server: {result['message']}")
            self.registered = True
            return True
        else:
            print("✗ Failed to register with server")
            self.registered = False
            return False
    
    def start_mini_server(self):
        """Start the client's mini-server in a separate thread"""
        def server_thread():
            try:
                print(f"Starting client mini-server on port {self.client_port}...")
                self.server_running = True
                self.app.run(host='0.0.0.0', port=self.client_port, debug=False)
            except Exception as e:
                print(f"Mini-server error: {e}")
            finally:
                self.server_running = False
        
        try:
            self.server_thread = _thread.start_new_thread(server_thread, ())
            time.sleep(1)  # Give the server time to start
            print(f"✓ Mini-server started on port {self.client_port}")
            return True
        except Exception as e:
            print(f"Failed to start mini-server: {e}")
            return False
    
    def test_connectivity(self):
        """Test basic connectivity to server
        
        Returns:
            bool: True if server is reachable, False otherwise
        """
        print("Testing basic connectivity...")
        data = self._make_request("/")
        
        if data:
            print("✓ Basic connectivity test passed")
            if isinstance(data, dict):
                print(f"Server status: {data.get('status', 'Unknown')}")
                endpoints = data.get('available_endpoints', [])
                if endpoints:
                    print(f"Available endpoints: {endpoints}")
            return True
        else:
            print("✗ Connectivity test failed")
            return False
    
    def send_hello_request(self):
        """Send GET request to server's /hello endpoint
        
        Returns:
            dict: Response data or None if failed
        """
        print("\n" + "="*40)
        print("Sending hello request...")
        
        data = self._make_request("/hello")
        
        if data:
            print("Response from server:")
            if isinstance(data, dict):
                print(f"  Message: {data.get('message', 'No message')}")
                print(f"  Timestamp: {data.get('timestamp', 'No timestamp')}")
                print(f"  Client IP: {data.get('client_ip', 'Unknown')}")
            else:
                print(f"  Raw response: {data}")
            return data
        else:
            print("✗ Hello request failed")
            return None
    
    def run_full_setup(self):
        """Run the complete client setup process
        
        Returns:
            bool: True if all setup steps successful, False otherwise
        """
        print(f"Starting Bidirectional Pico W Client: {self.client_id}")
        print("="*50)
        
        # Step 1: Connect to WiFi
        if not self.connect_to_wifi():
            print("Cannot proceed without WiFi connection")
            return False
        
        time.sleep(2)
        
        # Step 2: Start mini-server
        if not self.start_mini_server():
            print("Cannot proceed without mini-server")
            return False
        
        time.sleep(2)
        
        # Step 3: Test connectivity to main server
        if not self.test_connectivity():
            print("Cannot reach main server")
            return False
        
        # Step 4: Register with main server
        if not self.register_with_server():
            print("Failed to register with server")
            return False
        
        # Step 5: Send hello request
        self.send_hello_request()
        
        print(f"\n✓ Client {self.client_id} is fully operational!")
        print(f"✓ Mini-server running on port {self.client_port}")
        print(f"✓ Registered with main server")
        print(f"✓ Ready to receive commands from server")
        
        return True

# Convenience function for simple usage
def create_client(client_id="pico_client", ssid="PicoServer", password="picopass123", 
                  server_ip="192.168.4.1", server_port=80, client_port=8080):
    """Create and return a configured PicoClient instance
    
    Args:
        client_id (str): Unique identifier for this client
        ssid (str): WiFi network name to connect to
        password (str): WiFi network password  
        server_ip (str): Server IP address
        server_port (int): Server port number
        client_port (int): Port for client's mini-server
    
    Returns:
        PicoClient: Configured client instance
    """
    return PicoClient(client_id, ssid, password, server_ip, server_port, client_port)

# Default configuration
DEFAULT_CONFIG = {
    'ssid': 'PicoServer',
    'password': 'picopass123',
    'server_ip': '192.168.4.1',
    'server_port': 80,
    'client_port': 8080
}