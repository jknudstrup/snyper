import network
import time
from micropyserver import MicroPyServer

class Server:

    def __init__(self, ssid="PICO_AP", password="micropython123"):
        self.ssid = ssid
        self.password = password
        self.server = MicroPyServer()

    def start(self):
        # Start the access point
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=self.ssid, password=self.password)
        while not ap.active():
            time.sleep(0.1)
        print("AP up at", ap.ifconfig()[0])

        # Define a handler for the root path
        def handle_root(request):
            print("Received request:", request)
            self.server.send("HTTP/1.0 200 OK")
            self.server.send("Content-Type: text/plain")
            self.server.send("Hello from the Pico!")

        # Add the route
        self.server.add_route("/", handle_root)

        # Start the server
        self.server.start()

def start_server():
    server = Server()
    server.start()
