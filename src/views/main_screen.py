# main_screen.py - SNYPER Main Menu Navigation Hub

from gui.core.ugui import Screen
from gui.widgets import Label, Button
from gui.core.writer import CWriter
from gui.core.colors import *
import gui.fonts.font14 as font14
import gui.fonts.freesans20 as freesans20
from gui.core.ugui import ssd
from display.side_buttons import ButtonY
from views.screen_helpers import navigate_to_screen
import gc
import uasyncio

class MainScreen(Screen):
    """SNYPER Main Menu - Navigation Hub"""
    
    def __del__(self):
        print(f"💀 MainScreen #{id(self)} destroyed")
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        print(f"🏗️ MainScreen #{id(self)} created")
        
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
        Button(wri, row, col, text="New Game", callback=navigate_to_screen(NewGameScreen, self.controller), args=("new_game",), height=25)
        
        row += 40
        Button(wri, row, col, text="Options", callback=navigate_to_screen(OptionsScreen, self.controller), args=("options",), height=25)
        
        row += 40  
        Button(wri, row, col, text="Debug", callback=navigate_to_screen(DebugScreen, self.controller), args=("debug",), height=25)
        
        row += 40
        Button(wri, row, col, text="Test Async", callback=self._test_async_callback, height=25)
        
        self.button_y = ButtonY(wri)  # Visual select indicator only
        print(f"✨ MainScreen #{id(self)} ready! RAM: {gc.mem_free()}")
        
    
    def _start_server_tasks(self):
        """Start the HTTP server and game loop async tasks"""
        if not self.controller:
            print("⚠️ No controller provided - skipping server tasks")
            return
        
        # print(f"💾 RAM before server tasks: {gc.mem_free()}")
        
        # Only start server if it's not already running
        server_task = self.controller.start_server()
        if server_task is not None:
            # print("🚀 Registering HTTP server task with GUI event loop...")
            self.reg_task(server_task)
            # print(f"💾 RAM after server task registration: {gc.mem_free()}")
            
        
        gc.collect()
    
    def _test_async_callback(self, button):
        """Callback for Test Async button - starts async test"""
        print("🧪 Test Async button pressed - starting async test...")
        self.reg_task(self._test_async_function())
    
    async def _test_async_function(self):
        """Test async function with 3-second delay to verify non-blocking behavior"""
        print("⏳ Starting 3-second async test - UI should remain responsive...")
        await uasyncio.sleep_ms(3000)  # 3 seconds
        print("✅ Async test completed! UI should have remained responsive during wait.")