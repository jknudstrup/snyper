from microdot import Microdot, Response
import json
import network
import time
from config import config

def start_ap(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password)

    while not ap.active():
        time.sleep(0.1)

    print(f"AP {ssid} up at {ap.ifconfig()[0]}")

class MasterServer:
    """Master server class to handle HTTP requests - let me tell you something, this is gonna be AWESOME!"""
    
    def __init__(self, game_state):
        self.app = Microdot()
        self.game_state = game_state  # Shared state reference
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up all the routes - building our wrestling federation!"""
        
        @self.app.route('/')
        async def index(request):
            """Root endpoint - let the clients know we're ready to rumble!"""
            response_data = {"status": "ready", "game": "carnival_shooter"}
            return Response(json.dumps(response_data))

        @self.app.route('/register', methods=['POST'])
        async def register_client(request):
            """Register a new target client"""
            client_data = request.json
            client_id = client_data.get('client_id', 'unknown')
            self.game_state.connected_clients.add(client_id)
            print(f"🤝 Client {client_id} connected - that's what I'm talking about!")
            
            response_data = {"status": "registered", "client_id": client_id}
            return Response(json.dumps(response_data))

        @self.app.route('/target_hit', methods=['POST'])
        async def target_hit(request):
            """Handle when a target gets hit"""
            hit_data = request.json
            target_id = hit_data.get('target_id')
            
            if target_id and target_id in self.game_state.active_targets:
                self.game_state.active_targets.remove(target_id)
                self.game_state.score += 10
                print(f"💥 Target {target_id} hit! Score: {self.game_state.score} - OH YEAH!")
            
            response_data = {"status": "hit_registered", "score": self.game_state.score}
            return Response(json.dumps(response_data))

        @self.app.route('/start_game', methods=['POST'])
        async def start_game(request):
            """Start the game"""
            self.game_state.game_running = True
            self.game_state.score = 0
            self.game_state.active_targets.clear()
            print("🚀 GAME STARTED - Let me tell you something, brother!")
            
            response_data = {"status": "game_started"}
            return Response(json.dumps(response_data))

        @self.app.route('/stop_game', methods=['POST'])
        async def stop_game(request):
            """Stop the game"""
            self.game_state.game_running = False
            print("🏁 Game stopped - that was AWESOME!")
            
            response_data = {"status": "game_stopped", "final_score": self.game_state.score}
            return Response(json.dumps(response_data))

        @self.app.route('/get_targets', methods=['GET'])
        async def get_targets(request):
            """Get current active targets - useful for debugging, brother!"""
            response_data = {
                "active_targets": self.game_state.active_targets,
                "score": self.game_state.score,
                "game_running": self.game_state.game_running
            }
            return Response(json.dumps(response_data))

    async def start_server(self, host='0.0.0.0', port=80, debug=True):
        """Start the master server - this is where the magic happens, dude!"""
        print(f"🌐 Setting up WiFi AP: {config.ssid}")
        start_ap(config.ssid, config.password)
        
        print(f"🌐 Master server starting on {config.server_ip}:{config.port} - whatcha gonna do!")
        try:
            await self.app.start_server(host=config.server_ip, port=config.port, debug=debug)
        except KeyboardInterrupt:
            print("🛑 Master server received shutdown signal!")
            raise  # Re-raise so main() can handle it
        except Exception as e:
            print(f"💥 Master server error: {e}")
            raise