# server.py - Bidirectional Server module for Raspberry Pi Pico W
import network
import time
import urequests
import ujson
from server.microdot import Microdot

class PicoServer:
    def __init__(self, ssid="PicoServer", password="picopass123", port=80):
        """Initialize the Pico server
        
        Args:
            ssid (str): WiFi access point name
            password (str): WiFi access point password
            port (int): Server port number
        """
        self.ssid = ssid
        self.password = password
        self.port = port
        self.app = Microdot()
        self.ap = None
        
        # Registry of connected clients
        self.clients = {}  # {client_id: {"ip": "192.168.4.2", "port": 8080, "last_seen": timestamp}}
        
        # Set up routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up HTTP routes"""
        
        @self.app.route('/hello')
        def hello_world(request):
            """Handle GET requests to /hello"""
            # Get client IP from request.client_addr tuple (host, port)
            client_ip = request.client_addr[0] if request.client_addr else 'unknown'
            
            response_data = {
                "message": "Hello from Raspberry Pi Pico W!",
                "timestamp": time.time(),
                "client_ip": client_ip
            }
            
            print(f"Hello request received from: {response_data['client_ip']}")
            return response_data

        @self.app.route('/')
        def index(request):
            """Root endpoint for basic connectivity test"""
            return {
                "status": "Server is running", 
                "available_endpoints": ["/", "/hello", "/status", "/clients", "/register", "/send-command"],
                "server_info": {
                    "ssid": self.ssid,
                    "port": self.port
                }
            }
        
        @self.app.route('/status')
        def status(request):
            """Server status endpoint"""
            return {
                "status": "online",
                "uptime": time.time(),
                "access_point": self.ssid,
                "connected_clients": len(self.clients),
                "client_list": list(self.clients.keys())
            }
        
        @self.app.route('/clients')
        def list_clients(request):
            """List all registered clients"""
            return {
                "clients": self.clients,
                "count": len(self.clients)
            }
        
        @self.app.route('/register', methods=['POST'])
        def register_client(request):
            """Register a client with the server"""
            try:
                data = request.json
                if not data:
                    return {"error": "No JSON data provided"}, 400
                
                client_id = data.get('client_id')
                client_port = data.get('port', 8080)
                
                if not client_id:
                    return {"error": "client_id is required"}, 400
                
                # Get client IP from request
                client_ip = request.client_addr[0] if request.client_addr else 'unknown'
                
                # Register the client
                self.clients[client_id] = {
                    "ip": client_ip,
                    "port": client_port,
                    "last_seen": time.time(),
                    "registered_at": time.time()
                }
                
                print(f"Client '{client_id}' registered at {client_ip}:{client_port}")
                
                return {
                    "message": f"Client {client_id} registered successfully",
                    "client_info": self.clients[client_id]
                }
                
            except Exception as e:
                print(f"Registration error: {e}")
                return {"error": "Registration failed"}, 500
        
        @self.app.route('/send-command/<client_id>')
        def send_command_to_client(request, client_id):
            """Send a command to a specific client"""
            if client_id not in self.clients:
                return {"error": f"Client {client_id} not found"}, 404
            
            # Get command from query parameters
            command = request.args.get('cmd', 'print("Hello from server!")')
            
            client_info = self.clients[client_id]
            success, result = self._send_client_request(client_info, "/execute", {
                "command": command,
                "sender": "server"
            })
            
            if success:
                return {
                    "message": f"Command sent to {client_id}",
                    "command": command,
                    "result": result
                }
            else:
                return {
                    "error": f"Failed to send command to {client_id}",
                    "details": result
                }, 500
        
        @self.app.route('/broadcast')
        def broadcast_command(request):
            """Send a command to all registered clients"""
            command = request.args.get('cmd', 'print("Broadcast from server!")')
            
            if not self.clients:
                return {"error": "No clients registered"}, 404
            
            results = {}
            for client_id, client_info in self.clients.items():
                success, result = self._send_client_request(client_info, "/execute", {
                    "command": command,
                    "sender": "server",
                    "broadcast": True
                })
                results[client_id] = {
                    "success": success,
                    "result": result
                }
            
            return {
                "message": "Command broadcast to all clients",
                "command": command,
                "results": results
            }
    
    def _send_client_request(self, client_info, endpoint, data):
        """Send HTTP request to a client
        
        Args:
            client_info (dict): Client info with ip and port
            endpoint (str): Client endpoint to call
            data (dict): Data to send
            
        Returns:
            tuple: (success: bool, result: dict/str)
        """
        url = f"http://{client_info['ip']}:{client_info['port']}{endpoint}"
        
        try:
            print(f"Sending request to client at {url}")
            
            # Send POST request with JSON data
            headers = {'Content-Type': 'application/json'}
            response = urequests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                response.close()
                return True, result
            else:
                error_text = response.text
                response.close()
                return False, f"HTTP {response.status_code}: {error_text}"
                
        except Exception as e:
            return False, f"Request failed: {e}"
    
    def setup_access_point(self):
        """Set up the Pico as a WiFi Access Point
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.ap = network.WLAN(network.AP_IF)
            self.ap.active(True)
            
            # Configure the access point
            self.ap.config(essid=self.ssid, password=self.password)
            
            # Wait for the access point to become active
            timeout = 10
            while not self.ap.active() and timeout > 0:
                time.sleep(0.1)
                timeout -= 1
            
            if not self.ap.active():
                print("Failed to create access point")
                return False
            
            ip_info = self.ap.ifconfig()
            print(f"Access Point '{self.ssid}' created successfully")
            print(f"IP Address: {ip_info[0]}")
            print(f"Subnet Mask: {ip_info[1]}")
            print(f"Gateway: {ip_info[2]}")
            print(f"DNS: {ip_info[3]}")
            print(f"Password: {self.password}")
            return True
            
        except Exception as e:
            print(f"Error setting up access point: {e}")
            return False
    
    def cleanup_stale_clients(self, timeout=300):
        """Remove clients that haven't been seen for a while"""
        current_time = time.time()
        stale_clients = []
        
        for client_id, client_info in self.clients.items():
            if current_time - client_info['last_seen'] > timeout:
                stale_clients.append(client_id)
        
        for client_id in stale_clients:
            print(f"Removing stale client: {client_id}")
            del self.clients[client_id]
    
    def start(self, host='0.0.0.0'):
        """Start the server
        
        Args:
            host (str): Host address to bind to
        """
        print(f"Starting Bidirectional Pico W Server...")
        print(f"SSID: {self.ssid}")
        print(f"Port: {self.port}")
        
        # Set up access point
        if not self.setup_access_point():
            print("Cannot start server without access point")
            return False
        
        # Start the web server
        print(f"Starting web server on {host}:{self.port}...")
        print("Available routes:")
        print("  GET / - Server info")
        print("  GET /hello - Hello world endpoint")
        print("  GET /status - Server status")
        print("  GET /clients - List registered clients")
        print("  POST /register - Register a client")
        print("  GET /send-command/<client_id>?cmd=<command> - Send command to client")
        print("  GET /broadcast?cmd=<command> - Broadcast command to all clients")
        print("Server is ready for connections!")
        
        try:
            self.app.run(host=host, port=self.port, debug=True)
        except KeyboardInterrupt:
            print("\nServer stopped by user")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the server and clean up"""
        if self.ap:
            print("Shutting down access point...")
            self.ap.active(False)
            self.ap = None
        self.clients.clear()
        print("Server stopped")

# Convenience function for simple usage
def create_server(ssid="PicoServer", password="picopass123", port=80):
    """Create and return a configured PicoServer instance
    
    Args:
        ssid (str): WiFi access point name
        password (str): WiFi access point password
        port (int): Server port number
    
    Returns:
        PicoServer: Configured server instance
    """
    return PicoServer(ssid, password, port)

# Default configuration
DEFAULT_CONFIG = {
    'ssid': 'PicoServer',
    'password': 'picopass123',
    'port': 80
}