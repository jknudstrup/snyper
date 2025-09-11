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
        self.socket_port = self.port + 1  # Use port 8081 for socket protocol
        
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
        print(f"🔌 Starting socket server on {self.server_ip}:{self.socket_port}")
        try:
            self.socket_server = await uasyncio.start_server(
                self._handle_socket_client,
                self.server_ip,
                self.socket_port
            )
            print(f"✅ Socket server started on port {self.socket_port}")
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

    async def start_server(self, debug=True):
        """Start both HTTP and socket servers"""
        print(f"🌐 Master server starting on {self.server_ip}:{self.port} - whatcha gonna do!")
        
        # Start socket server first
        await self.start_socket_server()
        
        try:
            print(f"🚀 About to start HTTP server on {self.server_ip}:{self.port}")
            await self.app.start_server(host=self.server_ip, port=self.port, debug=debug)
            print(f"✅ HTTP server started successfully!")
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