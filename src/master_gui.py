# master_gui.py - GUI-First Master Controller

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd
from gui.widgets import Label, Button, CloseButton
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *

class MasterScreen(Screen):
    """Minimal master screen - Phase 1"""
    def __init__(self):
        def my_callback(button, arg):
            print(f"🎮 Button pressed: {arg}")

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        
        col = 2
        row = 2
        Label(wri, row, col, "SNYPER")
        row = 30
        Label(wri, row, col, "Phase 1 - GUI Mode")
        
        row = 60
        Button(wri, row, col, text="Test", callback=my_callback, args=("test",))
        col += 60
        Button(wri, row, col, text="Reset", callback=my_callback, args=("reset",))
        
        CloseButton(wri)

def main():
    """Main GUI entry point"""
    print("🎯 Starting SNYPER - GUI Mode (Phase 1)")
    Screen.change(MasterScreen)

if __name__ == "__main__":
    main()