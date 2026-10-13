import json

from enum import IntEnum
from common.errors import ProtocolError

PROTOCOL_VERSION = 1



class MsgType(IntEnum):
    HELLO = 0x01
    WELCOME = 0x02
    PING = 0x03
    PONG = 0x04
    BYE = 0x05
    ERROR = 0x06
    BROADCAST_TEST = 0x0F

class ErrorCode:
    BAD_VERSION = "BAD_VERSION"
    BAD_MESSAGE = "BAD_MESSAGE"
    NOT_READY = "NOT_READY"
    SERVER_FULL = "SERVER_FULL"

def encode_message(msg_type: MsgType, data: dict) ->tuple[int, bytes]:
    text = json.dumps(data)
    payload = text.encode("utf-8")
    return int(msg_type), payload


REQUIRED_FIELDS = {
    MsgType.HELLO: ["version", "req_id"],
    MsgType.WELCOME: ["req_id", "client_id"],
    MsgType.PING: ["req_id"],
    MsgType.PONG: ["req_id"],
    MsgType.BYE: [],
    MsgType.ERROR: ["code", "message"],
    MsgType.BROADCAST_TEST: ["text"],
}

def decode_message(msg_type: int, payload: bytes)-> tuple[MsgType, dict]:
    try:
        mtype = MsgType(msg_type)
    except ValueError:
        raise ProtocolError(f"unknown message type: {msg_type}")

    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        raise ProtocolError("payload is not valid UTF-8")


    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise ProtocolError("payload is not valid JSON")



    if not isinstance(data, dict):
        raise ProtocolError("payload must be a JSON object")

    for field in REQUIRED_FIELDS[mtype]:
        if field not in data:
            raise ProtocolError(f"missing field '{field}' in {mtype.name}")        

    return mtype, data
