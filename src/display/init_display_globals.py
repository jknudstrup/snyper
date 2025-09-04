# display/init_display_globals.py - Initialize display globals for SNYPER
# 
# This module handles the initialization of display-related global variables
# that must be set up before GUI components can be imported.

def initialize_display_globals():
    """
    Initialize all display-related globals required by the GUI system.
    
    This function MUST be called before importing GUI components from ugui.
    It performs two critical tasks:
    1. Import hardware_setup for its side effects (creates ssd/display singletons)
    2. Initialize global GPIO button handlers
    """
    
    # Import hardware_setup for its side effects - this is REQUIRED by micropython-micro-gui
    # The library expects hardware_setup to create global 'ssd' and 'display' singleton instances
    # that are then made available through ugui imports
    import display.hardware_setup  # Creates ssd/display instances
    
    # Initialize global GPIO handlers for physical side buttons
    from display.gpio_handlers import _init_global_buttons
    _init_global_buttons()
    
    print("🖥️  Display globals initialized (ssd, display, GPIO handlers)")