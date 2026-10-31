import socket as s
import threading

from common.errors import ConnectionClosed, SafeRoomError
from common.framing import recv_frame, send_frame
from common.protocol import PROTOCOL_VERSION, MsgType, decode_message, encode_message
from common.config import ServerConfig

class Connection:
    def __init__(self, config, on_message, on_disconnect):
        self.config = config
        self.on_message = on_message
        self.on_disconnect = on_disconnect
        self.sock = None
        self._send_lock = threading.Lock()
        self._next_req_id = 1

    def send(self, msg_type, data):
        with self._send_lock:
            req_id = self._next_req_id
            self._next_req_id += 1
            data["req_id"] = req_id
            mtype, payload = encode_message(msg_type, data)
            send_frame(self.sock, mtype, payload)
        return req_id

    def connect(self):
        self.sock = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.sock.connect((self.config.host, self.config.port))
        thread = threading.Thread(
            target= self._receive_loop,
            name= "reciever", 
            daemon= True
        )
        thread.start()
        self.send(MsgType.HELLO, {"version": PROTOCOL_VERSION})

    def _receive_loop(self):
        try:
            while True:
                mtype, payload = recv_frame(self.sock, self.config.max_frame_size)
                mtype, data = decode_message(msg_type= mtype, payload= payload)
                self.on_message(mtype, data)
        except ConnectionClosed:
            self.on_disconnect("server closed the connection")
        except SafeRoomError as e:
            self.on_disconnect(f"bad data from server: {e}")


    def close(self):
        try:
            self.send(MsgType.BYE, {})
        except ConnectionClosed:
            pass
        self.sock.close()