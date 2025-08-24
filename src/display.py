from gui.core.ugui import Screen, ssd, Widget, display
from gui.widgets import Label, Button, CloseButton
from gui.core.writer import CWriter
from gui.primitives.pushbutton import Pushbutton
import gui.fonts.font14 as font
from gui.core.colors import *
from machine import Pin
import uasyncio as asyncio

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

class PhysicalButtonOverlay:
    """Physical button overlay with GUI buttons on right side of screen"""
    
    def __init__(self, wri):
        # Initialize physical buttons from hardware_setup.py
        self.keyA = Pushbutton(Pin(15, Pin.IN, Pin.PULL_UP))
        self.keyB = Pushbutton(Pin(17, Pin.IN, Pin.PULL_UP))  
        self.keyX = Pushbutton(Pin(19, Pin.IN, Pin.PULL_UP))
        self.keyY = Pushbutton(Pin(21, Pin.IN, Pin.PULL_UP))
        
        # Use the provided writer
        self.wri = wri
        
        # Create GUI buttons positioned on screen
        self.gui_buttons = []
        self.setup_gui_buttons()
        self.bind_physical_to_gui()
        
        print("🎮 Physical button overlay initialized!")
    
    def setup_gui_buttons(self):
        """Create circular GUI buttons in vertical column on right edge"""
        # Button positions on absolute screen coordinates (right edge)
        button_configs = [
            {'label': 'A', 'row': 15, 'col': 208, 'callback': self.button_a_pressed, 'color': RED},
            {'label': 'B', 'row': 75, 'col': 208, 'callback': self.button_b_pressed, 'color': BLUE}, 
            {'label': 'X', 'row': 135, 'col': 208, 'callback': self.button_x_pressed, 'color': DARKBLUE},
            {'label': 'Y', 'row': 195, 'col': 208, 'callback': self.button_y_pressed, 'color': DARKGREEN}
        ]
        
        for config in button_configs:
            btn = PassiveButton(self.wri, 
                               row=config['row'], 
                               col=config['col'],
                               text=config['label'],
                               callback=config['callback'],
                               shape=CIRCLE,
                               height=25,
                               width=25,  
                               fgcolor=WHITE,
                               bgcolor=config['color'],
                               litcolor=YELLOW)  # Use yellow for lit state to contrast with all colors
            self.gui_buttons.append(btn)
            
        print(f"📱 Created {len(self.gui_buttons)} circular GUI buttons")
    
    def bind_physical_to_gui(self):
        """Bind physical button presses to trigger GUI button actions"""
        self.keyA.press_func(self.trigger_gui_button, (0,))
        self.keyB.press_func(self.trigger_gui_button, (1,))
        self.keyX.press_func(self.trigger_gui_button, (2,))  
        self.keyY.press_func(self.trigger_gui_button, (3,))
        
        print("🔗 Physical buttons bound to GUI buttons")
    
    def trigger_gui_button(self, button_index):
        """Simulate GUI button press and provide visual feedback"""
        if 0 <= button_index < len(self.gui_buttons):
            gui_btn = self.gui_buttons[button_index]
            gui_btn.trigger()  # Triggers callback and visual lighting effect
    
    # Test callback methods
    def button_a_pressed(self, button):
        """Handle A button press"""
        _ = button  # Acknowledge parameter
        print("🅰️ Button A pressed!")
        
    def button_b_pressed(self, button): 
        """Handle B button press"""
        _ = button  # Acknowledge parameter
        print("🅱️ Button B pressed!")
        
    def button_x_pressed(self, button):
        """Handle X button press"""
        _ = button  # Acknowledge parameter
        print("❌ Button X pressed!")
        
    def button_y_pressed(self, button):
        """Handle Y button press"""
        _ = button  # Acknowledge parameter
        print("🎯 Button Y pressed!")

def test_display():
    """Non-async test function just like the hello world"""
    print('Simple demo: testing display.')
    Screen.change(BaseScreen)