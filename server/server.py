import socket
import logging
import threading

from server.client_registry import ClientRegistry
from server.client_handler import ClientHandler
from common.protocol import MsgType, ErrorCode
from common.errors import ConnectionClosed
logger = logging.getLogger(__name__)

class Server():
    def __init__(self, config):
        self.config = config
        self.registry = ClientRegistry()

    def start(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.config.host, self.config.port))
        self.server_sock.listen()
        logger.info(f"server is listening on {self.config.host}:{self.config.port}")

        while True:
            conn, addr = self.server_sock.accept()

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
            thread.start()
            logger.info(f"client {handler.client_id} connected form {addr}")

        
        