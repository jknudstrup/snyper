from micropyserver import MicroPyServer

''' there should be a wi-fi connection code here '''

def hello_world(request):
    ''' request handler '''
    server.send("HELLO WORLD!")

server = MicroPyServer()
''' add route '''
server.add_route("/", hello_world)
''' start server '''
server.start()