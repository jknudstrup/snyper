from gui.core.ugui import Screen, ssd, Widget, display
from gui.widgets import Label, Button, CloseButton
from gui.core.writer import CWriter
from gui.primitives.pushbutton import Pushbutton
import gui.fonts.font14 as font
import gui.fonts.icons as icons
from gui.core.colors import *
from machine import Pin
import uasyncio as asyncio

# Global GPIO handlers - created once, persist across screens
_global_button_a = None
_global_button_b = None  
_global_button_x = None

def _init_global_buttons():
    """Initialize global GPIO handlers once"""
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
    if Screen.current_screen and hasattr(Screen.current_screen, 'button_a'):
        Screen.current_screen.button_a.trigger()

def _handle_button_b_press():
    """Global B button handler - find current screen's ButtonB and trigger it"""
    if Screen.current_screen and hasattr(Screen.current_screen, 'button_b'):
        Screen.current_screen.button_b.trigger()

def _handle_button_x_press():
    """Global X button handler - find current screen's ButtonX and trigger it"""  
    if Screen.current_screen and hasattr(Screen.current_screen, 'button_x'):
        Screen.current_screen.button_x.trigger()

class PassiveButton(Widget):
    """Non-focusable button for display-only purposes with callback support"""
    lit_time = 1000

    def __init__(self, writer, row, col, *, shape=RECTANGLE, height=20, width=50,
                 fgcolor=None, bgcolor=None, bdcolor=False, textcolor=None, 
                 litcolor=None, text="", callback=lambda *_: None, args=[]):
        
        sl = writer.stringlen(text)
        if shape == CIRCLE:
            width = max(sl, height)
            height = width
        else:
            width = max(sl + 10, width)
            
        # Call Widget constructor with active=False to make non-focusable
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, 
                        bdcolor, value=None, active=False)
        
        self.shape = shape
        self.radius = height // 2
        self.litcolor = litcolor
        self.textcolor = self.fgcolor if textcolor is None else textcolor
        self.text = text
        self.callback = callback
        self.callback_args = args
        
    def show(self):
        if self.screen is not Screen.current_screen:
            return
        x = self.col
        y = self.row
        w = self.width
        h = self.height
        super().show()  # Blank rectangle containing button
        
        if self.shape == CIRCLE:
            x += self.radius
            y += self.radius
            display.fillcircle(x, y, self.radius, self.bgcolor)
            display.circle(x, y, self.radius, self.fgcolor)
            if len(self.text):
                display.print_centred(self.writer, x, y, self.text, self.textcolor, self.bgcolor)
        else:
            xc = x + w // 2
            yc = y + h // 2
            if self.shape == RECTANGLE:
                display.fill_rect(x, y, w, h, self.bgcolor)
                display.rect(x, y, w, h, self.fgcolor)
                if len(self.text):
                    display.print_centred(self.writer, xc, yc, self.text, self.textcolor, self.bgcolor)
            elif self.shape == CLIPPED_RECT:
                display.fill_clip_rect(x, y, w, h, self.bgcolor)
                display.clip_rect(x, y, w, h, self.fgcolor)
                if len(self.text):
                    display.print_centred(self.writer, xc, yc, self.text, self.textcolor, self.bgcolor)

    async def shownormal(self):
        """Revert to normal color after a delay"""
        try:
            await asyncio.sleep_ms(PassiveButton.lit_time)
        except asyncio.CancelledError:
            pass
        self.bgcolor = self.def_bgcolor
        self.draw = True  # Redisplay

    def trigger(self):
        """Manually trigger the button (for physical button integration)"""
        self.callback(self, *self.callback_args)
        if self.litcolor is not None:
            if self.bgcolor != self.litcolor:
                self.bgcolor = self.litcolor
                self.draw = True  # Redisplay
                revert = asyncio.create_task(self.shownormal())
                Screen.current_screen.reg_task(revert, True)  # Cancel on screen change

class BaseScreen(Screen):
    def __init__(self):
        def my_callback(button, arg):
            print('Button pressed', arg)
        super().__init__()
        wri = CWriter(ssd, font, GREEN, BLACK, verbose=False)
        col = 2
        row = 2
        Label(wri, row, col, 'CARNIVAL SHOOTER')
        row = 50
        Button(wri, row, col, text='Yes', callback=my_callback, args=('Yes',))
        col += 60
        Button(wri, row, col, text='No', callback=my_callback, args=('No',))
        CloseButton(wri)  # Quit the application

def start_display():
    """Start the display - this runs synchronously like the hello world example!"""
    print('🎪 Display starting - just like the docs show!')
    print('🖥️  Calling Screen.change(BaseScreen)...')
    Screen.change(BaseScreen)  # This should work now!
    print('🖥️  Screen.change() returned - display should be active!')


def test_display():
    """Non-async test function just like the hello world"""
    print('Simple demo: testing display.')
    Screen.change(BaseScreen)


# Individual Physical Button Classes
# These replace the complex PhysicalButtonOverlay singleton system

class PhysicalButton(PassiveButton):
    """Base class for physical buttons - visual only, hardware handled globally"""
    
    def __init__(self, wri, pin=None, row=0, text='?', bgcolor=GREY, callback=None, **kwargs):
        """Initialize visual button (hardware handled by global GPIO handlers)"""
        defaults = {
            'row': row,
            'col': 208,
            'shape': CIRCLE,
            'height': 25,
            'width': 25,
            'text': text,
            'fgcolor': WHITE,
            'bgcolor': bgcolor,
            'litcolor': None,
            'callback': callback or self._default_callback
        }
        defaults.update(kwargs)
        
        super().__init__(wri, **defaults)
        
        # Initialize global GPIO handlers once
        _init_global_buttons()
    
    def _default_callback(self, button):
        """Default behavior if no callback provided"""
        pass


class ButtonA(PhysicalButton):
    """Physical A button (Back/Cancel) - Red circle"""
    def __init__(self, wri, callback=None, **kwargs):
        super().__init__(wri, pin=15, row=15, text='D', bgcolor=RED, callback=callback, **kwargs)


class ButtonB(PhysicalButton):
    """Physical B button (Skip/Next) - Blue circle"""
    def __init__(self, wri, callback=None, **kwargs):
        super().__init__(wri, pin=17, row=75, text='C', bgcolor=BLUE, callback=callback, **kwargs)


class ButtonX(PhysicalButton):
    """Physical X button (New/Action) - Dark blue circle"""
    def __init__(self, wri, callback=None, **kwargs):
        super().__init__(wri, pin=19, row=135, text='E', bgcolor=DARKBLUE, callback=callback, **kwargs)


class ButtonY(PhysicalButton):
    """Physical Y button (Select indicator) - Green circle - Visual only"""
    def __init__(self, wri, callback=None, **kwargs):
        # No GPIO pin - handled by GUI system
        super().__init__(wri, pin=None, row=195, text='F', bgcolor=DARKGREEN, callback=callback, **kwargs)
        # print("🟢 ButtonY: Visual indicator only (no hardware binding)")