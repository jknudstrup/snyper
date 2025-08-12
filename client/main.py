from client.client_http import ClientHTTP
from config import config

def start():
    ssid = config.get("ssid")
    password = config.get("password")
    server_ip = config.get("server_ip")
    client = ClientHTTP(ssid, password, server_ip)
    client.start()

start()