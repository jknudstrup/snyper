from gui.core.ugui import Screen

def navigate_to_screen(screen_class, controller=None):
    """Helper function to navigate to a screen"""
    def callback(button, arg):
        print(f"🔄 Navigating to {screen_class.__name__}")
        if controller and screen_class.__name__ == 'DebugScreen':
            Screen.change(screen_class, args=(controller,))
        else:
            Screen.change(screen_class)
    return callback