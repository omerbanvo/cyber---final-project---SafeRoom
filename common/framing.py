import struct


from common.errors import ConnectionClosed, FrameTooLarge, InvalidFrame

#reciving exactly n bytes
def recv_exact(sock, n: int) ->bytes:
    b = b""
    while len(b) < n:
        chunk = sock.recv(n - len(b))
        if not chunk:
            raise ConnectionClosed("connection faild: connection stopped unexpectedly before recieveing expected data ")
        b+=chunk
    return b

#function to send a message by frame
def send_frame(sock, msg_type: int, payload: bytes) -> None:
    length = len(payload) + 1
    
    header = struct.pack(">IB", length, msg_type)
    sock.sendall(header + payload)
    


def recv_frame(sock, max_size: int)-> tuple[int, bytes]:
    data = recv_exact(sock, 4)
    length = struct.unpack(">I", data)[0]
    if length > max_size:
        raise FrameTooLarge(f"frame length {length} exceeds max {max_size}")
    if length == 0:
        raise InvalidFrame("frame length is 0")
    body = recv_exact(sock, length)
    msg_type = body[0]
    payload = body[1:]
    return (msg_type, payload)