import socket

from common.config import load_config
from common.errors import ConnectionClosed
from common.framing import recv_frame, send_frame
from common.protocol import MsgType, decode_message, encode_message

config = load_config()


def connect():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((config.host, config.port))
    return sock


def send(sock, mtype, data):
    send_frame(sock, *encode_message(mtype, data))


def recv(sock):
    return decode_message(*recv_frame(sock, config.max_frame_size))


# Test 1: PING before HELLO
sock = connect()
send(sock, MsgType.PING, {"req_id": 1})
print("PING before HELLO:", recv(sock))
sock.close()

# Test 2: HELLO with version 99
sock = connect()
send(sock, MsgType.HELLO, {"version": 99, "req_id": 1})
print("HELLO v99:", recv(sock))
try:
    recv(sock)
    print("connection still open (BAD)")
except ConnectionClosed:
    print("server closed the connection (GOOD)")
sock.close()