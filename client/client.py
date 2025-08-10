import socket
import time
import machine
import network

class Client:
    def __init__(self, ssid="PICO_AP", password="micropython123"):
        self.ssid = ssid
        self.password = password
        self.send_every = 5.0
        self.t_clock_started = 0
        
        self.s = None
        
    def reset_network_interface(self):
        """Properly reset the network interface to handle soft resets"""
        # Get the station interface
        wlan = network.WLAN(network.STA_IF)
        
        # Force disconnect and deactivate
        if wlan.active():
            try:
                wlan.disconnect()
                time.sleep(0.5)  # Give it time to disconnect
            except:
                pass
            
            try:
                wlan.active(False)
                time.sleep(1)  # Important: give it time to fully deactivate
            except:
                pass
        
        # Also ensure AP interface is off (in case it was used before)
        try:
            ap = network.WLAN(network.AP_IF)
            if ap.active():
                ap.active(False)
                time.sleep(0.5)
        except:
            pass
            
        print("Network interfaces reset")
        return wlan
        
    def start(self):
        # Clean up any existing socket first
        if self.s is not None:
            try:
                self.s.close()
            except:
                pass
            self.s = None

        # Reset network interface to handle soft reset issues
        wlan = self.reset_network_interface()
        
        # Now activate and connect
        wlan.active(True)
        time.sleep(1)  # Give it time to activate
        
        print(f'Connecting to {self.ssid}...')
        wlan.connect(self.ssid, self.password)
        
        # Wait for connection with timeout
        max_wait = 20  # 20 second timeout
        wait_count = 0
        while not wlan.isconnected() and wait_count < max_wait:
            if wlan.status() < 0:  # error
                print(f"Wi-Fi connection failed with status: {wlan.status()}")
                raise RuntimeError("Wi-Fi connection failed")
            print(f"Waiting for connection... ({wait_count}/{max_wait})")
            time.sleep(1)
            wait_count += 1
            
        if not wlan.isconnected():
            print("Connection timeout - trying machine.reset()")
            # As a last resort, do a hard reset
            machine.reset()
            
        print(f'Connected to {self.ssid}')
        print(f'IP: {wlan.ifconfig()[0]}')

        # Now try to connect to server
        server_ip = "192.168.4.1"  # AP's default IP
        addr = socket.getaddrinfo(server_ip, 5000)[0][-1]
        s = socket.socket()
        
        s.settimeout(5.0)  # Increased timeout
        print(f'Attempting to connect to {server_ip}')
        
        try:
            s.connect(addr)
            self.s = s
            print("Connected to socket")
            self.t_clock_started = time.time()
            s.send(b"Hello from client!")
            
            # For this simple example, close after sending
            s.close()
            self.s = None
            print("Message sent successfully")
            
        except OSError as e:
            print(f"Socket connection failed: {e}")
            if s:
                try:
                    s.close()
                except:
                    pass
            # If socket connection fails after network is up, 
            # it might be a deeper issue requiring hard reset
            print("Socket connection failed - trying machine.reset()")
            machine.reset()

    def sayHowdy(self):
        if self.s is not None:
            self.s.send(b"Howdy")
        else:
            print("No active socket connection")
            
    def cleanup(self):
        """Call this before soft reset or when done"""
        if self.s is not None:
            try:
                self.s.close()
            except:
                pass
            self.s = None
            
        # Also clean up network interface
        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.disconnect()
            wlan.active(False)
        except:
            pass