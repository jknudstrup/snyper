# socket_protocol.py - SNYPER Socket Communication Protocol
#
# JSON Lines Protocol for Master/Target Communication
# Each message is a single line of JSON followed by newline

import json
import time
import uasyncio

class SocketMessage:
    """Represents a socket message in SNYPER protocol"""
    
    # Message Types (valid message types)
    TYPES = (
        "ping", "pong", "stand_up", "standing", "lay_down", "down",
        "activate", "activated", "register", "registered", "error"
    )
    
    def __init__(self, msg_type, msg_id=None, data=None, target_id=None):
        msg_type_lower = msg_type.lower()
        if msg_type_lower not in self.TYPES:
            raise ValueError(f"Invalid message type: {msg_type}. Valid types: {self.TYPES}")
        
        self.type = msg_type_lower
        self.id = msg_id or self._generate_id()
        self.data = data or {}
        self.target_id = target_id
        self.timestamp = time.time()
    
    def _generate_id(self):
        """Generate unique message ID"""
        return f"msg_{int(time.time() * 1000)}"
    
    def to_json(self):
        """Convert message to JSON string"""
        message = {
            "type": self.type,
            "id": self.id,
            "timestamp": self.timestamp
        }
        
        if self.target_id:
            message["target_id"] = self.target_id
            
        if self.data:
            message["data"] = self.data
            
        return json.dumps(message)
    
    def to_line(self):
        """Convert message to JSON line (with newline)"""
        return self.to_json() + "\n"
    
    @classmethod
    def from_json(cls, json_str):
        """Create message from JSON string"""
        try:
            data = json.loads(json_str)
            msg = cls(
                msg_type=data["type"],
                msg_id=data["id"],
                data=data.get("data"),
                target_id=data.get("target_id")
            )
            msg.timestamp = data.get("timestamp", time.time())
            return msg
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid message format: {e}")


# Message Line Parser

class MessageLineParser:
    """Parses incoming message lines from socket streams"""
    
    def __init__(self):
        self.buffer = ""
    
    def feed(self, data):
        """Feed data to parser, returns list of complete messages"""
        self.buffer += data
        messages = []
        
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            if line.strip():  # Skip empty lines
                try:
                    message = SocketMessage.from_json(line.strip())
                    messages.append(message)
                except ValueError as e:
                    print(f"⚠️ Invalid message received: {e}")
                    # Could create error message here if needed
        
        return messages
    
    def clear(self):
        """Clear the buffer"""
        self.buffer = ""

# Example Usage and Protocol Documentation

"""
SNYPER Socket Protocol Specification
===================================

Message Format: JSON Lines (each message is JSON followed by newline)

Base Message Structure:
{
    "type": "message_type",
    "id": "unique_message_id", 
    "timestamp": 1699123456.789,
    "target_id": "target_1",  // Optional
    "data": {}                 // Optional payload
}

Message Types:
--------------

1. PING / PONG (Health Check)
   Master → Target:
   {"type": "ping", "id": "msg_1", "target_id": "target_1"}
   
   Target → Master:
   {"type": "pong", "id": "msg_1", "target_id": "target_1", "data": {"status": "alive"}}

2. STAND_UP / STANDING (Target Stand Up)
   Master → Target:
   {"type": "stand_up", "id": "msg_2", "target_id": "target_1"}
   
   Target → Master:
   {"type": "standing", "id": "msg_2", "target_id": "target_1", "data": {"status": "standing"}}

3. LAY_DOWN / DOWN (Target Lay Down)
   Master → Target:
   {"type": "lay_down", "id": "msg_3", "target_id": "target_1"}
   
   Target → Master:
   {"type": "down", "id": "msg_3", "target_id": "target_1", "data": {"status": "down"}}

4. ACTIVATE / ACTIVATED (Target Activation)
   Master → Target:
   {"type": "activate", "id": "msg_4", "target_id": "target_1", "data": {"duration": 5}}
   
   Target → Master:
   {"type": "activated", "id": "msg_4", "target_id": "target_1", "data": {"status": "activated", "duration": 5}}

5. ERROR (Error Response)
   Any → Any:
   {"type": "error", "id": "msg_1", "target_id": "target_1", "data": {"error": "Command failed"}}

Benefits:
---------
- Human readable for debugging
- Built-in JSON parsing in MicroPython
- Newline delimited for easy stream parsing
- Extensible (easy to add fields)
- Request/response correlation via message ID
- Timestamps for debugging and timeout handling
"""

# Generic Socket Communication Function

async def send_message(command_msg, target_ip, port):
    """Generic function to send pre-constructed command messages to targets via socket"""
    target_id = command_msg.target_id
    command_type = command_msg.type
    
    try:
        print(f"🔌 Socket {command_type.lower()} to {target_id} at {target_ip}:{port}")
        
        # Connect to target
        reader, writer = await uasyncio.wait_for(
            uasyncio.open_connection(target_ip, port),
            timeout=5
        )
        
        try:
            # Send command message
            message_line = command_msg.to_line()
            print(f"📤 Sending {command_type}: {message_line.strip()}")
            writer.write(message_line.encode('utf-8'))
            await writer.drain()
            
            # Read response
            response_data = await uasyncio.wait_for(
                reader.read(1024),
                timeout=5
            )
            
            if not response_data:
                return {"status": "failed", "error": "No response", "ip": target_ip}
            
            # Parse response
            response_str = response_data.decode('utf-8').strip()
            print(f"📥 Received {command_type.lower()} response: {response_str}")
            
            response_message = SocketMessage.from_json(response_str)
            
            # Return raw response data for caller to process
            return {
                "status": "success",
                "ip": target_ip,
                "response_message": response_message
            }
                
        finally:
            writer.close()
            await writer.wait_closed()
            
    except Exception as e:
        print(f"💥 Socket {command_type.lower()} error to {target_id}: {e}")
        return {"status": "failed", "error": str(e), "ip": target_ip}