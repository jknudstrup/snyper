# debug_screen.py - Debug and Diagnostics Screen

from gui.core.ugui import Screen
from gui.widgets import Label, Button, CloseButton, Dropdown
from gui.core.writer import CWriter
from gui.core.colors import *
import gui.fonts.font14 as font14
from hardware_setup import ssd
import urequests

class DebugScreen(Screen):
    """Debug Screen"""  
    def __init__(self, game_state=None):
        super().__init__()
        self.game_state = game_state
        wri = CWriter(ssd, font14, GREEN, BLACK, verbose=False)
        
        # Title
        col = 2
        row = 2
        Label(wri, row, col, "Debug", fgcolor=GREEN)
        
        # PING functionality (moved from old MasterScreen)
        row = 40
        Button(wri, row, col, text="PING Targets", callback=self.ping_targets, args=("ping",), height=25)
        
        # Ping status display
        row = 70
        Label(wri, row, col, "Ping Status:")
        col += 80
        self.ping_status = Label(wri, row, col, "Ready", fgcolor=WHITE)
        
        # Target selection dropdown
        row = 100
        col = 2
        self.target_dropdown = Dropdown(wri, row, col,
                                      elements=self.get_target_list(),
                                      dlines=3,
                                      bdcolor=GREEN,
                                      callback=self.target_selected)
        
        # Selected target display
        row += 40
        Label(wri, row, col, "Selected:", fgcolor=YELLOW)
        col += 80
        self.selected_target_label = Label(wri, row, col, "None", fgcolor=WHITE)
        
        # Back button
        CloseButton(wri)
    
    def ping_targets(self, button, arg):
        """PING ALL THE TARGETS - moved from old MasterScreen"""
        print("⚡ TURBO PING SEQUENCE INITIATED!")
        self.ping_status.value("Pinging...")
        self.ping_status.fgcolor = YELLOW
        
        # Check if we have target IPs stored
        if not self.game_state or not hasattr(self.game_state, 'target_ips') or not self.game_state.target_ips:
            self.ping_status.value("No IPs stored")
            self.ping_status.fgcolor = RED
            print("💥 No target IPs stored - targets need to register first!")
            return
        
        alive_count = 0
        total_targets = len(self.game_state.target_ips)
        
        print(f"🚀 Pinging {total_targets} registered targets - NO SCANNING!")
        
        # Ping ONLY known target IPs - FAST AS HELL!
        for target_id, target_ip in self.game_state.target_ips.items():
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
    
    def get_target_list(self):
        """Get list of target names for dropdown"""
        if self.game_state and hasattr(self.game_state, 'target_ips') and self.game_state.target_ips:
            return list(self.game_state.target_ips.keys())
        else:
            return ["No targets registered"]
    
    def target_selected(self, dropdown):
        """Handle target selection from dropdown"""
        selected = dropdown.textvalue()
        self.selected_target_label.value(selected)
        print(f"🎯 Target selected: {selected}")
    
