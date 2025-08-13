# hello_screen.py - GUI Screen integrated with bidirectional server

import hardware_setup # Create a display instance
from gui.core.ugui import Screen, ssd

from gui.widgets import Label, Button, CloseButton
# from gui.core.writer import Writer  # Monochrome display
from gui.core.writer import CWriter
# Font for CWriter or Writer
import gui.fonts.font10 as font
from gui.core.colors import *



class BaseScreen(Screen):

    def __init__(self, server_instance=None):
        """Initialize the screen with optional server instance
        
        Args:
            server_instance: The PicoServer instance for sending commands
        """
        self.server_instance = server_instance
        
        def yes_callback(button, arg):
            """Handle Yes button press - send ping to client_1"""
            print(f'Button pressed: {arg}')
            
            if self.server_instance:
                # Send ping command to client_1
                client_id = 'pico_client_1'
                
                if client_id in self.server_instance.clients:
                    print(f"Sending ping to {client_id}...")
                    
                    # Send a simple ping command
                    ping_command = 'print("Ping received from server GUI!")'
                    client_info = self.server_instance.clients[client_id]
                    
                    success, result = self.server_instance._send_client_request(
                        client_info, 
                        "/execute", 
                        {
                            "command": ping_command,
                            "sender": "server_gui"
                        }
                    )
                    
                    if success:
                        print(f"✓ Ping sent successfully to {client_id}")
                        print(f"Response: {result}")
                        
                        # Update GUI to show success (optional)
                        self.update_status(f"Pinged {client_id} ✓")
                    else:
                        print(f"✗ Failed to ping {client_id}: {result}")
                        self.update_status(f"Ping failed ✗")
                else:
                    print(f"Client {client_id} not found or not registered")
                    available_clients = list(self.server_instance.clients.keys())
                    print(f"Available clients: {available_clients}")
                    self.update_status(f"Client not found")
            else:
                print("No server instance available")
                self.update_status("No server")

        def no_callback(button, arg):
            """Handle No button press"""
            print(f'Button pressed: {arg}')
            self.update_status("No pressed")

        super().__init__()
        # wri = Writer(ssd, arial10, verbose=False)  # Monochrome display
        wri = CWriter(ssd, font, GREEN, BLACK, verbose=False)

        col = 2
        row = 2
        Label(wri, row, col, 'Server Control')
        
        row = 50
        Button(wri, row, col, text='Ping Client', callback=yes_callback, args=('Ping',))
        col += 100
        Button(wri, row, col, text='No', callback=no_callback, args=('No',))
        
        # Status label to show results
        row = 90
        col = 2
        self.status_label = Label(wri, row, col, 'Ready...')
        
        CloseButton(wri)  # Quit the application
    
    def update_status(self, message):
        """Update the status label with a message"""
        try:
            # This might need adjustment based on your GUI library's capabilities
            print(f"Status: {message}")
            # If the GUI supports dynamic label updates, do it here
            # self.status_label.value(message)
        except Exception as e:
            print(f"Could not update GUI status: {e}")


def demo_screen(server_instance=None):
    """Launch the demo screen with server integration
    
    Args:
        server_instance: The PicoServer instance for sending commands
    """
    print('Server Control GUI: Use buttons to interact with clients.')
    if server_instance:
        print(f'Connected clients: {list(server_instance.clients.keys())}')
    else:
        print('Warning: No server instance provided - buttons will not send commands')
    
    # Pass the server instance to the screen
    Screen.change(BaseScreen)  # Pass server instance
    # Screen.change(BaseScreen, server_instance)  # Pass server instance


# Alternative factory function for easier integration
def create_server_control_screen(server_instance):
    """Create a server control screen with the given server instance
    
    Args:
        server_instance: The PicoServer instance
        
    Returns:
        function: A demo_screen function pre-configured with the server
    """
    def configured_demo_screen():
        return demo_screen(server_instance)
    
    return configured_demo_screen