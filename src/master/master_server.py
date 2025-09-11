from microdot import Microdot, Response
import json
import uasyncio
from config.config import config
from helpers import initialize_access_point
from utils.socket_protocol import MessageLineParser, SocketMessage

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
        
        # Socket server for new protocol
        self.socket_server = None
        
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


    async def start_socket_server(self):
        """Start the socket registration server"""
        print(f"🔌 Starting socket server on {self.server_ip}:{self.port}")
        try:
            self.socket_server = await uasyncio.start_server(
                self._handle_socket_client,
                self.server_ip,
                self.port
            )
            print(f"✅ Socket server started on port {self.port}")
        except Exception as e:
            print(f"💥 Socket server failed to start: {e}")
            raise
    
    async def _handle_socket_client(self, reader, writer):
        """Handle incoming socket connections"""
        client_addr = writer.get_extra_info('peername')
        client_ip = client_addr[0] if client_addr else "unknown"
        print(f"🔌 Socket connection from {client_ip}")
        
        parser = MessageLineParser()
        
        try:
            # Read data from client
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                
                # Parse incoming messages
                messages = parser.feed(data.decode('utf-8'))
                
                for message in messages:
                    print(f"📥 Received socket message: {message.type} from {message.target_id}")
                    
                    # Handle registration messages
                    if message.type == "register":
                        await self._handle_socket_registration(message, client_ip, writer)
                    else:
                        # Send error for unsupported message types
                        error_msg = SocketMessage(
                            "ERROR",
                            msg_id=message.id,
                            target_id=message.target_id,
                            data={"error": f"Unsupported message type: {message.type}"}
                        )
                        writer.write(error_msg.to_line().encode('utf-8'))
                        await writer.drain()
                
        except Exception as e:
            print(f"💥 Socket client error: {e}")
        finally:
            print(f"🔌 Closing socket connection from {client_ip}")
            writer.close()
            await writer.wait_closed()
    
    async def _handle_socket_registration(self, message, client_ip, writer):
        """Handle socket registration message"""
        client_id = message.target_id
        print(f"🎯 Socket registration: {client_id} from {client_ip}")
        
        try:
            # Call the registration callback (same as HTTP)
            if self.on_target_register:
                print(f"🤝 Calling registration callback for {client_id} at {client_ip}")
                self.on_target_register(client_id, client_ip)
                print(f"✅ Socket registration callback completed for {client_id}")
            else:
                print(f"🤝 Target {client_id} at {client_ip} wants to register (no callback registered)")
            
            # Send success response
            response = SocketMessage(
                "REGISTERED",
                msg_id=message.id,
                target_id=client_id,
                data={"status": "registered"}
            )
            writer.write(response.to_line().encode('utf-8'))
            await writer.drain()
            
            print(f"✅ Socket registration complete for {client_id}")
            
        except Exception as e:
            print(f"💥 Socket registration error: {e}")
            # Send error response
            error_msg = SocketMessage(
                "ERROR",
                msg_id=message.id,
                target_id=client_id,
                data={"error": str(e)}
            )
            writer.write(error_msg.to_line().encode('utf-8'))
            await writer.drain()

    async def ping_target(self, target_ip, target_id):
        """Ping a specific target using socket communication"""
        try:
            print(f"🔌 Socket ping to {target_id} at {target_ip}:{self.port}")
            
            # Create ping message
            ping_msg = SocketMessage(
                "PING",
                target_id=target_id,
                data={"from": "master"}
            )
            
            # Connect to target
            reader, writer = await uasyncio.wait_for(
                uasyncio.open_connection(target_ip, self.port),
                timeout=5
            )
            
            try:
                # Send ping message
                message_line = ping_msg.to_line()
                print(f"📤 Sending ping: {message_line.strip()}")
                writer.write(message_line.encode('utf-8'))
                await writer.drain()
                
                # Read response
                response_data = await uasyncio.wait_for(
                    reader.read(1024),
                    timeout=5
                )
                
                if not response_data:
                    return {"status": "failed", "error": "No response"}
                
                # Parse response
                response_str = response_data.decode('utf-8').strip()
                print(f"📥 Received ping response: {response_str}")
                
                response_message = SocketMessage.from_json(response_str)
                
                if response_message.type == "pong":
                    status = response_message.data.get("status", "unknown")
                    print(f"✅ {target_id} responded with PONG: {status}")
                    return {"status": status, "ip": target_ip}
                elif response_message.type == "error":
                    error_msg = response_message.data.get("error", "Unknown error")
                    print(f"💥 {target_id} responded with error: {error_msg}")
                    return {"status": "error", "error": error_msg, "ip": target_ip}
                else:
                    print(f"⚠️ {target_id} unexpected response type: {response_message.type}")
                    return {"status": "unknown", "response_type": response_message.type, "ip": target_ip}
                    
            finally:
                writer.close()
                await writer.wait_closed()
                
        except Exception as e:
            print(f"💥 Socket ping error to {target_id}: {e}")
            return {"status": "failed", "error": str(e), "ip": target_ip}

    async def raise_target(self, target_ip, target_id):
        """Send stand_up command to a specific target using socket communication"""
        try:
            print(f"🔌 Socket stand_up to {target_id} at {target_ip}:{self.port}")
            
            # Create stand_up message
            stand_up_msg = SocketMessage(
                "STAND_UP",
                target_id=target_id,
                data={"from": "master"}
            )
            
            # Connect to target
            reader, writer = await uasyncio.wait_for(
                uasyncio.open_connection(target_ip, self.port),
                timeout=5
            )
            
            try:
                # Send stand_up message
                message_line = stand_up_msg.to_line()
                print(f"📤 Sending STAND_UP: {message_line.strip()}")
                writer.write(message_line.encode('utf-8'))
                await writer.drain()
                
                # Read response
                response_data = await uasyncio.wait_for(
                    reader.read(1024),
                    timeout=5
                )
                
                if not response_data:
                    return {"status": "failed", "error": "No response"}
                
                # Parse response
                response_str = response_data.decode('utf-8').strip()
                print(f"📥 Received stand_up response: {response_str}")
                
                response_message = SocketMessage.from_json(response_str)
                
                if response_message.type == "standing":
                    status = response_message.data.get("status", "unknown")
                    print(f"✅ {target_id} responded with STANDING: {status}")
                    return {"status": status, "ip": target_ip}
                elif response_message.type == "error":
                    error_msg = response_message.data.get("error", "Unknown error")
                    print(f"💥 {target_id} responded with error: {error_msg}")
                    return {"status": "error", "error": error_msg, "ip": target_ip}
                else:
                    print(f"⚠️ {target_id} unexpected response type: {response_message.type}")
                    return {"status": "unknown", "response_type": response_message.type, "ip": target_ip}
                    
            finally:
                writer.close()
                await writer.wait_closed()
                
        except Exception as e:
            print(f"💥 Socket stand_up error to {target_id}: {e}")
            return {"status": "failed", "error": str(e), "ip": target_ip}

    async def lower_target(self, target_ip, target_id):
        """Send lay_down command to a specific target using socket communication"""
        try:
            print(f"🔌 Socket lay_down to {target_id} at {target_ip}:{self.port}")
            
            # Create lay_down message
            lay_down_msg = SocketMessage(
                "LAY_DOWN",
                target_id=target_id,
                data={"from": "master"}
            )
            
            # Connect to target
            reader, writer = await uasyncio.wait_for(
                uasyncio.open_connection(target_ip, self.port),
                timeout=5
            )
            
            try:
                # Send lay_down message
                message_line = lay_down_msg.to_line()
                print(f"📤 Sending LAY_DOWN: {message_line.strip()}")
                writer.write(message_line.encode('utf-8'))
                await writer.drain()
                
                # Read response
                response_data = await uasyncio.wait_for(
                    reader.read(1024),
                    timeout=5
                )
                
                if not response_data:
                    return {"status": "failed", "error": "No response"}
                
                # Parse response
                response_str = response_data.decode('utf-8').strip()
                print(f"📥 Received lay_down response: {response_str}")
                
                response_message = SocketMessage.from_json(response_str)
                
                if response_message.type == "down":
                    status = response_message.data.get("status", "unknown")
                    print(f"✅ {target_id} responded with DOWN: {status}")
                    return {"status": status, "ip": target_ip}
                elif response_message.type == "error":
                    error_msg = response_message.data.get("error", "Unknown error")
                    print(f"💥 {target_id} responded with error: {error_msg}")
                    return {"status": "error", "error": error_msg, "ip": target_ip}
                else:
                    print(f"⚠️ {target_id} unexpected response type: {response_message.type}")
                    return {"status": "unknown", "response_type": response_message.type, "ip": target_ip}
                    
            finally:
                writer.close()
                await writer.wait_closed()
                
        except Exception as e:
            print(f"💥 Socket lay_down error to {target_id}: {e}")
            return {"status": "failed", "error": str(e), "ip": target_ip}

    async def start_server(self, debug=True):
        """Start socket-only server"""
        print(f"🌐 Master server starting socket-only on {self.server_ip}:{self.port}")
        
        # Start socket server only
        await self.start_socket_server()
        
        try:
            print(f"✅ Master running socket-only mode on port {self.port}")
            # Keep socket server running (no HTTP server)
            while True:
                await uasyncio.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Master server received shutdown signal!")
            # Clean up socket server
            if self.socket_server:
                self.socket_server.close()
                await self.socket_server.wait_closed()
            raise  # Re-raise so main() can handle it
        except Exception as e:
            print(f"💥 Master server error: {e}")
            # Clean up socket server
            if self.socket_server:
                self.socket_server.close()
                await self.socket_server.wait_closed()
            raise