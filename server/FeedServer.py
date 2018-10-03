import http.server
import io
import socketserver
import threading

import logger
from server import *
from storage import *


log=logger.get_logger(__name__)


class FeedHandler(http.server.BaseHTTPRequestHandler):
  def log_message(self, format, *args):
    pass

  def do_GET(self):
    if not self.path.startswith("/feed/"):
      return self._send404("only /feed/<id> is implemented")

    id_str=self.path[6:].split("/")[0]
    if not id_str.isdecimal():
      return self._send400("need to pass id in URL")

    id=int(id_str)

    feed=self.server.storage.getFeedByID(id)
    if feed==None:
      return self._send404("feed with ID %d not found"%id)

    xml=self.server.renderer.renderFeed(feed)
    body=xml.encode()

    self.send_response(http.server.HTTPStatus.OK)
    self.send_header("Content-Type","application/rss+xml")
    self.send_header("Content-Length",len(body))
    self.end_headers()
    self.wfile.write(body)

  def _send400(self, message:str):
    self._sendTextResponse(http.server.HTTPStatus.BAD_REQUEST,message)

  def _send404(self, message:str):
    self._sendTextResponse(http.server.HTTPStatus.NOT_FOUND,message)

  def _sendTextResponse(self, status, message:str):
    self.send_response(status)
    body=message.encode()
    self.send_header("Content-Type","text/plain")
    self.send_header("Content-Length",len(body))
    self.end_headers()
    self.wfile.write(body)


class TCPServer(socketserver.TCPServer):
  storage=None
  renderer=None


class FeedServer(threading.Thread):
  port=58000
  _socket=None
  storage=None
  renderer=None

  def __init__(self, storage:Storage):
    super().__init__(daemon=True)
    self.storage=storage
    self.renderer=XMLRenderer()

  def run(self):
    self._socket=TCPServer(("127.0.0.1",self.port),FeedHandler)
    self._socket.storage=self.storage
    self._socket.renderer=self.renderer
    log.info("listening on port %d",self.port)
    self._socket.serve_forever()
