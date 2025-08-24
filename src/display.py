from gui.core.ugui import Screen, ssd
from gui.widgets import Label, Button, CloseButton
from gui.core.writer import CWriter
from gui.primitives.pushbutton import Pushbutton
import gui.fonts.font14 as font
from gui.core.colors import *
from machine import Pin

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
            {'label': 'A', 'row': 15, 'col': 208, 'callback': self.button_a_pressed},
            {'label': 'B', 'row': 75, 'col': 208, 'callback': self.button_b_pressed}, 
            {'label': 'X', 'row': 135, 'col': 208, 'callback': self.button_x_pressed},
            {'label': 'Y', 'row': 195, 'col': 208, 'callback': self.button_y_pressed}
        ]
        
        for config in button_configs:
            btn = Button(self.wri, 
                        row=config['row'], 
                        col=config['col'],
                        text=config['label'],
                        callback=config['callback'],
                        shape=CIRCLE,
                        height=25,
                        width=25,  
                        fgcolor=WHITE,
                        bgcolor=DARKBLUE,
                        litcolor=LIGHTGREEN)
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
            gui_btn.do_sel()  # Triggers callback and visual lighting effect
    
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