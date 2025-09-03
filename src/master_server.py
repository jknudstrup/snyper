from microdot import Microdot, Response
import json
import network
import time
import asyncio
from config import config
from helpers import initialize_access_point

class MasterServer:
    """Master server class to handle HTTP requests - let me tell you something, this is gonna be AWESOME!"""
    
    def __init__(self, controller):
        self.app = Microdot()
        self.controller = controller  # Controller reference instead of game_state
        self._ap = None
        self._setup_routes()
    
    async def start_ap(self):
        """Create WiFi Access Point with clean network state"""
        system_state = self.controller.system_state
        print(f"🌐 Creating WiFi AP: {system_state.ssid}")
        
        # Use our new helper function with reset
        self._ap = await initialize_access_point(system_state.ssid, system_state.password, reset=True)
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
            
            # Register through controller - single source of truth!
            self.controller.register_target(client_id, client_ip)
            
            response_data = {"status": "registered", "client_id": client_id}
            return Response(json.dumps(response_data))

        @self.app.route('/target_hit', methods=['POST'])
        async def target_hit(request):
            """Handle when a target gets hit"""
            hit_data = request.json
            target_id = hit_data.get('target_id')
            
            if target_id and target_id in self.controller.game_state.active_targets:
                self.controller.game_state.active_targets.remove(target_id)
                self.controller.game_state.score += 10
                print(f"💥 Target {target_id} hit! Score: {self.controller.game_state.score} - OH YEAH!")
            
            response_data = {"status": "hit_registered", "score": self.controller.game_state.score}
            return Response(json.dumps(response_data))

        @self.app.route('/start_game', methods=['POST'])
        async def start_game(request):
            """Start the game"""
            self.controller.start_game()
            self.controller.game_state.score = 0
            self.controller.game_state.active_targets.clear()
            print("🚀 GAME STARTED - Let me tell you something, brother!")
            
            response_data = {"status": "game_started"}
            return Response(json.dumps(response_data))

        @self.app.route('/stop_game', methods=['POST'])
        async def stop_game(request):
            """Stop the game"""
            self.controller.stop_game()
            print("🏁 Game stopped - that was AWESOME!")
            
            response_data = {"status": "game_stopped", "final_score": self.controller.game_state.score}
            return Response(json.dumps(response_data))

        @self.app.route('/get_targets', methods=['GET'])
        async def get_targets(request):
            """Get current active targets - useful for debugging, brother!"""
            response_data = {
                "active_targets": self.controller.game_state.active_targets,
                "score": self.controller.game_state.score,
                "game_running": self.controller.game_state.game_running
            }
            return Response(json.dumps(response_data))

    async def start_server(self, host='0.0.0.0', port=80, debug=True):
        """Start the master server - this is where the magic happens, dude!"""
        # WiFi AP is already set up by master.py, just start HTTP server
        print(f"🌐 Master server starting on {self.controller.system_state.server_ip}:{self.controller.system_state.port} - whatcha gonna do!")
        try:
            await self.app.start_server(host=self.controller.system_state.server_ip, port=self.controller.system_state.port, debug=debug)
        except KeyboardInterrupt:
            print("🛑 Master server received shutdown signal!")
            raise  # Re-raise so main() can handle it
        except Exception as e:
            print(f"💥 Master server error: {e}")
            raise