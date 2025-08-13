# main.py - Client main file  
# Save this as main.py on your CLIENT Pico W

from client.load_client import create_client, DEFAULT_CONFIG
import time

def main():
    """Main function for client Pico"""
    print("="*50)
    print("RASPBERRY PI PICO W - BIDIRECTIONAL CLIENT")
    print("="*50)
    
    # Create client with default configuration
    # IMPORTANT: Each client needs a unique client_id and client_port!
    client = create_client(
        client_id="pico_client_1",                    # Change this for each client!
        ssid=DEFAULT_CONFIG['ssid'],                  # "PicoServer"
        password=DEFAULT_CONFIG['password'],          # "picopass123"
        server_ip=DEFAULT_CONFIG['server_ip'],        # "192.168.4.1"
        server_port=DEFAULT_CONFIG['server_port'],    # 80
        client_port=8080                              # Change this for each client! (8081, 8082, etc.)
    )
    
    # Alternative: Create with custom settings for multiple clients
    # Client 2 example:
    # client = create_client(
    #     client_id="pico_client_2", 
    #     client_port=8081,
    #     ssid="PicoServer",
    #     password="picopass123"
    # )
    
    try:
        # Run the complete setup process
        success = client.run_full_setup()
        
        if success:
            print("\n" + "="*50)
            print("CLIENT IS NOW READY!")
            print("The server can now send commands to this client using:")
            print(f"  GET /send-command/{client.client_id}?cmd=print('Hello Client!')")
            print("Or broadcast to all clients with:")
            print("  GET /broadcast?cmd=print('Hello Everyone!')")
            print("\nClient will continue running to receive commands...")
            print("Press Ctrl+C to stop")
            
            # Keep the client running to receive commands
            while True:
                time.sleep(10)  # Heartbeat every 10 seconds
                
                # Optional: Send periodic status update to server
                if client.registered:
                    # You could add a heartbeat endpoint here
                    pass
        
    except KeyboardInterrupt:
        print("\nClient stopped by user")
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        # Clean up
        client.disconnect()
        print("Client finished")

if __name__ == "__main__":
    main()
    # Create client with default configuration
    # These should match your server settings:
    client = create_client(
        ssid=DEFAULT_CONFIG['ssid'],           # "PicoServer"
        password=DEFAULT_CONFIG['password'],   # "picopass123"
        server_ip=DEFAULT_CONFIG['server_ip'], # "192.168.4.1"
        server_port=DEFAULT_CONFIG['server_port'] # 80
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