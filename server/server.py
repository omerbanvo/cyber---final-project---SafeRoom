import socket
import logging
import threading

from server.client_registry import ClientRegistry
from server.client_handler import ClientHandler
from common.protocol import MsgType, ErrorCode
from common.errors import ConnectionClosed
logger = logging.getLogger(__name__)


SHUTDOWN_JOIN_TIMEOUT = 2.0   # seconds to wait for each client thread on shutdown
ACCEPT_TIMEOUT = 1.0          # accept() wakes up this often, so Ctrl+C works on Windows


class Server():
    def __init__(self, config):
        self.config = config
        self.registry = ClientRegistry()

    def start(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.config.host, self.config.port))
        self.server_sock.listen()
        self.server_sock.settimeout(ACCEPT_TIMEOUT)

        logger.info(f"server is listening on {self.config.host}:{self.config.port}")

        while True:
            try:
                conn, addr = self.server_sock.accept()
            except TimeoutError:
                continue

            handler = ClientHandler(conn, addr, self.registry, self.config)
            if not self.registry.add(handler.client_id, handler, self.config.max_clients):
                try:
                    handler.send(MsgType.ERROR, {
                        "code": ErrorCode.SERVER_FULL, 
                        "message": "server is full"
                    })
                except ConnectionClosed:
                    pass
                conn.close()
                logger.warning(f"rejected {addr}: server is full")
                continue

            thread = threading.Thread(
                target= handler.run, 
                name= f"client- {handler.client_id}" , 
                daemon= True
            )
            handler.thread = thread

            logger.info(f"client {handler.client_id} connected form {addr}")
            thread.start()

    def stop(self):
        self.server_sock.close()
        handlers = self.registry.snapshot()
        for handler in handlers:
            handler.shutdown()
        for handler in handlers:
            handler.thread.join(timeout=SHUTDOWN_JOIN_TIMEOUT)
        logger.info("server stopped")
    
        
        