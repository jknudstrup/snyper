import network
import time
import urequests

class ClientHTTP:
    def __init__(self, ssid, password, server_ip):
        self.ssid = ssid
        self.password = password
        self.server_ip = server_ip

    def reset_network_interface(self):
        """Properly reset the network interface to handle soft resets"""
        wlan = network.WLAN(network.STA_IF)
        if wlan.active():
            try:
                wlan.disconnect()
                time.sleep(0.5)
            except:
                pass
            try:
                wlan.active(False)
                time.sleep(1)
            except:
                pass
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
        # wlan = network.WLAN(network.STA_IF)
        wlan = self.reset_network_interface()
        wlan.active(True)
        time.sleep(1)
        
        print(f'Connecting to {self.ssid}...')
        wlan.connect(self.ssid, self.password)
        
        max_wait = 20
        wait_count = 0
        while not wlan.isconnected() and wait_count < max_wait:
            if wlan.status() < 0:
                print(f"Wi-Fi connection failed with status: {wlan.status()}")
                raise RuntimeError("Wi-Fi connection failed")
            print(f"Waiting for connection... ({wait_count}/{max_wait})")
            time.sleep(1)
            wait_count += 1
            
        if not wlan.isconnected():
            raise RuntimeError("Wi-Fi connection timeout")
            
        print(f'Connected to {self.ssid}')
        print(f'IP: {wlan.ifconfig()[0]}')

        # url = f"http://{self.server_ip}/hello"
        url = f"http://{self.server_ip}/"
        try:
            print(f"Sending GET request to {url}")
            response = urequests.get(url)
            print("Response from server:")
            print(response.text)
            response.close()
        except Exception as e:
            print(f"Failed to send message: {e}")
