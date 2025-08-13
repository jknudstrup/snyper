from microdot import Microdot, Response
from typing import Dict, Any, Optional
import json

class WebServer:
    """Web server class to handle HTTP requests - let me tell you something, this is gonna be AWESOME!"""
    
    def __init__(self, game_state) -> None:
        self.app: Microdot = Microdot()
        self.game_state = game_state  # Shared state reference
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Set up all the routes - building our wrestling federation!"""
        
        @self.app.route('/')
        async def index(request) -> Response:
            """Root endpoint - let the clients know we're ready to rumble!"""
            response_data: Dict[str, str] = {"status": "ready", "game": "carnival_shooter"}
            return Response(json.dumps(response_data))

        @self.app.route('/register', methods=['POST'])
        async def register_client(request) -> Response:
            """Register a new target client"""
            client_data: Dict[str, Any] = request.json
            client_id: str = client_data.get('client_id', 'unknown')
            self.game_state.connected_clients.add(client_id)
            print(f"🤝 Client {client_id} connected - that's what I'm talking about!")
            
            response_data: Dict[str, str] = {"status": "registered", "client_id": client_id}
            return Response(json.dumps(response_data))

        @self.app.route('/target_hit', methods=['POST'])
        async def target_hit(request) -> Response:
            """Handle when a target gets hit"""
            hit_data: Dict[str, Any] = request.json
            target_id: Optional[str] = hit_data.get('target_id')
            
            if target_id and target_id in self.game_state.active_targets:
                self.game_state.active_targets.remove(target_id)
                self.game_state.score += 10
                print(f"💥 Target {target_id} hit! Score: {self.game_state.score} - OH YEAH!")
            
            response_data: Dict[str, Any] = {"status": "hit_registered", "score": self.game_state.score}
            return Response(json.dumps(response_data))

        @self.app.route('/start_game', methods=['POST'])
        async def start_game(request) -> Response:
            """Start the game"""
            self.game_state.game_running = True
            self.game_state.score = 0
            self.game_state.active_targets.clear()
            print("🚀 GAME STARTED - Let me tell you something, brother!")
            
            response_data: Dict[str, str] = {"status": "game_started"}
            return Response(json.dumps(response_data))

        @self.app.route('/stop_game', methods=['POST'])
        async def stop_game(request) -> Response:
            """Stop the game"""
            self.game_state.game_running = False
            print("🏁 Game stopped - that was AWESOME!")
            
            response_data: Dict[str, Any] = {"status": "game_stopped", "final_score": self.game_state.score}
            return Response(json.dumps(response_data))

        @self.app.route('/get_targets', methods=['GET'])
        async def get_targets(request) -> Response:
            """Get current active targets - useful for debugging, brother!"""
            response_data: Dict[str, Any] = {
                "active_targets": self.game_state.active_targets,
                "score": self.game_state.score,
                "game_running": self.game_state.game_running
            }
            return Response(json.dumps(response_data))

    async def start_server(self, host: str = '0.0.0.0', port: int = 80, debug: bool = True) -> None:
        """Start the web server - this is where the magic happens, dude!"""
        print(f"🌐 Web server starting on {host}:{port} - whatcha gonna do!")
        await self.app.start_server(host=host, port=port, debug=debug)