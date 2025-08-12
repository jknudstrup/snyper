import network
import time
import socket

class ClientHTTP:
    def __init__(self, ssid="PICO_AP", password="micropython123"):
        self.ssid = ssid
        self.password = password
        self.server_ip = "192.168.4.1"
        self.wlan = network.WLAN(network.STA_IF)

    def connect_wifi(self):
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print(f"Connecting to network {self.ssid}...")
            self.wlan.connect(self.ssid, self.password)
            while not self.wlan.isconnected():
                time.sleep(1)
        print("Connected to Wi-Fi")
        print(f"IP Address: {self.wlan.ifconfig()[0]}")

    def send_test_message(self):
        time.sleep(5) # Give server time to start
        addr = socket.getaddrinfo(self.server_ip, 80)[0][-1]
        s = socket.socket()
        s.connect(addr)
        print(f"Sending GET request to http://{self.server_ip}/hello")
        s.send(b"GET /hello HTTP/1.0\r\n\r\n")
        data = s.recv(1000)
        print("Response from server:")
        print(data.decode())
        s.close()

    def start(self):
        self.connect_wifi()
        self.send_test_message()

def start_client():
    print("Running HTTP client")
    client = ClientHTTP()
    client.start()
