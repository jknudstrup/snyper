from gui.core.ugui import Screen, ssd, Widget, display
from gui.widgets import Label, Button, CloseButton
from gui.core.writer import CWriter
from gui.primitives.pushbutton import Pushbutton
import gui.fonts.font14 as font
import gui.fonts.icons as icons
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
    """Configurable physical button overlay with GUI buttons on right side of screen"""
    
    def __init__(self, wri, button_config=None):
        """
        Initialize physical button overlay with configurable GUI buttons
        
        Args:
            wri: Text writer for regular fonts
            button_config: Dict configuring which GUI buttons to show:
                {
                    'A': {'visible': True, 'icon': 'D', 'color': RED, 'callback': self.method},
                    'B': {'visible': False},
                    'X': {'visible': True, 'icon': 'E', 'color': BLUE, 'callback': self.method},
                    'Y': {'visible': True, 'icon': 'F', 'color': GREEN, 'callback': self.method}
                }
        """
        # Initialize physical buttons from hardware_setup.py
        self.keyA = Pushbutton(Pin(15, Pin.IN, Pin.PULL_UP))  # Back/Cancel button
        self.keyB = Pushbutton(Pin(17, Pin.IN, Pin.PULL_UP))  # Skip button
        self.keyX = Pushbutton(Pin(19, Pin.IN, Pin.PULL_UP))  # New button
        # self.keyY = Pushbutton(Pin(21, Pin.IN, Pin.PULL_UP))  # Now handled by GUI as 'sel'
        
        # Create icon writer for button icons
        self.wri_icons = CWriter(ssd, icons, WHITE, BLACK, verbose=False)
        
        # Store button configuration (empty dict if none provided)
        self.button_config = button_config or {}
        
        # Create GUI buttons positioned on screen
        self.gui_buttons = []
        self.setup_gui_buttons()
        self.bind_physical_to_gui()
        
        print(f"🎮 Physical button overlay initialized with {len(self.gui_buttons)} buttons!")
    
    def setup_gui_buttons(self):
        """Create circular GUI buttons for each configured button"""
        positions = {'A': 15, 'B': 75, 'X': 135, 'Y': 195}  # Row positions for each button
        
        # Only create buttons that are explicitly configured
        for button_name, config in self.button_config.items():
            if button_name in positions:
                row = positions[button_name]
                btn = PassiveButton(
                    self.wri_icons,
                    row=row,
                    col=208,
                    text=config.get('icon', button_name),  # Default to button name if no icon specified
                    callback=config.get('callback', lambda button: None),
                    shape=CIRCLE,
                    height=25,
                    width=25,
                    fgcolor=WHITE,
                    bgcolor=config.get('color', GREY),
                    litcolor=None  # No color change feedback
                )
                self.gui_buttons.append({'name': button_name, 'button': btn})
        
        print(f"📱 Created {len(self.gui_buttons)} configured GUI buttons")
    
    def bind_physical_to_gui(self):
        """Bind physical button presses to trigger GUI button actions"""
        # Only bind A button if it's configured (use release_func for single trigger)
        if 'A' in self.button_config:
            self.keyA.release_func(self.back_button_pressed)  # A = Back/Cancel (when configured)
        self.keyB.release_func(self.trigger_physical_button, ('B',))
        self.keyX.release_func(self.trigger_physical_button, ('X',))  
        # Y button now handled by GUI navigation system as 'sel'
        
        print("🔗 Physical buttons bound: A=Back (if configured), B/X=Configurable, Y=Sel")
    
    def trigger_physical_button(self, button_name):
        """Handle physical button press with optional visual feedback"""
        # Check if button is configured (only configured buttons exist now)
        if button_name not in self.button_config:
            print(f"🚫 Physical button {button_name} press ignored (button not configured)")
            return
        
        # Find GUI button for this physical button
        gui_button_info = next((item for item in self.gui_buttons if item['name'] == button_name), None)
        
        if gui_button_info:
            # Trigger visual feedback and callback
            gui_button_info['button'].trigger()
        else:
            # This shouldn't happen since we only create buttons for configured items
            print(f"⚠️ Warning: Button {button_name} configured but no GUI button found")
    
    def back_button_pressed(self):
        """Handle A button as back/cancel button like CloseButton"""
        # Trigger visual feedback on A button if visible
        a_button_info = next((item for item in self.gui_buttons if item['name'] == 'A'), None)
        if a_button_info:
            a_button_info['button'].trigger()  # Visual feedback
        
        # Navigate back like CloseButton does
        Screen.back()
        print("⬅️ Back button pressed - navigating back")
    
    # Visual callback methods (for GUI button feedback only)
    def button_a_pressed(self, button):
        """Visual feedback for A button (actual back functionality in back_button_pressed)"""
        _ = button  # Acknowledge parameter
        # Visual feedback only - back functionality handled by back_button_pressed()
        
    def button_b_pressed(self, button): 
        """Handle B button press"""
        _ = button  # Acknowledge parameter
        print("🅱️ Skip button pressed!")
        
    def button_x_pressed(self, button):
        """Handle X button press"""
        _ = button  # Acknowledge parameter
        print("❌ New button pressed!")
        
    def button_y_pressed(self, button):
        """Visual feedback for Y button (actual select functionality handled by GUI system)"""
        _ = button  # Acknowledge parameter
        # Visual feedback only - select functionality handled by GUI navigation

def test_display():
    """Non-async test function just like the hello world"""
    print('Simple demo: testing display.')
    Screen.change(BaseScreen)