import logging
import threading
import uuid
from enum import Enum

from common.errors import ConnectionClosed, SafeRoomError
from common.framing import recv_frame, send_frame
from common.protocol import MsgType, decode_message, encode_message

logger = logging.getLogger(__name__)

class ClientState(Enum):
    CONNECTED = "connected"
    READY = "ready" 
    CLOSED = "closed"

class ClientHandler:
    def __init__(self, sock, addr, registry, config):
        self.sock = sock
        self.addr = addr
        self.registry = registry
        self.config = config
        self.client_id = uuid.uuid4().hex[:8]
        self.state = ClientState.CONNECTED 
        self._send_lock = threading.Lock()


    def send(self, msg_type: MsgType, data) -> None:
        mtype, message = encode_message(msg_type, data)
        with self._send_lock:
            send_frame(self.sock, mtype, message)

    def run(self):
        try:
            while self.state != ClientState.CLOSED:
                msg_type, payload = recv_frame(self.sock, self.config.max_frame_size)
                msg_type, data = decode_message(msg_type, payload)
                self.handle_message(msg_type, data)
        except ConnectionClosed:
            logger.info(f"client {self.client_id} disconnected")

        except SafeRoomError as e:
            logger.warning(f"client {self.client_id} sent bad data: {e}")

        finally:
            self.state = ClientState.CLOSED
            self.registry.remove(self.client_id)
            self.sock.close()
            logger.info(f"client {self.client_id} cleaned up")
        

      
    def handle_message(self, mtype, data):

        logger.info(f"received {mtype.name} from {self.client_id}") 