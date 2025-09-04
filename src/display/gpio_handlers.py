# display/gpio_handlers.py - Global GPIO handlers for physical side buttons

from gui.primitives.pushbutton import Pushbutton
from machine import Pin

# Global GPIO handlers - created once, persist across screens
_global_button_a = None
_global_button_b = None  
_global_button_x = None

def _init_global_buttons():
    """Initialize global GPIO handlers for side buttons once"""
    global _global_button_a, _global_button_b, _global_button_x
    if _global_button_a is None:
        try:
            _global_button_a = Pushbutton(Pin(15, Pin.IN, Pin.PULL_UP))
            _global_button_a.release_func(_handle_button_a_press)
            _global_button_b = Pushbutton(Pin(17, Pin.IN, Pin.PULL_UP))
            _global_button_b.release_func(_handle_button_b_press)
            _global_button_x = Pushbutton(Pin(19, Pin.IN, Pin.PULL_UP))
            _global_button_x.release_func(_handle_button_x_press)
        except Exception as e:
            print(f"⚠️ Global GPIO setup failed: {e}")

def _handle_button_a_press():
    """Global A button handler - find current screen's ButtonA and trigger it"""
    from gui.core.ugui import Screen
    if Screen.current_screen and hasattr(Screen.current_screen, 'button_a'):
        Screen.current_screen.button_a.trigger()

def _handle_button_b_press():
    """Global B button handler - find current screen's ButtonB and trigger it"""
    from gui.core.ugui import Screen
    if Screen.current_screen and hasattr(Screen.current_screen, 'button_b'):
        Screen.current_screen.button_b.trigger()

def _handle_button_x_press():
    """Global X button handler - find current screen's ButtonX and trigger it"""
    from gui.core.ugui import Screen  
    if Screen.current_screen and hasattr(Screen.current_screen, 'button_x'):
        Screen.current_screen.button_x.trigger()