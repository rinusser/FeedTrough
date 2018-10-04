import http.server
import io
import socketserver
import threading

import logger
from server import *
from storage import *


log=logger.get_logger(__name__)


class FeedHandler(http.server.BaseHTTPRequestHandler):
  """HTTP request handler implementation serving stored feeds as RSS 2.0 XML.
  """

  def log_message(self, format, *args):
    """logging callback, silently discards messages.
    """
    pass

  def do_GET(self):
    """callback for HTTP GET requests, serves feeds and denies everything else.
    """
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
  """Utility class, contains references to Storage and Renderer implementations for handlers.
  """
  storage=None  #: the storage to use, as storage.Storage
  renderer=None #: the renderer to use, usually XMLRenderer


class FeedServer(threading.Thread):
  """The HTTP server for feeds.

  This class extends threading.Thread: call start() to spawn it in the background.
  """

  port=58000    #: the TCP port to listen on
  _socket=None
  storage=None  #: the storage handler to use, will be initialized by the constructor
  renderer=None #: the XML renderer to use, will be initialized by the constructor

  def __init__(self, storage:Storage):
    """
    :param Storage storage: the storage handler to read feeds from
    """
    super().__init__(daemon=True)
    self.storage=storage
    self.renderer=XMLRenderer()

  def run(self):
    """main worker method for the server

    You'll probably want to call .start() instead.
    """
    self._socket=TCPServer(("127.0.0.1",self.port),FeedHandler)
    self._socket.storage=self.storage
    self._socket.renderer=self.renderer
    log.info("listening on port %d",self.port)
    self._socket.serve_forever()
