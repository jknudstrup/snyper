# client.py - Client module for Raspberry Pi Pico W
import network
import urequests
import time
import ujson

class PicoClient:
    def __init__(self, ssid="PicoServer", password="picopass123", 
                 server_ip="192.168.4.1", server_port=80):
        """Initialize the Pico client
        
        Args:
            ssid (str): WiFi network name to connect to
            password (str): WiFi network password
            server_ip (str): Server IP address
            server_port (int): Server port number
        """
        self.ssid = ssid
        self.password = password
        self.server_ip = server_ip
        self.server_port = server_port
        self.wlan = None
        self.connected = False
    
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
    
    def _make_request(self, endpoint, method="GET"):
        """Make HTTP request to server
        
        Args:
            endpoint (str): API endpoint (e.g., "/hello")
            method (str): HTTP method
            
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
    
    def get_server_status(self):
        """Get server status information
        
        Returns:
            dict: Server status data or None if failed
        """
        print("Getting server status...")
        return self._make_request("/status")
    
    def run_basic_test(self):
        """Run a basic client test sequence
        
        Returns:
            bool: True if all tests passed, False otherwise
        """
        print("Starting Pico W Client Test...")
        
        # Connect to WiFi
        if not self.connect_to_wifi():
            print("Cannot proceed without WiFi connection")
            return False
        
        # Wait a bit for everything to settle
        time.sleep(2)
        
        success = True
        
        # Test basic connectivity
        if not self.test_connectivity():
            print("Cannot reach server - check if server is running")
            success = False
        else:
            # Send hello request
            hello_response = self.send_hello_request()
            if not hello_response:
                success = False
            
            # Get server status
            status_response = self.get_server_status()
            if status_response:
                print(f"\nServer status: {status_response.get('status', 'unknown')}")
        
        if success:
            print("\n✓ All client tests completed successfully!")
        else:
            print("\n✗ Some client tests failed")
        
        return success

# Convenience function for simple usage
def create_client(ssid="PicoServer", password="picopass123", 
                  server_ip="192.168.4.1", server_port=80):
    """Create and return a configured PicoClient instance
    
    Args:
        ssid (str): WiFi network name to connect to
        password (str): WiFi network password  
        server_ip (str): Server IP address
        server_port (int): Server port number
    
    Returns:
        PicoClient: Configured client instance
    """
    return PicoClient(ssid, password, server_ip, server_port)

# Default configuration
DEFAULT_CONFIG = {
    'ssid': 'PicoServer',
    'password': 'picopass123',
    'server_ip': '192.168.4.1',
    'server_port': 80
}