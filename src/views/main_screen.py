# main_screen.py - SNYPER Main Menu Navigation Hub

from gui.core.ugui import Screen
from gui.widgets import Label, Button
from gui.core.writer import CWriter
from gui.core.colors import *
import gui.fonts.arial10 as arial10
from hardware_setup import ssd

def navigate_to_screen(screen_class):
    """Helper function to navigate to a screen"""
    def callback(button, arg):
        print(f"🔄 Navigating to {screen_class.__name__}")
        Screen.change(screen_class)
    return callback

class MainScreen(Screen):
    """SNYPER Main Menu - Navigation Hub"""
    def __init__(self):
        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        
        # Title
        col = 2
        row = 2
        Label(wri, row, col, "SNYPER", fgcolor=GREEN)
        row = 25
        Label(wri, row, col, "Carnival Target System", fgcolor=WHITE)
        
        # Import screen classes here to avoid circular imports
        from views.new_game_screen import NewGameScreen
        from views.options_screen import OptionsScreen
        from views.debug_screen import DebugScreen
        
        # Navigation buttons
        row = 60
        col = 2
        Button(wri, row, col, text="New Game", callback=navigate_to_screen(NewGameScreen), args=("new_game",))
        
        row += 30
        Button(wri, row, col, text="Options", callback=navigate_to_screen(OptionsScreen), args=("options",))
        
        row += 30  
        Button(wri, row, col, text="Debug", callback=navigate_to_screen(DebugScreen), args=("debug",))
        
        # System status at bottom
        row = 180
        col = 2
        Label(wri, row, col, "System:", fgcolor=YELLOW)
        col += 60
        self.system_status = Label(wri, row, col, "Ready", fgcolor=GREEN)