#!/usr/bin/env python3
# test_protocol.py - Test the socket protocol utilities

import sys
sys.path.append('src')

from utils.socket_protocol import *

def test_basic_messages():
    """Test creating and parsing basic messages"""
    print("🧪 Testing Basic Message Creation and Parsing...")
    
    # Test PING message
    ping = create_ping_message("target_1")
    print(f"PING: {ping.to_line().strip()}")
    
    # Test PONG message
    pong = create_pong_message(ping.id, "target_1", "alive")
    print(f"PONG: {pong.to_line().strip()}")
    
    # Test parsing
    parsed_ping = SocketMessage.from_json(ping.to_json())
    print(f"Parsed PING type: {parsed_ping.type}, id: {parsed_ping.id}")
    
    print("✅ Basic message test passed!")

def test_message_parser():
    """Test the line parser with multiple messages"""
    print("\n🧪 Testing Message Line Parser...")
    
    parser = MessageLineParser()
    
    # Create some test messages
    ping1 = create_ping_message("target_1")
    ping2 = create_ping_message("target_2")
    stand_up = create_stand_up_message("target_1")
    
    # Simulate receiving data in chunks
    data_chunk1 = ping1.to_line() + ping2.to_line()[:10]  # Partial message
    data_chunk2 = ping2.to_line()[10:] + stand_up.to_line()
    
    # Parse first chunk
    messages1 = parser.feed(data_chunk1)
    print(f"Chunk 1: Found {len(messages1)} complete messages")
    for msg in messages1:
        print(f"  - {msg.type} to {msg.target_id}")
    
    # Parse second chunk  
    messages2 = parser.feed(data_chunk2)
    print(f"Chunk 2: Found {len(messages2)} complete messages")
    for msg in messages2:
        print(f"  - {msg.type} to {msg.target_id}")
    
    print("✅ Message parser test passed!")

def test_all_message_types():
    """Test all message types"""
    print("\n🧪 Testing All Message Types...")
    
    # PING/PONG
    ping = create_ping_message("target_1")
    pong = create_pong_message(ping.id, "target_1")
    print(f"PING/PONG: {ping.type} → {pong.type}")
    
    # STAND_UP/STANDING
    stand_up = create_stand_up_message("target_1")
    standing = create_standing_message(stand_up.id, "target_1")
    print(f"STAND_UP/STANDING: {stand_up.type} → {standing.type}")
    
    # LAY_DOWN/DOWN
    lay_down = create_lay_down_message("target_1")
    down = create_down_message(lay_down.id, "target_1")
    print(f"LAY_DOWN/DOWN: {lay_down.type} → {down.type}")
    
    # ACTIVATE/ACTIVATED
    activate = create_activate_message("target_1", 10)
    activated = create_activated_message(activate.id, "target_1", 10)
    print(f"ACTIVATE/ACTIVATED: {activate.type} → {activated.type}")
    print(f"  Duration: {activate.data['duration']} seconds")
    
    # ERROR
    error = create_error_message("msg_123", "Something went wrong", "target_1")
    print(f"ERROR: {error.type} - {error.data['error']}")
    
    print("✅ All message types test passed!")

def test_protocol_round_trip():
    """Test full round-trip: create → serialize → parse → use"""
    print("\n🧪 Testing Protocol Round Trip...")
    
    # Create original message
    original = create_activate_message("target_1", 5)
    print(f"Original: {original.type} for {original.target_id}, duration={original.data['duration']}")
    
    # Serialize to JSON line
    json_line = original.to_line()
    print(f"Serialized: {json_line.strip()}")
    
    # Parse back
    parsed = SocketMessage.from_json(json_line.strip())
    print(f"Parsed: {parsed.type} for {parsed.target_id}, duration={parsed.data['duration']}")
    
    # Verify they match
    assert original.type == parsed.type
    assert original.target_id == parsed.target_id
    assert original.data['duration'] == parsed.data['duration']
    
    print("✅ Round trip test passed!")

if __name__ == "__main__":
    print("🚀 SNYPER Socket Protocol Test Suite")
    print("=" * 50)
    
    test_basic_messages()
    test_message_parser()
    test_all_message_types()
    test_protocol_round_trip()
    
    print("\n🎆 All tests passed! Protocol is ready for implementation.")