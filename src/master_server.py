from microdot import Microdot, Response
import json
import network
import time
import asyncio
from config import config
from helpers import initialize_access_point

class MasterServer:
    """Master server class to handle HTTP requests - let me tell you something, this is gonna be AWESOME!"""
    
    def __init__(self):
        self.app = Microdot()
        self._ap = None
        
        # Load config values into server
        self.ssid = config.ssid
        self.password = config.password  
        self.server_ip = config.server_ip
        self.port = config.port
        
        self._setup_routes()
    
    async def start_ap(self):
        """Create WiFi Access Point with clean network state"""
        print(f"🌐 Creating WiFi AP: {self.ssid}")
        
        # Use our new helper function with reset
        self._ap = await initialize_access_point(self.ssid, self.password, reset=True)
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
            client_data = request.json
            client_id = client_data.get('client_id', 'unknown')
            client_ip = request.client_addr[0]  # GRAB THAT IP!
            
            # TODO: Implement communication pattern to controller
            # self.controller.register_target(client_id, client_ip)
            print(f"🤝 Target {client_id} at {client_ip} wants to register (communication pattern TBD)")
            
            response_data = {"status": "registered", "client_id": client_id}
            return Response(json.dumps(response_data))

        @self.app.route('/target_hit', methods=['POST'])
        async def target_hit(request):
            """Handle when a target gets hit"""
            hit_data = request.json
            target_id = hit_data.get('target_id')
            
            # TODO: Implement communication pattern to controller
            # if target_id and target_id in self.controller.game_state.active_targets:
            #     self.controller.game_state.active_targets.remove(target_id)
            #     self.controller.game_state.score += 10
            #     print(f"💥 Target {target_id} hit! Score: {self.controller.game_state.score} - OH YEAH!")
            print(f"💥 Target {target_id} hit! (communication pattern TBD)")
            
            response_data = {"status": "hit_registered", "score": 0}
            return Response(json.dumps(response_data))

    async def start_server(self, host='0.0.0.0', port=80, debug=True):
        """Start the master server - this is where the magic happens, dude!"""
        # WiFi AP is already set up by controller, just start HTTP server
        print(f"🌐 Master server starting on {host}:{port} - whatcha gonna do!")
        try:
            await self.app.start_server(host=host, port=port, debug=debug)
        except KeyboardInterrupt:
            print("🛑 Master server received shutdown signal!")
            raise  # Re-raise so main() can handle it
        except Exception as e:
            print(f"💥 Master server error: {e}")
            raise