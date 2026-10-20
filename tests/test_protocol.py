import unittest

from common.errors import ProtocolError
from common.protocol import MsgType, decode_message, encode_message
from common.protocol import REQUIRED_FIELDS, MsgType, decode_message, encode_message

class TestProtocol(unittest.TestCase):

    def test_encode_decode_roundtrip(self):
        original = {"version": 1, "req_id": 7}
        msg_type, payload = encode_message(MsgType.HELLO, original)

        decoded_type, decoded_data = decode_message(msg_type, payload)

        self.assertEqual(decoded_type, MsgType.HELLO)
        self.assertEqual(decoded_data, original)

    def test_unknown_type(self):
        with self.assertRaises(ProtocolError):
            decode_message(99, b'{}')

    def test_broken_json(self):
        with self.assertRaises(ProtocolError):
            decode_message(MsgType.PING, b'not json')

    def test_list_instead_of_dict(self):
        with self.assertRaises(ProtocolError):
            decode_message(MsgType.PING, b'[1, 2]')

    def test_invalid_utf8(self):
        with self.assertRaises(ProtocolError):
            decode_message(MsgType.PING, b'\xff\xfe')

    def test_missing_required_field(self):
        with self.assertRaises(ProtocolError):
            decode_message(MsgType.HELLO, b'{"req_id": 1}')

    def test_every_type_has_required_fields(self):
        for mtype in MsgType:
            self.assertIn(mtype, REQUIRED_FIELDS)

    def test_wrong_field_type(self):
        with self.assertRaises(ProtocolError) :
            decode_message(MsgType.HELLO, b'{"version": "1", "req_id": 1}')


if __name__ == "__main__":
    unittest.main()