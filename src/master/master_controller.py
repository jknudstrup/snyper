# master_controller.py - MasterController Pattern Implementation
# 
# Single controller for managing all SNYPER system state and operations

import uasyncio
from master.master_server import MasterServer


class MasterController:
    """Central controller managing all SNYPER operations"""
    
    def __init__(self):
        self.server = MasterServer(on_target_register=self.register_target)
        self._ap = None
        self._server_started = False
        
        # Target tracking - unified structure
        self.targets = {}  # target_name -> {"ip": ip_address, ...}
        
        print("🎯 MasterController initialized - Command center operational!")
    
    
    def start_ap(self):
        """Start WiFi Access Point via server (synchronous wrapper)"""
        # MicroPython has single event loop, just get it
        loop = uasyncio.get_event_loop()
        return loop.run_until_complete(self.server.start_ap())
    
    def start_server(self):
        """Start WiFi AP and HTTP server for target registration"""
        
        if self._server_started:
            print("⚠️ Server already started, skipping")
            return None
            
        print("🌐 Starting master server through controller...")
        self._server_started = True
        
        # Create server task but don't start it yet - that's handled by GUI
        async def server_task():
            # WiFi AP should already be started by now via controller.start_ap()
            try:
                await self.server.start_server(debug=True)
            except Exception as e:
                print(f"💥 Master server error: {e}")
                raise
        
        # Return the coroutine for reg_task to handle
        return server_task()
    
    
    def register_target(self, client_id, client_ip):
        """Register a new target client"""
        self.targets[client_id] = {"ip": client_ip}
        
        print(f"🤝 Target {client_id} registered at {client_ip} via controller - LOCKED AND LOADED!")
        print(f"🔍 Controller Debug: {len(self.targets)} targets registered")
    
    def get_targets(self):
        """Get list of registered target names"""
        targets = list(self.targets.keys())
        print(f"📋 Controller returning {len(targets)} targets: {targets}")
        return targets
    
    async def ping_targets(self):
        """Ping all registered targets and return results"""
        if not self.targets:
            print("⚠️ No targets registered to ping")
            return {}
        
        results = {}
        print(f"🚀 Socket pinging {len(self.targets)} registered targets...")
        
        for target_name, target_info in self.targets.items():
            target_ip = target_info["ip"]
            
            try:
                print(f"⚡ Socket pinging {target_name} at {target_ip}...")
                # Use socket ping instead of HTTP
                result = await self.server.ping_target(target_ip, target_name)
                results[target_name] = result
                
                status = result.get("status")
                if status == "alive":
                    print(f"✅ {target_name} at {target_ip} is ALIVE AND KICKING!")
                elif status == "failed":
                    error = result.get("error", "Unknown error")
                    print(f"💥 {target_name} at {target_ip} failed to respond: {error}")
                else:
                    print(f"⚠️ {target_name} responded with status: {status}")
                
            except Exception as e:
                print(f"💥 {target_name} at {target_ip} ping error: {e}")
                results[target_name] = {"status": "failed", "ip": target_ip, "error": str(e)}
            
            # Allow GUI to stay responsive between pings
            await uasyncio.sleep_ms(100)
        
        return results
    
    async def raise_all(self):
        """Send stand_up command to all registered targets"""
        if not self.targets:
            print("⚠️ No targets registered to raise")
            return {}
        
        results = {}
        print(f"🚀 Socket sending STAND UP command to {len(self.targets)} targets...")
        
        for target_name, target_info in self.targets.items():
            target_ip = target_info["ip"]
            
            try:
                print(f"⬆️ Socket commanding {target_name} to stand up...")
                # Use socket stand_up instead of HTTP
                result = await self.server.raise_target(target_ip, target_name)
                results[target_name] = result
                
                status = result.get("status")
                if status == "standing":
                    print(f"✅ {target_name} is now STANDING - ready for action!")
                elif status == "command_queued":
                    print(f"✅ {target_name} received STAND UP command - processing...")
                elif status == "failed":
                    error = result.get("error", "Unknown error")
                    print(f"💥 {target_name} at {target_ip} failed to respond: {error}")
                else:
                    print(f"⚠️ {target_name} responded with status: {status}")
                
            except Exception as e:
                print(f"💥 {target_name} at {target_ip} stand_up error: {e}")
                results[target_name] = {"status": "failed", "ip": target_ip, "error": str(e)}
            
            # Allow GUI to stay responsive between commands
            await uasyncio.sleep_ms(100)
        
        return results
    
    async def lower_all(self):
        """Send lay_down command to all registered targets"""
        if not self.targets:
            print("⚠️ No targets registered to lower")
            return {}
        
        results = {}
        print(f"🚀 Socket sending LAY DOWN command to {len(self.targets)} targets...")
        
        for target_name, target_info in self.targets.items():
            target_ip = target_info["ip"]
            
            try:
                print(f"⬇️ Socket commanding {target_name} to lay down...")
                # Use socket lay_down instead of HTTP
                result = await self.server.lower_target(target_ip, target_name)
                results[target_name] = result
                
                status = result.get("status")
                if status == "down":
                    print(f"✅ {target_name} is now DOWN - taking cover!")
                elif status == "command_queued":
                    print(f"✅ {target_name} received LAY DOWN command - processing...")
                elif status == "failed":
                    error = result.get("error", "Unknown error")
                    print(f"💥 {target_name} at {target_ip} failed to respond: {error}")
                else:
                    print(f"⚠️ {target_name} responded with status: {status}")
                
            except Exception as e:
                print(f"💥 {target_name} at {target_ip} lay_down error: {e}")
                results[target_name] = {"status": "failed", "ip": target_ip, "error": str(e)}
            
            # Allow GUI to stay responsive between commands
            await uasyncio.sleep_ms(100)
        
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