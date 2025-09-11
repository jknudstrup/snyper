import network
import time
import uasyncio
from config.config import config
from utils.helpers import reset_network_interface
from target.target_events import target_event_queue, TargetEvent, HTTP_COMMAND_UP, HTTP_COMMAND_DOWN, HTTP_COMMAND_ACTIVATE
from utils.socket_protocol import SocketMessage, SocketServer

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

class TargetServer(SocketServer):
    """Target server - ready to serve and protect this digital battlefield!"""
    
    def __init__(self):
        # Initialize parent SocketServer with port
        super().__init__(config.port)
        
        self.node_id = config.get('node_id', 'target_unknown')
    

    async def register_with_master_socket(self):
        """Register this target with the master server using socket protocol"""
        master_ip = config.server_ip
        socket_port = config.port
        
        try:
            print(f"🔌 Socket registering with master at {master_ip}:{socket_port}")
            
            # Create registration message
            register_msg = SocketMessage(
                "REGISTER",
                target_id=self.node_id,
                data={"client_id": self.node_id}
            )
            
            # Use inherited send_message method
            result = await self.send_message(register_msg, master_ip, socket_port)
            
            if result["status"] == "failed":
                print(f"💥 Socket registration error: {result.get('error', 'Unknown error')}")
                return False
            
            # Process successful response
            response_message = result["response_message"]
            
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
                
        except Exception as e:
            print(f"💥 Socket registration error: {e}")
            return False


    async def _handle_message(self, message, client_ip, writer):
        """Handle individual socket messages from master"""
        print(f"📥 Target received: {message.type} from master")
        
        # Handle different message types
        if message.type == "ping":
            await self._handle_ping_command(message, writer)
        elif message.type == "stand_up":
            await self._handle_stand_up_command(message, writer)
        elif message.type == "lay_down":
            await self._handle_lay_down_command(message, writer)
        elif message.type == "activate":
            await self._handle_activate_command(message, writer)
        else:
            # Send error for unsupported message types
            error_msg = SocketMessage(
                "ERROR",
                msg_id=message.id,
                target_id=self.node_id,
                data={"error": f"Unsupported command: {message.type}"}
            )
            writer.write(error_msg.to_line().encode('utf-8'))
            await writer.drain()

    async def _handle_ping_command(self, message, writer):
        """Handle PING command from master"""
        print(f"🏓 Processing PING command from master")
        
        try:
            # Send PONG response
            pong_msg = SocketMessage(
                "PONG",
                msg_id=message.id,
                target_id=self.node_id,
                data={
                    "status": "alive",
                    "message": "Target reporting for duty!"
                }
            )
            
            response_line = pong_msg.to_line()
            print(f"📤 Sending PONG: {response_line.strip()}")
            writer.write(response_line.encode('utf-8'))
            await writer.drain()
            
        except Exception as e:
            print(f"💥 Error sending PONG response: {e}")
            # Send error response
            error_msg = SocketMessage(
                "ERROR",
                msg_id=message.id,
                target_id=self.node_id,
                data={"error": str(e)}
            )
            writer.write(error_msg.to_line().encode('utf-8'))
            await writer.drain()

    async def _handle_stand_up_command(self, message, writer):
        """Handle STAND_UP command from master"""
        print(f"⬆️ Processing STAND_UP command from master")
        
        try:
            # Emit event to controller (same as HTTP route)
            await target_event_queue.put(TargetEvent(HTTP_COMMAND_UP))
            
            # Send STANDING response
            standing_msg = SocketMessage(
                "STANDING",
                msg_id=message.id,
                target_id=self.node_id,
                data={
                    "status": "command_queued",
                    "message": "Stand up command queued"
                }
            )
            
            response_line = standing_msg.to_line()
            print(f"📤 Sending STANDING: {response_line.strip()}")
            writer.write(response_line.encode('utf-8'))
            await writer.drain()
            
        except Exception as e:
            print(f"💥 Error processing STAND_UP command: {e}")
            # Send error response
            error_msg = SocketMessage(
                "ERROR",
                msg_id=message.id,
                target_id=self.node_id,
                data={"error": str(e)}
            )
            writer.write(error_msg.to_line().encode('utf-8'))
            await writer.drain()

    async def _handle_lay_down_command(self, message, writer):
        """Handle LAY_DOWN command from master"""
        print(f"⬇️ Processing LAY_DOWN command from master")
        
        try:
            # Emit event to controller (same as HTTP route)
            await target_event_queue.put(TargetEvent(HTTP_COMMAND_DOWN))
            
            # Send DOWN response
            down_msg = SocketMessage(
                "DOWN",
                msg_id=message.id,
                target_id=self.node_id,
                data={
                    "status": "command_queued",
                    "message": "Lay down command queued"
                }
            )
            
            response_line = down_msg.to_line()
            print(f"📤 Sending DOWN: {response_line.strip()}")
            writer.write(response_line.encode('utf-8'))
            await writer.drain()
            
        except Exception as e:
            print(f"💥 Error processing LAY_DOWN command: {e}")
            # Send error response
            error_msg = SocketMessage(
                "ERROR",
                msg_id=message.id,
                target_id=self.node_id,
                data={"error": str(e)}
            )
            writer.write(error_msg.to_line().encode('utf-8'))
            await writer.drain()

    async def _handle_activate_command(self, message, writer):
        """Handle ACTIVATE command from master"""
        print(f"⚡ Processing ACTIVATE command from master")
        
        try:
            # Extract duration from message data
            duration = message.data.get("duration", 5)  # Default 5 seconds
            print(f"🎯 Target {self.node_id} received activate command for {duration} seconds")
            
            # Emit event to controller (same as HTTP route)
            await target_event_queue.put(TargetEvent(HTTP_COMMAND_ACTIVATE, {'duration': duration}))
            
            # Send ACTIVATED response
            activated_msg = SocketMessage(
                "ACTIVATED",
                msg_id=message.id,
                target_id=self.node_id,
                data={
                    "status": "activation_queued",
                    "duration": duration,
                    "message": "Activation command queued"
                }
            )
            
            response_line = activated_msg.to_line()
            print(f"📤 Sending ACTIVATED: {response_line.strip()}")
            writer.write(response_line.encode('utf-8'))
            await writer.drain()
            
        except Exception as e:
            print(f"💥 Error processing ACTIVATE command: {e}")
            # Send error response
            error_msg = SocketMessage(
                "ERROR",
                msg_id=message.id,
                target_id=self.node_id,
                data={"error": str(e)}
            )
            writer.write(error_msg.to_line().encode('utf-8'))
            await writer.drain()


    async def start_server(self, host='0.0.0.0', port=config.port):
        """Start the target server - time to get this party started!"""
        print(f"📡 Connecting to master WiFi: {config.ssid}")
        await connect_to_wifi(config.ssid, config.password)
        
        print(f"🤝 Registering with master server...")
        # Socket-only registration
        socket_success = await self.register_with_master_socket()
        if not socket_success:
            print(f"💥 Socket registration failed - no HTTP fallback in socket-only mode")
            raise RuntimeError("Target registration failed")
        
        print(f"🎯 Target server {self.node_id} starting socket-only on {host}:{port}")
        
        # Start socket server for incoming commands
        await self.start_socket_server(host)
        
        try:
            # Keep socket server running (no HTTP server)
            print(f"✅ Target running socket-only mode on port {port}")
            # Wait indefinitely for socket connections
            while True:
                await uasyncio.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Target server received shutdown signal!")
            # Clean up socket server
            if self.socket_server:
                self.socket_server.close()
                await self.socket_server.wait_closed()
            raise
        except Exception as e:
            print(f"💥 Target server error: {e}")
            # Clean up socket server
            if self.socket_server:
                self.socket_server.close()
                await self.socket_server.wait_closed()
            raise