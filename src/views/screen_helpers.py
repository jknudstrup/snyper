from gui.core.ugui import Screen
import gc

def navigate_to_screen(screen_class, controller=None):
    """Helper function to navigate to a screen"""
    def callback(button, arg):
        # print(f"🔄 Navigating to {screen_class.__name__}")
        print(f"RAM: {gc.mem_free()}")
        gc.collect()  # Force GC before navigation
        
        # Get controller from current screen to avoid capturing it in closure
        current_controller = getattr(Screen.current_screen, 'controller', None) if Screen.current_screen else controller
        
        if current_controller:
            Screen.change(screen_class, mode=Screen.REPLACE, args=(current_controller,))
        else:
            Screen.change(screen_class, mode=Screen.REPLACE)
            
        gc.collect()  # Force GC after navigation
        print(f"RAM: {gc.mem_free()}")
    return callback

def navigate_to_main(controller):
    """Navigate back to MainScreen with controller"""
    from views.main_screen import MainScreen  # Import here to avoid circular import
    # print("🔄 Navigating back to MainScreen")
    print(f"RAM: {gc.mem_free()}")
    gc.collect()  # Force GC before navigation
    
    Screen.change(MainScreen, mode=Screen.REPLACE, args=(controller,))
    
    gc.collect()  # Force GC after navigation
    print(f"RAM: {gc.mem_free()}")