# master_controller.py - MasterController Pattern Implementation
# 
# Single controller for managing all SNYPER system state and operations

import asyncio
import time
import urequests
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
        
        # Target tracking - unified structure
        self.targets = {}  # target_name -> {"ip": ip_address, ...}
        

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
    
    async def ping_targets(self):
        """Ping all registered targets and return results"""
        if not self.system_state.targets:
            print("⚠️ No targets registered to ping")
            return {}
        
        results = {}
        print(f"🚀 Pinging {len(self.system_state.targets)} registered targets...")
        
        for target_name, target_info in self.system_state.targets.items():
            target_ip = target_info["ip"]
            target_url = f"http://{target_ip}:{self.system_state.port}/ping"
            
            try:
                print(f"⚡ Pinging {target_name} at {target_ip}...")
                response = urequests.get(target_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "alive":
                        print(f"✅ {target_name} at {target_ip} is ALIVE AND KICKING!")
                        results[target_name] = {"status": "alive", "ip": target_ip}
                    else:
                        print(f"⚠️ {target_name} responded but status is not alive: {data}")
                        results[target_name] = {"status": "unknown", "ip": target_ip}
                else:
                    print(f"⚠️ {target_name} responded with HTTP {response.status_code}")
                    results[target_name] = {"status": "error", "ip": target_ip}
                
                response.close()
                
            except Exception as e:
                print(f"💥 {target_name} at {target_ip} failed to respond: {e}")
                results[target_name] = {"status": "failed", "ip": target_ip}
            
            # Allow GUI to stay responsive between pings
            await asyncio.sleep(0.1)
        
        return results
    
    async def raise_all(self):
        """Send stand_up command to all registered targets"""
        if not self.system_state.targets:
            print("⚠️ No targets registered to raise")
            return {}
        
        results = {}
        print(f"🚀 Sending STAND UP command to {len(self.system_state.targets)} targets...")
        
        for target_name, target_info in self.system_state.targets.items():
            target_ip = target_info["ip"]
            target_url = f"http://{target_ip}:{self.system_state.port}/stand_up"
            
            try:
                print(f"⬆️ Commanding {target_name} to stand up...")
                response = urequests.get(target_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "standing":
                        print(f"✅ {target_name} is now STANDING - ready for action!")
                        results[target_name] = {"status": "standing", "ip": target_ip}
                    else:
                        print(f"⚠️ {target_name} responded but status unexpected: {data}")
                        results[target_name] = {"status": "unknown", "ip": target_ip}
                else:
                    print(f"⚠️ {target_name} responded with HTTP {response.status_code}")
                    results[target_name] = {"status": "error", "ip": target_ip}
                
                response.close()
                
            except Exception as e:
                print(f"💥 {target_name} at {target_ip} failed to respond: {e}")
                results[target_name] = {"status": "failed", "ip": target_ip}
            
            # Allow GUI to stay responsive between commands
            await asyncio.sleep(0.1)
        
        return results
    
    async def lower_all(self):
        """Send lay_down command to all registered targets"""
        if not self.system_state.targets:
            print("⚠️ No targets registered to lower")
            return {}
        
        results = {}
        print(f"🚀 Sending LAY DOWN command to {len(self.system_state.targets)} targets...")
        
        for target_name, target_info in self.system_state.targets.items():
            target_ip = target_info["ip"]
            target_url = f"http://{target_ip}:{self.system_state.port}/lay_down"
            
            try:
                print(f"⬇️ Commanding {target_name} to lay down...")
                response = urequests.get(target_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "down":
                        print(f"✅ {target_name} is now DOWN - taking cover!")
                        results[target_name] = {"status": "down", "ip": target_ip}
                    else:
                        print(f"⚠️ {target_name} responded but status unexpected: {data}")
                        results[target_name] = {"status": "unknown", "ip": target_ip}
                else:
                    print(f"⚠️ {target_name} responded with HTTP {response.status_code}")
                    results[target_name] = {"status": "error", "ip": target_ip}
                
                response.close()
                
            except Exception as e:
                print(f"💥 {target_name} at {target_ip} failed to respond: {e}")
                results[target_name] = {"status": "failed", "ip": target_ip}
            
            # Allow GUI to stay responsive between commands
            await asyncio.sleep(0.1)
        
        return results
    
    async def ping_and_cleanup_targets(self):
        """Ping all targets and remove any that fail to respond"""
        results = await self.ping_targets()
        
        # Remove failed targets from system state
        failed_targets = [name for name, result in results.items() if result["status"] == "failed"]
        
        if failed_targets:
            print(f"🧹 Cleaning up {len(failed_targets)} failed targets...")
            for target_name in failed_targets:
                target_ip = self.system_state.targets[target_name]["ip"]
                del self.system_state.targets[target_name]
                print(f"🗑️ Removed {target_name} ({target_ip}) from registered targets")
            
            print(f"📊 Cleanup complete: {len(self.system_state.targets)} targets remaining")
        else:
            print("✨ All targets responded successfully - no cleanup needed!")
        
        return results
    
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