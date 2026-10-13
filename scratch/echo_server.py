
import socket

from common.config import load_config
config = load_config()
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((config.host, config.port))
    print(f"server is listening on {config.host}:{config.port}")
    server.listen()
    conn, add = server.accept()
    print(f"client connected on {add}")
    while True:
        data = conn.recv(1024)
        if not data:          # b"" means the client closed the connection
           break
        print(f"received: {data!r}")
        conn.sendall(data)
    conn.close()

if __name__ == "__main__":
    start_server()