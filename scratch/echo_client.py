import socket


from common.config import load_config

config = load_config()

def start_client():
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    conn.connect((config.host, config.port))

    conn.send(b"test")
    conn.send(b"123")
    message = conn.recv(1024).decode("utf8")
    print(message)


if __name__ == "__main__":
    start_client()