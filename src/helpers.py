# helpers.py - Shared utility functions for SNYPER

import network
import time
import asyncio
from config import config

def reset_network_interface():
    """Properly reset the network interface to handle soft resets
    
    This clears network caching bullshit that causes mysterious connection issues.
    Should be called at startup for both master and target devices.
    """
    # Get both interfaces
    wlan = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    
    # Force disconnect and deactivate station interface
    if wlan.active():
        try:
            wlan.disconnect()
            time.sleep(0.5)  # Give it time to disconnect
        except:
            pass
        
        try:
            wlan.active(False)
            time.sleep(1)  # Important: give it time to fully deactivate
        except:
            pass
    
    # Also ensure AP interface is off (in case it was used before)
    if ap.active():
        try:
            ap.active(False)
            time.sleep(0.5)
        except:
            pass
        
    print("🔄 Network interfaces reset - ready for clean connection!")
    return wlan, ap

def start_ap(ssid, password):
    """Create WiFi Access Point with clean network state"""
    print(f"🌐 Creating WiFi AP: {ssid}")
    
    # Reset network interfaces first to clear any cached bullshit!
    wlan, ap = reset_network_interface()
    
    # Now create a clean AP
    ap.active(True)
    ap.config(essid=ssid, password=password)

    while not ap.active():
        print("⏳ Waiting for AP to activate...")
        time.sleep(0.1)

    print(f"✅ WiFi AP '{ssid}' ACTIVE at {ap.ifconfig()[0]}")
    return ap

# ========== GAME STATE & TASKS ==========

class GameState:
    """Shared game state - the backbone of our operation!"""
    def __init__(self):
        self.score = 0
        self.active_targets = []
        self.connected_clients = set()
        self.game_running = False
        # Import event_bus here to avoid circular imports
        from events import event_bus
        self.event_bus = event_bus

# Global game state instance
game_state = GameState()

# Event handlers for game loop
async def handle_game_start(event):
    """Respond to game start orders"""
    print("🚀 Game loop received START command!")
    game_state.game_running = True

async def handle_game_stop(event):
    """Respond to game stop orders"""
    print("🛑 Game loop received STOP command!")
    game_state.game_running = False

async def handle_target_hit(event):
    """Process target elimination reports"""
    from events import emit_event, EventTypes
    
    target_id = event.data.get('target_id')
    if target_id and target_id in game_state.active_targets:
        game_state.active_targets.remove(target_id)
        old_score = game_state.score
        game_state.score += 10
        print(f"💥 Target {target_id} eliminated! Score: {old_score} -> {game_state.score}")
        
        # Broadcast score change intelligence
        await emit_event(EventTypes.SCORE_CHANGED, "game_loop",
                        old_score=old_score, new_score=game_state.score, target_id=target_id)

async def standalone_game_loop_task():
    """Main game logic - standalone version for GUI integration"""
    from events import emit_event, subscribe_to_event, EventTypes
    
    print("🎯 Game loop starting, old chap!")
    
    # Subscribe to events that affect game logic
    subscribe_to_event(EventTypes.GAME_STARTED, handle_game_start, "game_loop")
    subscribe_to_event(EventTypes.GAME_STOPPED, handle_game_stop, "game_loop") 
    subscribe_to_event(EventTypes.TARGET_HIT, handle_target_hit, "game_loop")
    
    while True:
        if game_state.game_running:
            print("🎮 Game tick - maintaining operational readiness...")
            
            # Example: Pop up a target every 3 seconds during game
            if len(game_state.active_targets) < 3:  # Max 3 targets
                target_id = f"target_{len(game_state.active_targets)}"
                game_state.active_targets.append(target_id)
                print(f"🎯 Target {target_id} deployed!")
                
                # Broadcast intelligence about new target
                await emit_event(EventTypes.TARGET_SPAWNED, "game_loop", 
                               target_id=target_id, position=len(game_state.active_targets))
        
        await asyncio.sleep(1.0)  # Strategic pause between operations

async def standalone_master_server_task():
    """Initialize and run the master server - standalone version for GUI integration"""
    from master_server import MasterServer
    
    print("🌐 Creating MasterServer instance for GUI integration...")
    master_server = MasterServer(game_state)  # Pass the shared state
    print("🌐 Starting master server from GUI...")
    
    # Skip WiFi AP setup - GUI already did it, just start HTTP server
    print(f"🌐 Master HTTP server starting on {config.server_ip}:{config.port}")
    try:
        # Call the microdot app directly, skip the MasterServer.start_server wrapper
        await master_server.app.start_server(host=config.server_ip, port=config.port, debug=True)
    except Exception as e:
        print(f"💥 Master server error: {e}")
        raise