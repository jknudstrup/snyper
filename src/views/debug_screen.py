# debug_screen.py - Debug and Diagnostics Screen

from gui.core.ugui import Screen
from gui.widgets import Label, Button, CloseButton
from gui.core.writer import CWriter
from gui.core.colors import *
import gui.fonts.arial10 as arial10
from hardware_setup import ssd
import urequests

class DebugScreen(Screen):
    """Debug and Diagnostics Screen"""  
    def __init__(self):
        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        
        # Title
        col = 2
        row = 2
        Label(wri, row, col, "Debug & Diagnostics", fgcolor=GREEN)
        
        # PING functionality (moved from old MasterScreen)
        row = 40
        Button(wri, row, col, text="PING Targets", callback=self.ping_targets, args=("ping",))
        
        # Ping status display
        row = 70
        Label(wri, row, col, "Ping Status:")
        col += 80
        self.ping_status = Label(wri, row, col, "Ready", fgcolor=WHITE)
        
        # Additional debug options
        row = 100
        col = 2
        Button(wri, row, col, text="Network Info", callback=self.network_info, args=("network",))
        
        row += 30
        Button(wri, row, col, text="System Stats", callback=self.system_stats, args=("stats",))
        
        # Back button
        CloseButton(wri)
    
    def ping_targets(self, button, arg):
        """PING ALL THE TARGETS - moved from old MasterScreen"""
        print("⚡ TURBO PING SEQUENCE INITIATED!")
        self.ping_status.value("Pinging...")
        self.ping_status.fgcolor = YELLOW
        
        # Import here to avoid circular dependency
        from master import game_state
        
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
    
    def network_info(self, button, arg):
        print("📶 Displaying network information...")
        # TODO: Implement network diagnostics
        
    def system_stats(self, button, arg):
        print("📊 Displaying system statistics...")
        # TODO: Implement system statistics