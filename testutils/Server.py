import http.server
import socketserver
import threading


class SilentRequestHandler(http.server.SimpleHTTPRequestHandler):
  def log_message(self, format, *args):
    pass


class Server(threading.Thread):
  port=58050
  _socket=None

  def __init__(self):
    super().__init__(daemon=True)

  def run(self):
    self._socket=socketserver.TCPServer(("127.0.0.1",self.port),SilentRequestHandler)
#    print("listening on port %d"%self.port)
    self._socket.serve_forever()

