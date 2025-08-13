# server.py - Server module for Raspberry Pi Pico W
import network
import time
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
                "available_endpoints": ["/", "/hello"],
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
                "connected_clients": "unknown"  # Pico W doesn't easily expose this
            }
    
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
    
    def start(self, host='0.0.0.0'):
        """Start the server
        
        Args:
            host (str): Host address to bind to
        """
        print(f"Starting Pico W Server...")
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