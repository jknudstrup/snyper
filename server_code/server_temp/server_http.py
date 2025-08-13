import network
import time
from server.microserver.micropyserver import MicroPyServer
from server.microserver import utils


class ServerHTTP:
    def __init__(self, ssid="PICO_AP_2", password="micropython123"):
        self.ssid = ssid
        self.password = password
        self.server = MicroPyServer()


    def start(self):
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=self.ssid, password=self.password)

        while not ap.active():
            time.sleep(0.1)

        print(f"AP up at {ap.ifconfig()[0]}")

        self.server.add_route('/', self.hello)
        self.server.add_route('/hello', self.hello)
        self.server.start()

def hello(self, request):
    # def hello(self):
        print(request)
        self.server.send("Hello from the other side!")
    
