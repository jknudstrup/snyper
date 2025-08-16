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

class MasterScreen(Screen):
    """SNYPER master screen - Phase 2"""
    def __init__(self):
        def my_callback(button, arg):
            print(f"🎮 Button pressed: {arg}")
        
        def ping_targets_callback(button, arg):
            """PING ALL THE TARGETS - LIGHTNING SPEED EDITION!"""
            print(f"⚡ TURBO PING button pressed - PREPARE FOR SPEED!")
            self.ping_all_targets()

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        
        col = 2
        row = 2
        Label(wri, row, col, "SNYPER")
        row = 25
        Label(wri, row, col, "Phase 2 - Server Mode")
        
        # WiFi status display
        row = 50
        Label(wri, row, col, "WiFi AP:")
        col += 60
        self.wifi_status = Label(wri, row, col, "STARTING...", fgcolor=YELLOW)
        
        # Server status display
        row = 70
        col = 2
        Label(wri, row, col, "Server:")
        col += 60
        self.server_status = Label(wri, row, col, "STARTING...", fgcolor=YELLOW)
        
        # Control buttons
        row = 90
        col = 2
        Button(wri, row, col, text="Test", callback=my_callback, args=("test",))
        col += 60
        Button(wri, row, col, text="Reset", callback=my_callback, args=("reset",))
        
        # PING TARGETS button - LET'S ROCK!
        row = 110
        col = 2
        Button(wri, row, col, text="PING", callback=ping_targets_callback, args=("ping",))
        
        # Ping status display
        row = 130
        col = 2
        Label(wri, row, col, "Ping Status:")
        col += 80
        self.ping_status = Label(wri, row, col, "Ready", fgcolor=WHITE)
        
        CloseButton(wri)
        
        # Setup WiFi AFTER display is ready
        print("🖥️  Display widgets created - now starting WiFi...")
        try:
            self.ap = start_ap(config.ssid, config.password)
            # Verify AP is actually working
            print(f"📶 WiFi AP Details: IP={self.ap.ifconfig()[0]}, Active={self.ap.active()}")
            print(f"📶 AP Config: SSID='{config.ssid}', ready for target connections")
            self.wifi_status.value("ACTIVE")
            self.wifi_status.fgcolor = GREEN
        except Exception as e:
            print(f"💥 WiFi setup failed: {e}")
            self.wifi_status.value("FAILED")
            self.wifi_status.fgcolor = RED
            return
        
        # Register async tasks with GUI - server already loaded!
        print("🚀 Registering async tasks with GUI (no imports needed)...")
        try:
            self.reg_task(standalone_game_loop_task())
            self.reg_task(standalone_master_server_task())
            self.server_status.value("ACTIVE")
            self.server_status.fgcolor = GREEN
            print("✅ All tasks registered successfully!")
        except Exception as e:
            print(f"💥 Task registration failed: {e}")
            self.server_status.value("FAILED")
            self.server_status.fgcolor = RED
    
    def ping_all_targets(self):
        """Ping ONLY registered targets - LIGHTNING FAST!"""
        print("⚡ TURBO PING SEQUENCE INITIATED!")
        self.ping_status.value("Pinging...")
        self.ping_status.fgcolor = YELLOW
        
        # Check if we have target IPs stored
        if not hasattr(game_state, 'target_ips') or not game_state.target_ips:
            self.ping_status.value("No IPs stored")
            self.ping_status.fgcolor = RED
            print("💥 No target IPs stored - targets need to register first!")
            return
        
        alive_count = 0
        total_targets = len(game_state.target_ips)
        
        print(f"🚀 Pinging {total_targets} registered targets - NO SCANNING!")
        
        # Ping ONLY known target IPs - FAST AS HELL!
        for target_id, target_ip in game_state.target_ips.items():
            try:
                print(f"⚡ Pinging {target_id} at {target_ip}:8080...")
                response = urequests.get(f"http://{target_ip}:8080/ping", timeout=1)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {target_id} at {target_ip} is ALIVE AND KICKING!")
                    alive_count += 1
                else:
                    print(f"⚠️ {target_id} at {target_ip} responded with status {response.status_code}")
                
                response.close()
                
            except Exception as e:
                print(f"💥 {target_id} at {target_ip} unreachable: {e}")
        
        # Update status display
        if alive_count == total_targets:
            self.ping_status.value(f"✅ {alive_count}/{total_targets}")
            self.ping_status.fgcolor = GREEN
            print(f"🎆 ALL {alive_count} targets responded - FLAWLESS VICTORY!")
        elif alive_count > 0:
            self.ping_status.value(f"⚠️ {alive_count}/{total_targets}")
            self.ping_status.fgcolor = YELLOW
            print(f"⚠️ {alive_count}/{total_targets} targets responded")
        else:
            self.ping_status.value("💥 None")
            self.ping_status.fgcolor = RED
            print("💥 No targets responded to ping!")

def main():
    """Main GUI entry point"""
    print("🎯 Starting SNYPER - GUI Mode (Phase 2 - Server)")
    Screen.change(MasterScreen)

if __name__ == "__main__":
    main()