import logging
import threading
import uuid
from enum import Enum

from common.errors import ConnectionClosed, SafeRoomError
from common.framing import recv_frame, send_frame
from common.protocol import MsgType, decode_message, encode_message, ErrorCode, PROTOCOL_VERSION

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
    def send_error(self, code, message, req_id=None )-> None: 
        data = {"code": code, "message": message}
        if req_id is not None: 
            data["req_id"]= req_id
        self.send(msg_type= MsgType.ERROR, data=data)

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
        
    def _handle_hello(self, data):
        req_id = data["req_id"]
        if self.state == ClientState.READY :
            self.send_error(ErrorCode.BAD_MESSAGE, "already said HELLO", req_id)
            return
        if data["version"] != PROTOCOL_VERSION :
            self.send_error(ErrorCode.BAD_VERSION,
                            f"unsupported version {data['version']}, expected {PROTOCOL_VERSION}",
                            req_id)
            self.state = ClientState.CLOSED
            return
        
        self.state = ClientState.READY
        self.send(MsgType.WELCOME, {"req_id": req_id, "client_id": self.client_id})
        logger.info(f"client {self.client_id} is READY")


    def _handle_ping(self, data):
        req_id = data["req_id"]
        self.send(MsgType.PONG, {"req_id":req_id})

    def _handle_bye(self, data):
        logger.info(f"client {self.client_id} said bye")
        self.state = ClientState.CLOSED

    def _handle_broadcast(self, data):
        message = {"from": self.client_id, "text": data["text"]}
        clients = self.registry.snapshot()
        count = 0
        for other in clients:
            if other is self:
                continue
            if other.state != ClientState.READY:
                continue
            try:
                other.send(MsgType.BROADCAST_TEST, message)
                count += 1
            except ConnectionClosed as e:
                logger.warning(f"broadcast to {other.client_id} failed: {e}")
        logger.info(f"broadcast from {self.client_id} sent to {count} clients")
    def handle_message(self, mtype, data):

        logger.info(f"received {mtype.name} from {self.client_id}") 
        if self.state == ClientState.CONNECTED and mtype != MsgType.HELLO:
            self.send_error(ErrorCode.NOT_READY, 
                            "send HELLO first", 
                            data.get("req_id")
                            )
            return
        
        if mtype == MsgType.HELLO: 
            self._handle_hello(data)
        elif mtype == MsgType.PING:
            self._handle_ping(data)
        elif mtype == MsgType.BYE:
            self._handle_bye(data)
        elif mtype == MsgType.PONG:
            pass
        elif mtype == MsgType.BROADCAST_TEST:
            self._handle_broadcast(data)
        else:
            self.send_error(
                ErrorCode.BAD_MESSAGE,
                f"unexpected message {mtype.name}",
                data.get("req_id"),
            )
