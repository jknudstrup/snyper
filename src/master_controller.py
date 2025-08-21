# master_controller.py - MasterController Pattern Implementation
# 
# Single controller for managing all SNYPER system state and operations

import asyncio
import time
from config import config
from helpers import reset_network_interface

class SystemState:
    """Persistent system state that survives across game sessions"""
    
    def __init__(self):
        # Load all config values into system state
        self.ssid = config.ssid
        self.password = config.password  
        self.server_ip = config.server_ip
        self.port = config.port
        self.node_id = config.node_id
        
        # Target tracking - unified structure
        self.targets = {}  # target_name -> {"ip": ip_address, ...}
        
        print(f"📊 SystemState initialized - Node: {self.node_id}, AP: {self.ssid}")

class GameState:
    """Game-specific state that resets between games"""
    
    def __init__(self):
        self.score = 0
        self.active_targets = []
        self.game_running = False
        
        print("🎮 GameState initialized - Ready for action!")
    
    def reset_game(self):
        """Reset game state for new game"""
        self.score = 0
        self.active_targets.clear()
        self.game_running = False
        print("🔄 Game state reset - Ready for new game!")

class MasterController:
    """Central controller managing all SNYPER operations"""
    
    def __init__(self):
        self.system_state = SystemState()
        self.game_state = GameState()
        self.master_server = None
        self._server_task = None
        self._game_loop_task = None
        self._ap = None
        
        print("🎯 MasterController initialized - Command center operational!")
    
    def start_ap(self):
        """Create WiFi Access Point with clean network state"""
        print(f"🌐 Creating WiFi AP: {self.system_state.ssid}")
        
        # Reset network interfaces first to clear any cached bullshit!
        wlan, ap = reset_network_interface()
        
        # Now create a clean AP
        ap.active(True)
        ap.config(essid=self.system_state.ssid, password=self.system_state.password)

        while not ap.active():
            print("⏳ Waiting for AP to activate...")
            time.sleep(0.1)

        print(f"✅ WiFi AP '{self.system_state.ssid}' ACTIVE at {ap.ifconfig()[0]}")
        self._ap = ap
        return ap
    
    def start_server(self):
        """Start the HTTP server for target registration"""
        from master_server import MasterServer
        
        print("🌐 Starting master server through controller...")
        self.master_server = MasterServer(self)
        
        # Create server task but don't start it yet - that's handled by GUI
        async def server_task():
            print(f"🌐 Master HTTP server starting on {self.system_state.server_ip}:{self.system_state.port}")
            try:
                await self.master_server.app.start_server(
                    host=self.system_state.server_ip, 
                    port=self.system_state.port, 
                    debug=True
                )
            except Exception as e:
                print(f"💥 Master server error: {e}")
                raise
        
        self._server_task = server_task()
        return self._server_task
    
    def start_game_loop(self):
        """Start the game logic loop"""
        async def game_loop_task():
            print("🎯 Game loop starting through controller!")
            
            while True:
                if self.game_state.game_running:
                    print("🎮 Game tick - maintaining operational readiness...")
                    
                    # Example: Pop up a target every 3 seconds during game
                    if len(self.game_state.active_targets) < 3:  # Max 3 targets
                        target_id = f"target_{len(self.game_state.active_targets)}"
                        self.game_state.active_targets.append(target_id)
                        print(f"🎯 Target {target_id} deployed!")
                
                await asyncio.sleep(1.0)  # Strategic pause between operations
        
        self._game_loop_task = game_loop_task()
        return self._game_loop_task
    
    def register_target(self, client_id, client_ip):
        """Register a new target client"""
        self.system_state.targets[client_id] = {"ip": client_ip}
        
        print(f"🤝 Target {client_id} registered at {client_ip} via controller - LOCKED AND LOADED!")
        print(f"🔍 Controller Debug: {len(self.system_state.targets)} targets registered")
    
    def get_targets(self):
        """Get list of registered target names"""
        targets = list(self.system_state.targets.keys())
        print(f"📋 Controller returning {len(targets)} targets: {targets}")
        return targets
    
    def ping_targets(self):
        """Get target IPs for ping operations"""
        return {name: target["ip"] for name, target in self.system_state.targets.items()}
    
    def start_game(self):
        """Start a new game"""
        self.game_state.game_running = True
        print("🚀 Game started via controller!")
    
    def stop_game(self):
        """Stop current game"""
        self.game_state.game_running = False
        print("🛑 Game stopped via controller!")
    
    def reset_game(self):
        """Reset game state for new game"""
        self.game_state.reset_game()