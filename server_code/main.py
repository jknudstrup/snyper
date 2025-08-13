# main.py - Server main file
# Save this as main.py on your SERVER Pico W

from server.load_server import create_server, DEFAULT_CONFIG

from config import config

def main():
    """Main function for server Pico"""
    print("="*50)
    print("RASPBERRY PI PICO W - SERVER")
    print("="*50)
    
    ssid = config.get('ssid')
    password = config.get('password')
    port = config.get('port')
    
    # Create server with default configuration
    # You can customize these values:
    server = create_server(
        ssid,           # "PicoServer"
        password,   # "picopass123"  
        port # 80
    )
    
    # Alternative: Create with custom settings
    # server = create_server(
    #     ssid="MyCustomPico",
    #     password="mypassword123",
    #     port=8080
    # )
    
    # Start the server (this will block until stopped)
    try:
        server.start()
    except Exception as e:
        print(f"Failed to start server: {e}")

if __name__ == "__main__":
    main()