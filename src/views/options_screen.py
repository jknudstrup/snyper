# options_screen.py - Options and Configuration Screen

from gui.core.ugui import Screen
from gui.widgets import Label, Button
from gui.core.writer import CWriter
from gui.core.colors import *
import gui.fonts.font14 as font14
from gui.core.ugui import ssd
from display.side_buttons import ButtonA, ButtonY
from views.screen_helpers import navigate_to_main

class OptionsScreen(Screen):
    """Options and Configuration Screen"""
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
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
        
        # Create individual physical buttons
        self.button_a = ButtonA(wri, callback=self._back_to_main)  # A = Back to Main
        self.button_y = ButtonY(wri)  # Y = Select indicator
    
    def wifi_settings(self, button, arg):
        # print("📶 Opening WiFi settings...")
        pass
        # TODO: Implement WiFi configuration
        
    def device_config(self, button, arg):
        # print("⚙️ Opening device configuration...")
        pass
        # TODO: Implement device configuration
    
    def _back_to_main(self, button):
        """Navigate back to MainScreen - breaks circular reference"""
        navigate_to_main(self.controller)