from microdot import Microdot, Response
import json
import network
import time
import urequests
from config import config
from events import event_bus, emit_event, EventTypes

def connect_to_wifi(ssid, password):
    """Connect to the master's WiFi AP - time to join the network, brother!"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print(f'🔄 Waiting for connection... ({max_wait})')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError(f'💥 Network connection failed. Status: {wlan.status()}')
    else:
        print(f'📡 Connected to {ssid}! IP: {wlan.ifconfig()[0]}')
        return wlan.ifconfig()[0]

class TargetServer:
    """Target server - ready to serve and protect this digital battlefield!"""
    
    def __init__(self):
        self.app = Microdot()
        self.node_id = config.get('node_id', 'target_unknown')
        self.master_url = f"http://{config.server_ip}:{config.port}"
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up all routes - building our target command center!"""
        
        @self.app.route('/ping')
        async def ping(request):
            """Health check endpoint - still standing strong!"""
            response_data = {
                "status": "alive", 
                "target_id": self.node_id,
                "message": "Target reporting for duty!"
            }
            return Response(json.dumps(response_data))

        @self.app.route('/stand_up')
        async def stand_up(request):
            """Command target to stand up"""
            await emit_event(EventTypes.TARGET_CONTROL, 'target_server', action='stand_up')
            print(f"🎯 Target {self.node_id} standing up - ready for action!")
            
            response_data = {"status": "standing", "target_id": self.node_id}
            return Response(json.dumps(response_data))

        @self.app.route('/lay_down')
        async def lay_down(request):
            """Command target to lay down"""
            await emit_event(EventTypes.TARGET_CONTROL, 'target_server', action='lay_down')
            print(f"🎯 Target {self.node_id} laying down - taking cover!")
            
            response_data = {"status": "down", "target_id": self.node_id}
            return Response(json.dumps(response_data))

        @self.app.route('/activate', methods=['POST'])
        async def activate(request):
            """Activate target for specified duration"""
            try:
                data = request.json
                duration = data.get('duration', 5)  # Default 5 seconds
                
                await emit_event(EventTypes.TARGET_CONTROL, 'target_server', 
                               action='activate', duration=duration)
                print(f"🎯 Target {self.node_id} activated for {duration} seconds - let's rock!")
                
                response_data = {
                    "status": "activated", 
                    "target_id": self.node_id,
                    "duration": duration
                }
                return Response(json.dumps(response_data))
            except Exception as e:
                print(f"💥 Activation error: {e}")
                return Response(json.dumps({"error": str(e)}), status_code=400)

    async def register_with_master(self):
        """Register this target with the master server"""
        try:
            registration_data = {'client_id': self.node_id}
            print(f"🤝 Registering with master at {self.master_url}/register")
            
            response = urequests.post(
                f"{self.master_url}/register",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(registration_data)
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully registered target {self.node_id} with master!")
                await emit_event(EventTypes.CLIENT_CONNECTED, 'target_server', 
                               client_id=self.node_id)
            else:
                print(f"⚠️  Registration failed: {response.status_code}")
            
            response.close()
        except Exception as e:
            print(f"💥 Registration error: {e}")

    async def report_hit(self, hit_value):
        """Report a target hit to the master server"""
        try:
            hit_data = {
                'target_id': self.node_id,
                'hit_value': hit_value
            }
            
            response = urequests.post(
                f"{self.master_url}/target_hit",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(hit_data)
            )
            
            if response.status_code == 200:
                print(f"💥 Hit reported successfully! Value: {hit_value}")
            else:
                print(f"⚠️  Hit report failed: {response.status_code}")
            
            response.close()
        except Exception as e:
            print(f"💥 Hit reporting error: {e}")

    async def start_server(self, host='0.0.0.0', port=8080):
        """Start the target server - time to get this party started!"""
        print(f"📡 Connecting to master WiFi: {config.ssid}")
        connect_to_wifi(config.ssid, config.password)
        
        print(f"🤝 Registering with master server...")
        await self.register_with_master()
        
        print(f"🎯 Target server {self.node_id} starting on {host}:{port}")
        try:
            await self.app.start_server(host=host, port=port, debug=True)
        except KeyboardInterrupt:
            print("🛑 Target server received shutdown signal!")
            raise
        except Exception as e:
            print(f"💥 Target server error: {e}")
            raise