# new_game_screen.py - New Game Setup Screen

from gui.core.ugui import Screen
from gui.widgets import Label, Button
from gui.core.writer import CWriter
from gui.core.colors import *
import gui.fonts.font14 as font14
from hardware_setup import ssd
from display import ButtonA, ButtonY
from views.screen_helpers import navigate_to_main

class NewGameScreen(Screen):
    """New Game Setup Screen"""
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        wri = CWriter(ssd, font14, GREEN, BLACK, verbose=False)
        
        # Title
        col = 2
        row = 2
        Label(wri, row, col, "New Game Setup", fgcolor=GREEN)
        
        # Game options (placeholder for now)
        row = 40
        Label(wri, row, col, "Game Mode:")
        row += 30
        Button(wri, row, col, text="Quick Game", callback=self.start_quick_game, args=("quick",), height=25)
        
        row += 30
        Button(wri, row, col, text="Custom Game", callback=self.start_custom_game, args=("custom",), height=25)
        
        # Add normal Back button for testing
        row += 40
        Button(wri, row, col, text="Back", callback=self._back_to_main, height=25)
        
        # Create individual physical buttons
        self.button_a = ButtonA(wri, callback=self._back_to_main)  # A = Back to Main
        self.button_y = ButtonY(wri)  # Y = Select indicator
    
    def start_quick_game(self, button, arg):
        # print("🎮 Starting quick game...")
        # TODO: Implement game start logic
        pass
        
    def start_custom_game(self, button, arg):
        # print("🎮 Starting custom game...")
        # TODO: Implement custom game setup
        pass
    
    def _back_to_main(self, button):
        """Navigate back to MainScreen - breaks circular reference"""
        navigate_to_main(self.controller)