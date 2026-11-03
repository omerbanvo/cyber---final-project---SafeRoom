import threading

from common.protocol import MsgType
from client.connection import Connection
from common.config import load_config
from common.errors import ConfigError, ConnectionClosed

disconnected = threading.Event()


def on_message(mtype, data) -> None:
    if mtype == MsgType.WELCOME:
        print(f"connected as {data['client_id']}")
    elif mtype == MsgType.PONG:
        print(f"pong (req {data['req_id']})")
    elif mtype == MsgType.ERROR:
        print(f"error {data['code']}: {data['message']}")
    elif mtype == MsgType.BROADCAST_TEST:
        print(f"[{data['from']}] {data['text']}")
    else:
            print(f"{mtype.name}: {data}")

def on_disconnect(reason) -> None:
    print(f"disconnected: {reason}")
    disconnected.set()


def main():
    try:
        config = load_config()
    except ConfigError as e:
        print(f"error: {e}")
        return 
    conn = Connection(config, on_message, on_disconnect)
    try:
        conn.connect()
    except OSError:
        print("can't connect to server")
        return 
    print("commands: /ping, /bc <text>, /bye")
    while not disconnected.is_set():
        try:
            line = input("> ")
        except (KeyboardInterrupt, EOFError):
            conn.close()
            break
        try:
            if disconnected.is_set():
                break
            if line.lower() == "/ping":
                conn.send(MsgType.PING, {})
            elif line.startswith("/bc "):
                conn.send(MsgType.BROADCAST_TEST, {"text": line[4:]})
            elif line.lower() == "/bye":
                conn.close()
                break
            else:
                print("commands: /ping, /bc <text>, /bye")
        except ConnectionClosed:
            print("connection lost")
            break
