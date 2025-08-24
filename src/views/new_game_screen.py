# new_game_screen.py - New Game Setup Screen

from gui.core.ugui import Screen
from gui.widgets import Label, Button
from gui.core.writer import CWriter
from gui.core.colors import *
import gui.fonts.font14 as font14
from hardware_setup import ssd

class NewGameScreen(Screen):
    """New Game Setup Screen"""
    def __init__(self):
        super().__init__()
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
        
        # Back functionality now handled by physical A button
    
    def start_quick_game(self, button, arg):
        print("🎮 Starting quick game...")
        # TODO: Implement game start logic
        
    def start_custom_game(self, button, arg):
        print("🎮 Starting custom game...")
        # TODO: Implement custom game setup