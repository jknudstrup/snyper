# main.py - Client main file  
# Save this as main.py on your CLIENT Pico W

from client.load_client import create_client, DEFAULT_CONFIG

from config import config

def main():
    """Main function for client Pico"""
    print("="*50)
    print("RASPBERRY PI PICO W - CLIENT")
    print("="*50)
    
    ssid = config.get('ssid')
    password = config.get('password')
    server_ip = config.get('server_ip')
    port = config.get('port')
    # Create client with default configuration
    # These should match your server settings:
    client = create_client(
        ssid,           # "PicoServer"
        password,   # "picopass123"
        server_ip, # "192.168.4.1"
        port # 80
    )
    
    # Alternative: Create with custom settings
    # client = create_client(
    #     ssid="MyCustomPico",
    #     password="mypassword123", 
    #     server_ip="192.168.4.1",
    #     server_port=8080
    # )
    
    try:
        # Run the basic test sequence
        success = client.run_basic_test()
        
        if success:
            print("\n" + "="*50)
            print("You can also use the client manually:")
            print("  client.connect_to_wifi()")
            print("  client.send_hello_request()")
            print("  client.get_server_status()")
            print("  client.disconnect()")
            
            # Example of manual usage:
            # if not client.connected:
            #     client.connect_to_wifi()
            # 
            # # Send multiple requests
            # for i in range(3):
            #     print(f"\n--- Request {i+1} ---")
            #     client.send_hello_request()
            #     time.sleep(2)
        
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        # Clean up
        client.disconnect()
        print("\nClient finished")

if __name__ == "__main__":
    main()