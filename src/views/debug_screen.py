# debug_screen.py - Debug and Diagnostics Screen

from gui.core.ugui import Screen
from gui.widgets import Label, Button, Dropdown
from gui.core.writer import CWriter
from gui.core.colors import *
import gui.fonts.font14 as font14
from hardware_setup import ssd
import urequests

class DebugScreen(Screen):
    """Debug Screen"""  
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        wri = CWriter(ssd, font14, GREEN, BLACK, verbose=False)
        
        # Title
        col = 2
        row = 2
        Label(wri, row, col, "Debug", fgcolor=GREEN)
        
        # PING functionality (moved from old MasterScreen)
        row = 40
        Button(wri, row, col, text="PING Targets", callback=self.ping_targets, args=("ping",), height=25)
        
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
        
        # Back functionality now handled by physical A button
    
    def ping_targets(self, button, arg):
        """PING ALL THE TARGETS - with cleanup via controller"""
        print("⚡ TURBO PING SEQUENCE INITIATED!")
        self.ping_status.value("Pinging...")
        self.ping_status.fgcolor = YELLOW
        
        # Check if we have controller
        if not self.controller:
            self.ping_status.value("No controller")
            self.ping_status.fgcolor = RED
            print("💥 No controller provided to DebugScreen!")
            return
        
        # Register async ping task with GUI event loop
        self.reg_task(self._do_ping_async())
    
    async def _do_ping_async(self):
        """Async wrapper for ping operation"""
        try:
            # Use controller's ping and cleanup method
            results = await self.controller.ping_and_cleanup_targets()
            
            if not results:
                self.ping_status.value("No targets")
                self.ping_status.fgcolor = RED
                print("💥 No targets to ping!")
                return
            
            # Count alive targets
            alive_count = sum(1 for result in results.values() if result["status"] == "alive")
            total_targets = len(results)
            
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
            
            # Refresh dropdown in case targets were removed
            self.refresh_target_dropdown()
            
        except Exception as e:
            self.ping_status.value("Error")
            self.ping_status.fgcolor = RED
            print(f"💥 Ping operation failed: {e}")
    
    def get_target_list(self):
        """Get list of target names for dropdown"""
        if not self.controller:
            print("⚠️ No controller provided to DebugScreen")
            return ["No controller"]
            
        targets = self.controller.get_targets()
        if targets:
            return targets
        else:
            return ["No targets"]
    
    def target_selected(self, dropdown):
        """Handle target selection from dropdown"""
        selected = dropdown.textvalue()
        self.selected_target_label.value(selected)
        print(f"🎯 Target selected: {selected}")
    
    def refresh_target_dropdown(self):
        """Update dropdown with current registered targets"""
        new_elements = self.get_target_list()
        self.target_dropdown.els = new_elements
        self.target_dropdown.update()
        print(f"🔄 Target dropdown refreshed: {len(new_elements)} targets available")
    
