from microdot import Microdot, Response
import json
from config.config import config
from helpers import initialize_access_point

class MasterServer:
    """Master server class to handle HTTP requests - let me tell you something, this is gonna be AWESOME!"""
    
    def __init__(self, on_target_register=None):
        self.app = Microdot()
        self._ap = None
        
        # Load config values into server
        self.ssid = config.ssid
        self.password = config.password  
        self.server_ip = config.server_ip
        self.port = config.port
        
        # Callback functions for communicating with controller
        self.on_target_register = on_target_register
        
        self._setup_routes()
    
    async def start_ap(self):
        """Create WiFi Access Point with clean network state"""
        print(f"🌐 Creating WiFi AP: {self.ssid}")
        
        # Use our new helper function with reset
        self._ap = await initialize_access_point(self.ssid, self.password, reset=False)
        return self._ap
    
    def _setup_routes(self):
        """Set up all the routes - building our wrestling federation!"""
        
        @self.app.route('/')
        async def index(request):
            """Root endpoint - let the clients know we're ready to rumble!"""
            response_data = {"status": "ready", "game": "carnival_shooter"}
            return Response(json.dumps(response_data))

        @self.app.route('/register', methods=['POST'])
        async def register_client(request):
            """Register a new target client - NOW WITH IP TRACKING!"""
            print(f"📡 RECEIVED REGISTRATION REQUEST from {request.client_addr}")
            
            client_data = request.json
            client_id = client_data.get('client_id', 'unknown')
            client_ip = request.client_addr[0]  # GRAB THAT IP!
            
            print(f"🎯 Processing registration: {client_id} at {client_ip}")
            
            # Call controller through callback
            if self.on_target_register:
                self.on_target_register(client_id, client_ip)
                print(f"✅ Registration callback completed for {client_id}")
            else:
                print(f"🤝 Target {client_id} at {client_ip} wants to register (no callback registered)")
            
            response_data = {"status": "registered", "client_id": client_id}
            return Response(json.dumps(response_data))


    async def start_server(self, debug=True):
        """Start the master server - this is where the magic happens, dude!"""
        # WiFi AP is already set up by controller, just start HTTP server
        print(f"🌐 Master server starting on {self.server_ip}:{self.port} - whatcha gonna do!")
        try:
            print(f"🚀 About to start HTTP server on {self.server_ip}:{self.port}")
            await self.app.start_server(host=self.server_ip, port=self.port, debug=debug)
            print(f"✅ HTTP server started successfully!")
        except KeyboardInterrupt:
            print("🛑 Master server received shutdown signal!")
            raise  # Re-raise so main() can handle it
        except Exception as e:
            print(f"💥 Master server error: {e}")
            raise