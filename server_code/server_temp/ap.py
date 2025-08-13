import network
import time

def start_ap(ssid, password):
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=ssid, password=password)

        while not ap.active():
            time.sleep(0.1)

        print(f"AP {ssid} up at {ap.ifconfig()[0]}")