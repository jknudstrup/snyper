# master_controller.py - MasterController Pattern Implementation
# 
# Single controller for managing all SNYPER system state and operations

import asyncio
import time
import urequests
from config import config
from master_server import MasterServer


class MasterController:
    """Central controller managing all SNYPER operations"""
    
    def __init__(self):
        self.server = MasterServer()
        self._server_task = None
        self._ap = None
        
        # Target tracking - unified structure
        self.targets = {}  # target_name -> {"ip": ip_address, ...}
        
        print("🎯 MasterController initialized - Command center operational!")
    
    
    def start_server(self):
        """Start WiFi AP and HTTP server for target registration"""
        
        print("🌐 Starting master server through controller...")
        
        # Create server task but don't start it yet - that's handled by GUI
        async def server_task():
            # Start WiFi AP first
            await self.server.start_ap()
            
            # Then start HTTP server
            print(f"🌐 Master HTTP server starting on {self.server.server_ip}:{self.server.port}")
            try:
                await self.server.app.start_server(
                    host=self.server.server_ip, 
                    port=self.server.port, 
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
                target_ip = self.targets[target_name]["ip"]
                del self.targets[target_name]
                print(f"🗑️ Removed {target_name} ({target_ip}) from registered targets")
            
            print(f"📊 Cleanup complete: {len(self.targets)} targets remaining")
        else:
            print("✨ All targets responded successfully - no cleanup needed!")
        
        return results