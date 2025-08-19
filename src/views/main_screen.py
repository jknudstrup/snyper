# main_screen.py - SNYPER Main Menu Navigation Hub

from gui.core.ugui import Screen
from gui.widgets import Label, Button
from gui.core.writer import CWriter
from gui.core.colors import *
import gui.fonts.font14 as font14
import gui.fonts.freesans20 as freesans20
from hardware_setup import ssd

def navigate_to_screen(screen_class, game_state=None):
    """Helper function to navigate to a screen"""
    def callback(button, arg):
        print(f"🔄 Navigating to {screen_class.__name__}")
        if game_state and screen_class.__name__ == 'DebugScreen':
            Screen.change(screen_class, args=(game_state,))
        else:
            Screen.change(screen_class)
    return callback

class MainScreen(Screen):
    """SNYPER Main Menu - Navigation Hub"""
    def __init__(self, game_state=None):
        super().__init__()
        self.game_state = game_state
        
        # Start the HTTP server and game loop tasks
        self._start_server_tasks()
        wri = CWriter(ssd, font14, GREEN, BLACK, verbose=False)
        
        # Big title with freesans20 font
        title_wri = CWriter(ssd, freesans20, GREEN, BLACK, verbose=False)
        col = 2
        row = 5
        Label(title_wri, row, col, "SNYPER", fgcolor=GREEN)
        
        # Import screen classes here to avoid circular imports
        from views.new_game_screen import NewGameScreen
        from views.options_screen import OptionsScreen
        from views.debug_screen import DebugScreen
        
        # Navigation buttons (increased spacing for font14)
        row = 60
        col = 2
        Button(wri, row, col, text="New Game", callback=navigate_to_screen(NewGameScreen), args=("new_game",), height=25)
        
        row += 40
        Button(wri, row, col, text="Options", callback=navigate_to_screen(OptionsScreen), args=("options",), height=25)
        
        row += 40  
        Button(wri, row, col, text="Debug", callback=navigate_to_screen(DebugScreen, self.game_state), args=("debug",), height=25)
        
        # System status at bottom (more space)
        row = 200
        col = 2
        Label(wri, row, col, "System:", fgcolor=YELLOW)
        col += 80
        self.system_status = Label(wri, row, col, "Ready", fgcolor=GREEN)
    
    def _start_server_tasks(self):
        """Start the HTTP server and game loop async tasks"""
        from helpers import standalone_master_server_task, standalone_game_loop_task
        
        print("🚀 Registering HTTP server task with GUI event loop...")
        self.reg_task(standalone_master_server_task())
        
        print("🎮 Registering game loop task with GUI event loop...")  
        self.reg_task(standalone_game_loop_task())