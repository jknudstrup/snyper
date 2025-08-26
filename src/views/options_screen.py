# options_screen.py - Options and Configuration Screen

from gui.core.ugui import Screen
from gui.widgets import Label, Button
from gui.core.writer import CWriter
from gui.core.colors import *
import gui.fonts.font14 as font14
from hardware_setup import ssd
from display import PhysicalButtonOverlay

class OptionsScreen(Screen):
    """Options and Configuration Screen"""
    def __init__(self):
        super().__init__()
        wri = CWriter(ssd, font14, GREEN, BLACK, verbose=False)
        
        # Title
        col = 2
        row = 2
        Label(wri, row, col, "Options", fgcolor=GREEN)
        
        # Configuration options (placeholder for now)
        row = 40
        Label(wri, row, col, "Configuration:")
        
        row += 30
        Button(wri, row, col, text="WiFi Settings", callback=self.wifi_settings, args=("wifi",), height=25)
        
        row += 30
        Button(wri, row, col, text="Device Config", callback=self.device_config, args=("device",), height=25)
        
        # Options screen button config: show back button and select button  
        button_config = {
            'A': {'icon': 'D', 'color': RED, 'callback': lambda b: None},      # A = Back (visual indicator)
            'Y': {'icon': 'F', 'color': DARKGREEN, 'callback': lambda b: None} # Y = Select indicator
        }
        
        # Initialize physical button overlay
        self.button_overlay = PhysicalButtonOverlay(wri, button_config)
    
    def wifi_settings(self, button, arg):
        print("📶 Opening WiFi settings...")
        # TODO: Implement WiFi configuration
        
    def device_config(self, button, arg):
        print("⚙️ Opening device configuration...")
        # TODO: Implement device configuration