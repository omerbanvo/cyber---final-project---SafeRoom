import socket
import struct

from common.config import load_config
from common.framing import send_frame
config = load_config()


def connect():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((config.host, config.port))
    return sock


def wait_for_close(sock, name):
    sock.settimeout(15)
    try:
        data = sock.recv(1024)
        if data == b"":
            print(f"{name}: server closed the connection (GOOD)")
        else:
            print(f"{name}: server sent {data!r}")
    except socket.timeout:
        print(f"{name}: server did NOT close the connection (BAD)")
    sock.close()


# Attack 1: huge length
sock = connect()
sock.sendall(struct.pack(">I", 0xFFFFFFFF))
wait_for_close(sock, "huge length")


sock = connect()
send_frame(sock, 3, b"not json")
wait_for_close(sock, "broken json")


sock = connect()
send_frame(sock, 99, b"{}")
wait_for_close(sock, "unknown type")


sock = connect()
wait_for_close(sock, "silent")