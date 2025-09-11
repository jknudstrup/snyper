# Async socket client for bidirectional communication
# Implements MicroPython-compliant socket communication

import uasyncio
import socket
from utils.socket_protocol import (
    SocketMessage,
    MessageLineParser,
    MSG_PING, MSG_PONG, MSG_STAND_UP, MSG_STANDING, MSG_LAY_DOWN, MSG_DOWN,
    MSG_ACTIVATE, MSG_ACTIVATED, MSG_REGISTER, MSG_REGISTERED, MSG_ERROR,
    create_ping_message, create_stand_up_message, create_lay_down_message,
    create_activate_message, create_register_message
)

class MasterSocketClient:
    """Async socket client for master-to-target communication"""
    
    def __init__(self, default_port=8080, default_timeout=3):
        self.default_port = default_port
        self.default_timeout = default_timeout
        print(f"🔌 MasterSocketClient initialized (port: {default_port}, timeout: {default_timeout}s)")
    
    async def _resolve_address(self, host, port):
        """Resolve address using getaddrinfo() for MicroPython compliance"""
        try:
            # Use getaddrinfo for portable address resolution
            addr_info = socket.getaddrinfo(host, port)
            if not addr_info:
                raise OSError(f"Could not resolve address: {host}:{port}")
            
            # Get the first valid address
            family, socktype, proto, canonname, sockaddr = addr_info[0]
            return sockaddr
        except OSError as e:
            print(f"💥 Address resolution failed for {host}:{port} - {e}")
            raise
    
    async def _send_message_and_get_response(self, host, port, message, timeout=None):
        """
        Send a message to target and wait for response
        
        Returns:
            SocketMessage: Parsed response message
            
        Raises:
            OSError: For all socket-related errors
            asyncio.TimeoutError: For timeout scenarios
        """
        timeout = timeout or self.default_timeout
        
        try:
            # Resolve address first (MicroPython compliance)
            sockaddr = await self._resolve_address(host, port)
            print(f"🔗 Connecting to {host}:{port} (resolved: {sockaddr})")
            
            # Create async connection using uasyncio (not raw sockets)
            reader, writer = await uasyncio.wait_for(
                uasyncio.open_connection(host, port),
                timeout
            )
            
            try:
                # Send message using writer.write() (MicroPython compliance)
                message_line = message.to_line()
                print(f"📤 Sending: {message_line.strip()}")
                writer.write(message_line.encode('utf-8'))
                await writer.drain()
                
                # Read response using reader.read() (MicroPython compliance)
                print(f"📥 Waiting for response...")
                response_data = await uasyncio.wait_for(
                    reader.read(1024),  # Read up to 1KB
                    timeout
                )
                
                if not response_data:
                    raise OSError("Connection closed by target")
                
                # Parse response
                response_str = response_data.decode('utf-8').strip()
                print(f"📥 Received: {response_str}")
                
                response_message = SocketMessage.from_json(response_str)
                
                # Verify response matches request
                if response_message.id != message.id:
                    raise ValueError(f"Response ID mismatch: expected {message.id}, got {response_message.id}")
                
                return response_message
                
            finally:
                # Proper connection cleanup
                writer.close()
                await writer.wait_closed()
                
        except uasyncio.TimeoutError:
            print(f"⏰ Timeout communicating with {host}:{port}")
            raise
        except OSError as e:
            print(f"💥 Socket error communicating with {host}:{port} - {e}")
            raise
        except Exception as e:
            print(f"💥 Unexpected error communicating with {host}:{port} - {e}")
            raise OSError(f"Communication failed: {e}")
    
    async def ping_target(self, target_ip, target_id=None, timeout=None):
        """
        Ping a specific target
        
        Args:
            target_ip: IP address of target
            target_id: Optional target identifier
            timeout: Optional timeout override
            
        Returns:
            dict: Result with status and timing info
            
        Raises:
            OSError: For socket/network errors
        """
        target_id = target_id or f"target_at_{target_ip}"
        
        try:
            # Create ping message
            ping_msg = create_ping_message(target_id)
            
            # Send and get response
            response = await self._send_message_and_get_response(
                target_ip, 
                self.default_port, 
                ping_msg, 
                timeout
            )
            
            # Parse response
            if response.type == MSG_PONG:
                status = response.data.get("status", "unknown")
                if status == "alive":
                    print(f"✅ {target_id} at {target_ip} is ALIVE AND KICKING!")
                    return {"status": "alive", "ip": target_ip, "target_id": target_id}
                else:
                    print(f"⚠️ {target_id} responded but status unexpected: {status}")
                    return {"status": "unknown", "ip": target_ip, "target_id": target_id}
            
            elif response.type == MSG_ERROR:
                error_msg = response.data.get("error", "Unknown error")
                print(f"💥 {target_id} returned error: {error_msg}")
                return {"status": "error", "ip": target_ip, "target_id": target_id, "error": error_msg}
            
            else:
                print(f"⚠️ {target_id} sent unexpected response type: {response.type}")
                return {"status": "unknown", "ip": target_ip, "target_id": target_id}
                
        except (OSError, uasyncio.TimeoutError) as e:
            print(f"💥 {target_id} at {target_ip} failed to respond: {e}")
            return {"status": "failed", "ip": target_ip, "target_id": target_id, "error": str(e)}
    
    async def send_stand_up_command(self, target_ip, target_id=None, timeout=None):
        """Send stand up command to target"""
        target_id = target_id or f"target_at_{target_ip}"
        
        try:
            # Create stand up message
            stand_up_msg = create_stand_up_message(target_id)
            
            # Send and get response
            response = await self._send_message_and_get_response(
                target_ip,
                self.default_port,
                stand_up_msg,
                timeout
            )
            
            # Parse response
            if response.type == MSG_STANDING:
                status = response.data.get("status", "unknown")
                if status in ["standing", "command_queued"]:
                    print(f"✅ {target_id} received STAND UP command - {status}")
                    return {"status": status, "ip": target_ip, "target_id": target_id}
                else:
                    print(f"⚠️ {target_id} unexpected standing status: {status}")
                    return {"status": "unknown", "ip": target_ip, "target_id": target_id}
            
            elif response.type == MSG_ERROR:
                error_msg = response.data.get("error", "Unknown error")
                print(f"💥 {target_id} stand up error: {error_msg}")
                return {"status": "error", "ip": target_ip, "target_id": target_id, "error": error_msg}
            
            else:
                print(f"⚠️ {target_id} unexpected response to stand up: {response.type}")
                return {"status": "unknown", "ip": target_ip, "target_id": target_id}
                
        except (OSError, uasyncio.TimeoutError) as e:
            print(f"💥 {target_id} at {target_ip} stand up failed: {e}")
            return {"status": "failed", "ip": target_ip, "target_id": target_id, "error": str(e)}
    
    async def send_lay_down_command(self, target_ip, target_id=None, timeout=None):
        """Send lay down command to target"""
        target_id = target_id or f"target_at_{target_ip}"
        
        try:
            # Create lay down message
            lay_down_msg = create_lay_down_message(target_id)
            
            # Send and get response
            response = await self._send_message_and_get_response(
                target_ip,
                self.default_port,
                lay_down_msg,
                timeout
            )
            
            # Parse response
            if response.type == MSG_DOWN:
                status = response.data.get("status", "unknown")
                if status in ["down", "command_queued"]:
                    print(f"✅ {target_id} received LAY DOWN command - {status}")
                    return {"status": status, "ip": target_ip, "target_id": target_id}
                else:
                    print(f"⚠️ {target_id} unexpected down status: {status}")
                    return {"status": "unknown", "ip": target_ip, "target_id": target_id}
            
            elif response.type == MSG_ERROR:
                error_msg = response.data.get("error", "Unknown error")
                print(f"💥 {target_id} lay down error: {error_msg}")
                return {"status": "error", "ip": target_ip, "target_id": target_id, "error": error_msg}
            
            else:
                print(f"⚠️ {target_id} unexpected response to lay down: {response.type}")
                return {"status": "unknown", "ip": target_ip, "target_id": target_id}
                
        except (OSError, uasyncio.TimeoutError) as e:
            print(f"💥 {target_id} at {target_ip} lay down failed: {e}")
            return {"status": "failed", "ip": target_ip, "target_id": target_id, "error": str(e)}
    
    async def send_activate_command(self, target_ip, duration=5, target_id=None, timeout=None):
        """Send activate command to target"""
        target_id = target_id or f"target_at_{target_ip}"
        
        try:
            # Create activate message
            activate_msg = create_activate_message(target_id, duration)
            
            # Send and get response
            response = await self._send_message_and_get_response(
                target_ip,
                self.default_port,
                activate_msg,
                timeout
            )
            
            # Parse response
            if response.type == MSG_ACTIVATED:
                status = response.data.get("status", "unknown")
                response_duration = response.data.get("duration", duration)
                if status in ["activated", "activation_queued"]:
                    print(f"✅ {target_id} received ACTIVATE command - {status} ({response_duration}s)")
                    return {"status": status, "ip": target_ip, "target_id": target_id, "duration": response_duration}
                else:
                    print(f"⚠️ {target_id} unexpected activate status: {status}")
                    return {"status": "unknown", "ip": target_ip, "target_id": target_id}
            
            elif response.type == MSG_ERROR:
                error_msg = response.data.get("error", "Unknown error")
                print(f"💥 {target_id} activate error: {error_msg}")
                return {"status": "error", "ip": target_ip, "target_id": target_id, "error": error_msg}
            
            else:
                print(f"⚠️ {target_id} unexpected response to activate: {response.type}")
                return {"status": "unknown", "ip": target_ip, "target_id": target_id}
                
        except (OSError, uasyncio.TimeoutError) as e:
            print(f"💥 {target_id} at {target_ip} activate failed: {e}")
            return {"status": "failed", "ip": target_ip, "target_id": target_id, "error": str(e)}