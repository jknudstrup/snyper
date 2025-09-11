from microdot import Microdot, Response
import json
import network
import time
import urequests
import uasyncio
import socket
from config.config import config
from helpers import reset_network_interface
from target.target_events import target_event_queue, TargetEvent, HTTP_COMMAND_UP, HTTP_COMMAND_DOWN, HTTP_COMMAND_ACTIVATE
from utils.socket_protocol import SocketMessage

async def connect_to_wifi(ssid, password):
    """Connect to the master's WiFi AP - time to join the network, brother!"""
    print(f"🔧 Starting WiFi connection process to {ssid}")
    
    # Reset network interfaces first to clear any cached bullshit!
    # print("🔄 Resetting network interfaces...")
    await reset_network_interface()
    print("✅ Network interfaces reset complete")
    
    # Now do a clean connection
    print("🔌 Creating WLAN interface...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print(f"📡 Attempting connection to {ssid}...")
    wlan.connect(ssid, password)
    print("🎯 Connection initiated, waiting for status...")

    max_wait = 30
    while max_wait > 0:
        status = wlan.status()
        print(f'🔄 Connection status: {status}, waiting... ({max_wait})')
        if status < 0 or status >= 3:
            print(f"🎉 Connection status changed: {status}")
            break
        max_wait -= 1
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
            print(f'Target {self.node_id} was pinged')
            
            # ====== TEST CODE - REMOVE AFTER ASYNC DEBUGGING ======
            # Adding 3-second delay to test UI responsiveness during long operations
            print(f"🧪 TEST: Simulating 3-second delay on ping response...")
            await uasyncio.sleep_ms(3000)
            print(f"🧪 TEST: Delay complete, sending response")
            # ====== END TEST CODE ======
            
            response_data = {
                "status": "alive", 
                "target_id": self.node_id,
                "message": "Target reporting for duty!"
            }
            return Response(json.dumps(response_data))

        @self.app.route('/stand_up')
        async def stand_up(request):
            """Command target to stand up"""
            print(f"🎯 Target {self.node_id} received stand_up command")
            
            # Emit event to controller
            await target_event_queue.put(TargetEvent(HTTP_COMMAND_UP))
            
            response_data = {"status": "command_queued", "target_id": self.node_id}
            return Response(json.dumps(response_data))

        @self.app.route('/lay_down')
        async def lay_down(request):
            """Command target to lay down"""
            print(f"🎯 Target {self.node_id} received lay_down command")
            
            # Emit event to controller
            await target_event_queue.put(TargetEvent(HTTP_COMMAND_DOWN))
            
            response_data = {"status": "command_queued", "target_id": self.node_id}
            return Response(json.dumps(response_data))

        @self.app.route('/activate', methods=['POST'])
        async def activate(request):
            """Activate target for specified duration"""
            try:
                data = request.json
                duration = data.get('duration', 5)  # Default 5 seconds
                
                print(f"🎯 Target {self.node_id} received activate command for {duration} seconds")
                
                # Emit event to controller
                await target_event_queue.put(TargetEvent(HTTP_COMMAND_ACTIVATE, {'duration': duration}))
                
                response_data = {
                    "status": "activation_queued", 
                    "target_id": self.node_id,
                    "duration": duration
                }
                return Response(json.dumps(response_data))
            except Exception as e:
                print(f"💥 Activation error: {e}")
                return Response(json.dumps({"error": str(e)}), status_code=400)

    async def register_with_master_socket(self):
        """Register this target with the master server using socket protocol"""
        master_ip = config.server_ip
        socket_port = config.port + 1  # Master socket server on port 8081
        
        try:
            print(f"🔌 Socket registering with master at {master_ip}:{socket_port}")
            
            # Create registration message
            register_msg = SocketMessage(
                "REGISTER",
                target_id=self.node_id,
                data={"client_id": self.node_id}
            )
            
            # Connect to master socket server
            reader, writer = await uasyncio.wait_for(
                uasyncio.open_connection(master_ip, socket_port),
                timeout=5
            )
            
            try:
                # Send registration message
                message_line = register_msg.to_line()
                print(f"📤 Sending socket registration: {message_line.strip()}")
                writer.write(message_line.encode('utf-8'))
                await writer.drain()
                
                # Read response
                response_data = await uasyncio.wait_for(
                    reader.read(1024),
                    timeout=5
                )
                
                if not response_data:
                    raise OSError("Connection closed by master")
                
                # Parse response
                response_str = response_data.decode('utf-8').strip()
                print(f"📥 Received socket response: {response_str}")
                
                response_message = SocketMessage.from_json(response_str)
                
                # Check response
                if response_message.type == "registered":
                    print(f"✅ Successfully socket-registered target {self.node_id} with master!")
                    return True
                elif response_message.type == "error":
                    error_msg = response_message.data.get("error", "Unknown error")
                    print(f"💥 Socket registration error from master: {error_msg}")
                    return False
                else:
                    print(f"⚠️ Socket registration unexpected response type: {response_message.type}")
                    return False
                    
            finally:
                writer.close()
                await writer.wait_closed()
                
        except Exception as e:
            print(f"💥 Socket registration error: {e}")
            return False

    async def register_with_master(self):
        """Register this target with the master server (HTTP fallback)"""
        try:
            registration_data = {'client_id': self.node_id}
            print(f"🤝 HTTP Registering with master at {self.master_url}/register")
            
            response = urequests.post(
                f"{self.master_url}/register",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(registration_data)
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully registered target {self.node_id} with master!")
            else:
                print(f"⚠️  Registration failed: {response.status_code}")
            
            response.close()
        except Exception as e:
            print(f"💥 Registration error: {e}")

    async def report_result(self, hit_value):
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

    async def start_server(self, host='0.0.0.0', port=config.port):
        """Start the target server - time to get this party started!"""
        print(f"📡 Connecting to master WiFi: {config.ssid}")
        await connect_to_wifi(config.ssid, config.password)
        
        print(f"🤝 Registering with master server...")
        # Try socket registration first, fall back to HTTP
        socket_success = await self.register_with_master_socket()
        if not socket_success:
            print(f"🔄 Socket registration failed, trying HTTP fallback...")
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