# master.py - GUI-First Master Controller
#
# ⚠️  STANDING ORDER: NO IMPORTS FROM THIS FILE ⚠️
# ONLY main.py may import run_master() from this file.
# All other scripts must use helpers.py for shared functions.
# This prevents circular dependencies and maintains clean architecture.

# CRITICAL: Import heavy server components FIRST to get clean RAM!
print("🚀 Pre-loading server components before GUI fragments memory...")
from master_server import MasterServer
from events import event_bus, emit_event, subscribe_to_event, EventTypes
print("✅ Server components loaded in clean memory!")

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen

# ========== ENTRY POINT ==========

def run_master():
    """Main GUI entry point - starts with navigation system"""
    print("🎯 Starting SNYPER - Navigation System Active")
    
    # Create controller instance
    from master_controller import MasterController
    controller = MasterController()
    
    # Start WiFi AP through controller
    controller.start_ap()
    
    # Launch GUI with controller
    from views.main_screen import MainScreen
    Screen.change(MainScreen, args=(controller,))

if __name__ == "__main__":
    run_master()