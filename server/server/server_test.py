import network
import time
from .micropyserver import MicroPyServer

def start_server(ssid="PICO_AP", password="micropython123"):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password)

    while not ap.active():
        time.sleep(0.1)

    print(f"AP up at {ap.ifconfig()[0]}")

    server = MicroPyServer()

    def index(request):
        server.send("HTTP/1.0 200 OK\r\n")
        server.send("Content-Type: text/html\r\n\r\n")
        server.send("<h1>Hello, World!</h1>")

    def hello(request):
        server.send("HTTP/1.0 200 OK\r\n")
        server.send("Content-Type: text/plain\r\n\r\n")
        server.send("Hello from the other side!")

    server.add_route('/', index)
    server.add_route('/hello', hello)

    server.start()

