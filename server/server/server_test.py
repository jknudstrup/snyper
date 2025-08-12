import network
import time
from server.microserver.micropyserver import MicroPyServer
from server.microserver import utils


def test_server():
    server = MicroPyServer()


    def index(request):
        server.send('OK')

    def hello_world(request):
        ''' request handler '''
        server.send("HELLO WORLD!")


    def stop(request):
        server.stop()


    def set_cookies(request):
        cookies_header = utils.create_cookie("name", "value", expires="Sat, 01-Jan-2030 00:00:00 GMT")
        utils.send_response(server, "OK", extend_headers=[cookies_header])


    def get_cookies(request):
        cookies = utils.get_cookies(request)
        utils.send_response(server, str(cookies))


    server.add_route("/", index)
    server.add_route("/hello", hello_world)
    server.add_route("/stop", stop)
    server.add_route("/set_cookies", set_cookies)
    server.add_route("/get_cookies", get_cookies)

    server.start()
    
