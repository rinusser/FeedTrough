import http.server
import socketserver
import threading


class SilentRequestHandler(http.server.SimpleHTTPRequestHandler):
  """HTTP request handler implementation that has been muted.
  """

  def log_message(self, format, *args):
    """logging function, silently discards all messages.

    Automatically called from TCPServer.
    """
    pass


class Server(threading.Thread):
  """HTTP server, serving file system contents starting at the current working directory.

  This extends threading.Thread, so usually you'll want to call the inherited .start() method.
  """

  port=58050   #: the TCP port to listen on
  _socket=None

  def __init__(self):
    super().__init__(daemon=True)

  def run(self):
    """Main worker method, call only if you want the server in the foreground.

    You'll probably want to call .start() instead.
    """
    self._socket=socketserver.TCPServer(("127.0.0.1",self.port),SilentRequestHandler)
    self._socket.serve_forever()

