# master_gui.py - GUI-First Master Controller

# CRITICAL: Import heavy server components FIRST to get clean RAM!
print("🚀 Pre-loading server components before GUI fragments memory...")
from master_server import MasterServer
from events import event_bus, emit_event, subscribe_to_event, EventTypes
print("✅ Server components loaded in clean memory!")

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd
from gui.widgets import Label, Button, CloseButton
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *

# WiFi and config imports
import network
import time
import asyncio
import urequests
from config import config
from helpers import reset_network_interface

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

# ========== ENTRY POINT ==========

def run_master():
    """Main GUI entry point - starts with navigation system"""
    print("🎯 Starting SNYPER - Navigation System Active")
    from views.main_screen import MainScreen
    start_ap(config.ssid, config.password)
    Screen.change(MainScreen, args=(game_state,))

if __name__ == "__main__":
    run_master()