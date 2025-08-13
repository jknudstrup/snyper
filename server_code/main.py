# main.py - Server main file with GUI integration
# Save this as main.py on your SERVER Pico W

from server.load_server import create_server, DEFAULT_CONFIG
import _thread
import time

def start_server_thread(server):
    """Start the server in a separate thread"""
    try:
        print("Starting server thread...")
        server.start()
    except Exception as e:
        print(f"Server thread error: {e}")

def main():
    """Main function for server Pico with GUI integration"""
    print("="*50)
    print("RASPBERRY PI PICO W - GUI INTEGRATED SERVER")
    print("="*50)
    
    # Create server with default configuration
    server = create_server(
        ssid=DEFAULT_CONFIG['ssid'],           # "PicoServer"
        password=DEFAULT_CONFIG['password'],   # "picopass123"  
        port=DEFAULT_CONFIG['port']            # 80
    )
    
    print("Server Features:")
    print("• GUI control interface")
    print("• Clients can connect and register themselves")
    print("• GUI buttons can send commands to clients")
    print("• Server API still available for direct access")
    print()
    
    # Start the server in a separate thread so GUI can run in main thread
    try:
        # Start server thread
        # server_thread = _thread.start_new_thread(start_server_thread, (server,))
        
        # # Give server time to start up
        # time.sleep(3)
        # print("Server thread started, waiting for setup to complete...")
        # time.sleep(2)
        
        server.start()
        # Import and start GUI (this should run in the main thread)
        # try:
        #     from hello_screen import demo_screen
        #     print("Starting GUI interface...")
        #     print("Note: GUI will be functional once clients register!")
            
        #     # Launch the GUI with server instance
        #     demo_screen(server)
            
        # except ImportError as e:
        #     print(f"GUI not available: {e}")
        #     print("Running in server-only mode...")
            
        #     # If GUI isn't available, just keep server running
        #     try:
        #         while True:
        #             time.sleep(10)
        #             # Optionally print status
        #             if hasattr(server, 'clients'):
        #                 client_count = len(server.clients)
        #                 if client_count > 0:
        #                     print(f"Active clients: {list(server.clients.keys())}")
        #     except KeyboardInterrupt:
        #         print("\nServer stopped by user")
        
    except Exception as e:
        print(f"Failed to start server: {e}")
        # Fallback: try to start server normally
        try:
            print("Trying fallback server start...")
            server.start()
        except Exception as e2:
            print(f"Fallback server start also failed: {e2}")

if __name__ == "__main__":
    main()