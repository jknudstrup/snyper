# from server.server_http import ServerHTTP

# def start():
#     server = ServerHTTP()
#     server.start()

# start()
from config import config
from server.ap import start_ap
from server.server_test import test_server

ssid = config.get("ssid")
password = config.get("password")

start_ap(ssid, password)
test_server()

