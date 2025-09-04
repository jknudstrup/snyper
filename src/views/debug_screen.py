# debug_screen.py - Debug and Diagnostics Screen

from gui.core.ugui import Screen
from gui.widgets import Label, Button, Dropdown
from gui.core.writer import CWriter
from gui.core.colors import *
import gui.fonts.font14 as font14
from gui.core.ugui import ssd
from display.side_buttons import ButtonA, ButtonB, ButtonX, ButtonY
import json
import machine
from views.screen_helpers import navigate_to_main

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
        
        # Target selection dropdown
        row = 40
        self.target_dropdown = Dropdown(wri, row, col,
                                      elements=self.get_target_list(),
                                      dlines=3,
                                      bdcolor=GREEN,
                                      callback=self.target_selected)
        
        # Control buttons - evenly spaced in single column
        row += 60
        Button(wri, row, col, text="PING Targets", callback=self.ping_targets, args=("ping",), height=25)
        
        row += 35
        Button(wri, row, col, text="Raise All", callback=self.raise_all_targets, args=("raise_all",), height=25)
        
        row += 35
        Button(wri, row, col, text="Lower All", callback=self.lower_all_targets, args=("lower_all",), height=25)
        
        row += 35
        Button(wri, row, col, text="Disable", callback=self.disable_device, fgcolor=RED, height=25)
        
        # Selected target display
        # row += 40
        # Label(wri, row, col, "Selected:", fgcolor=YELLOW)
        # col += 80
        # self.selected_target_label = Label(wri, row, col, "None", fgcolor=WHITE)
        
        # Ping status display
        # row += 30
        # col = 2
        # Label(wri, row, col, "Status:", fgcolor=YELLOW)
        # col += 60
        # self.ping_status = Label(wri, row, col, "Ready", fgcolor=GREEN)
        
        # Create individual physical buttons
        self.button_a = ButtonA(wri, callback=self._navigate_to_main)
        self.button_b = ButtonB(wri, callback=lambda b: None)  # print("⏭️ Debug: Skip")
        self.button_x = ButtonX(wri, callback=lambda b: None)  # print("🆕 Debug: New")
        self.button_y = ButtonY(wri, callback=lambda b: None)  # print("▶️ Debug: Play")
    
    def ping_targets(self, button, arg):
        """PING ALL THE TARGETS - with cleanup via controller"""
        print("⚡ TURBO PING SEQUENCE INITIATED!")
        
        # Check if we have controller
        if not self.controller:
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
                print("💥 No targets to ping!")
                return
            
            # Count alive targets
            alive_count = sum(1 for result in results.values() if result["status"] == "alive")
            total_targets = len(results)
            
            # Log results
            if alive_count == total_targets:
                print(f"🎆 ALL {alive_count} targets responded")
            elif alive_count > 0:
                print(f"⚠️ {alive_count}/{total_targets} targets responded")
            else:
                print("💥 No targets responded to ping!")
            
            # Refresh dropdown in case targets were removed
            self.refresh_target_dropdown()
            
        except Exception as e:
            print(f"💥 Ping operation failed: {e}")
    
    def raise_all_targets(self, button, arg):
        """RAISE ALL TARGETS - make them stand up"""
        print("⬆️ RAISE ALL TARGETS SEQUENCE INITIATED!")
        
        # Check if we have controller
        if not self.controller:
            print("💥 No controller provided to DebugScreen!")
            return
        
        # Register async raise task with GUI event loop
        self.reg_task(self._do_raise_async())
    
    async def _do_raise_async(self):
        """Async wrapper for raise all operation"""
        try:
            # Use controller's raise_all method
            results = await self.controller.raise_all()
            
            if not results:
                print("💥 No targets to raise!")
                return
            
            # Count successful responses (standing or command_queued)
            success_count = sum(1 for result in results.values() 
                              if result["status"] in ["standing", "command_queued"])
            total_targets = len(results)
            
            # Log results
            if success_count == total_targets:
                print(f"🎆 ALL {success_count} targets received RAISE command")
            elif success_count > 0:
                print(f"⚠️ {success_count}/{total_targets} targets responded to raise command")
            else:
                print("💥 No targets responded to raise command!")
            
        except Exception as e:
            print(f"💥 Raise all operation failed: {e}")
    
    def lower_all_targets(self, button, arg):
        """LOWER ALL TARGETS - make them lay down"""
        print("⬇️ LOWER ALL TARGETS SEQUENCE INITIATED!")
        
        # Check if we have controller
        if not self.controller:
            print("💥 No controller provided to DebugScreen!")
            return
        
        # Register async lower task with GUI event loop
        self.reg_task(self._do_lower_async())
    
    async def _do_lower_async(self):
        """Async wrapper for lower all operation"""
        try:
            # Use controller's lower_all method
            results = await self.controller.lower_all()
            
            if not results:
                print("💥 No targets to lower!")
                return
            
            # Count successful responses (down or command_queued)
            success_count = sum(1 for result in results.values() 
                              if result["status"] in ["down", "command_queued"])
            total_targets = len(results)
            
            # Log results
            if success_count == total_targets:
                print(f"🎆 ALL {success_count} targets received LOWER command")
            elif success_count > 0:
                print(f"⚠️ {success_count}/{total_targets} targets responded to lower command")
            else:
                print("💥 No targets responded to lower command!")
            
        except Exception as e:
            print(f"💥 Lower all operation failed: {e}")
    
    def disable_device(self, button):
        """DISABLE DEVICE - set to disable mode and reset"""
        print("🚫 DISABLE DEVICE SEQUENCE INITIATED!")
        
        try:
            # Write disable state to device_id.json
            disable_config = {"node_id": "disable"}
            
            with open("device_id.json", "w") as f:
                json.dump(disable_config, f)
            
            print("✅ Device set to disable mode - resetting...")
            
            # Hard reset the device
            machine.reset()
            
        except Exception as e:
            print(f"💥 Disable operation failed: {e}")
    
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
        print(f"🎯 Target selected: {selected}")
    
    def refresh_target_dropdown(self):
        """Update dropdown with current registered targets"""
        new_elements = self.get_target_list()
        self.target_dropdown.els = new_elements
        self.target_dropdown.update()
        print(f"🔄 Target dropdown refreshed: {len(new_elements)} targets available")
    
    def _navigate_to_main(self, button):
        """Navigate back to MainScreen with controller"""
        navigate_to_main(self.controller)
    
