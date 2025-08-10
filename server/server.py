import socket
import time

import network

class Timer:
    
    def __init__(self, timeout, callback):
        self.timeout = timeout
        self.callback = callback
        self.t_started = 0
    
    def start(self):
        self.t_started = time.time()
    
    def check(self):
        dt = time.time() - self.t_started
        if dt >= self.timeout:
            self.callback()
            self.t_started = time.time()
        
def timer_callback():
    print("timer fired")

def do_socket_thing(sock, fn, timeout=1, max_attempts=1, sleep_interval=0.05):

    if timeout is not None:
        sock.settimeout(timeout)
    attempt = 0
    if attempt < max_attempts:
        try:
            result = fn()
            return {
                "success": True,
                "result": result,
                }
        except OSError:
            attempt += 1
            time.sleep(sleep_interval)
            
    return {
        "success": False,
        "result": None,
    }
        

class Server:

    def __init__(self, ssid="PICO_AP", password = "micropython123"):
        self.ssid = ssid
        self.password = password

    def start(self):
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=self.ssid, password=self.password)
        # Wait for AP to be active
        while not ap.active():
            time.sleep(0.1)

        ip, _, _, _ = ap.ifconfig()
        print("AP up at", ip)  # typically 192.168.4.1

        addr = socket.getaddrinfo("0.0.0.0", 5000)[0][-1]
        srv = socket.socket()
        srv.bind(addr)
        srv.listen(1)
        print("Listening on", addr)
        srv.settimeout(1.0)
        
        loop_num = -1
        sleep_interval = 0.05
        while True:
            loop_num += 1
            # print("loop_num", str(loop_num))
            conn = None
            try:
                conn, client_address = srv.accept()
                conn.settimeout(1.0)
                
                try:
                    data = conn.recv(1024)
                    if data:
                        print("Server: Got", data, "from", client_address)
                        # Optionally send a response:
                        # conn.send(b"Message received, brother")
                    else:
                        print("got empty data")
                        
                except OSError:
                    print("conn.recv timed out")
                    
            except OSError:
                # srv.accept() timed out, continue to next iteration
                pass
            finally:
                # Always close the connection if it was created
                if conn is not None:
                    try:
                        conn.close()
                    except:
                        pass
                        
            time.sleep(sleep_interval)