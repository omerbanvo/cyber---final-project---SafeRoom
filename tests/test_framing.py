import socket
import struct
import threading
import unittest

from common.errors import ConnectionClosed, FrameTooLarge, InvalidFrame
from common.framing import recv_frame, send_frame

MAX_SIZE = 1024 * 1024


class TestFraming(unittest.TestCase):

    def setUp(self):
        self.a, self.b = socket.socketpair()

    def tearDown(self):
        self.a.close()
        self.b.close()

    def test_three_frames_in_a_row(self):
        send_frame(self.a, 1, b"first")
        send_frame(self.a, 2, b"second")
        send_frame(self.a, 3, b"third")

        self.assertEqual(recv_frame(self.b, MAX_SIZE), (1, b"first"))
        self.assertEqual(recv_frame(self.b, MAX_SIZE), (2, b"second"))
        self.assertEqual(recv_frame(self.b, MAX_SIZE), (3, b"third"))

    def test_large_frame_500kb(self):
        payload = b"x" * 500_000

        sender = threading.Thread(target=send_frame, args=(self.a, 1, payload))
        sender.start()

        msg_type, received = recv_frame(self.b, MAX_SIZE)
        sender.join()

        self.assertEqual(msg_type, 1)
        self.assertEqual(received, payload)

    def test_frame_too_large(self):
        self.a.sendall(struct.pack(">I", MAX_SIZE + 1))

        with self.assertRaises(FrameTooLarge):
            recv_frame(self.b, MAX_SIZE)

    def test_zero_length_frame(self):
        self.a.sendall(struct.pack(">I", 0))

        with self.assertRaises(InvalidFrame):
            recv_frame(self.b, MAX_SIZE)

    def test_closed_in_middle_of_frame(self):
        self.a.sendall(struct.pack(">I", 10) + b"abc")
        self.a.close()

        with self.assertRaises(ConnectionClosed):
            recv_frame(self.b, MAX_SIZE)


if __name__ == "__main__":
    unittest.main()