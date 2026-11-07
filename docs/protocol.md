# SafeRoom Protocol — Stage 1

## 1. Frame format

TCP is a stream of bytes, not messages. So every message is sent inside a **frame**.
The frame says its own length first, so the other side knows how many bytes to read.

```
+-------------------+-----------+-----------------------------+
| length (4 bytes)  | type (1B) | payload (length - 1 bytes)  |
+-------------------+-----------+-----------------------------+
```

- **length**: unsigned, big-endian (`struct` format `>I`). It counts the type byte **and** the payload: `length = 1 + len(payload)`.
- **type**: one byte (`B`). The message type (see section 2).
- **payload**: the message body. In stage 1 it is JSON, encoded as UTF-8.

**Rules when receiving a frame:**
- `length == 0` → invalid frame, the connection is closed.
- `length > max_frame_size` (default 1 MiB) → the connection is closed **before** reading the payload. This blocks a client that sends a fake huge length (for example 4 GB) to make the server allocate memory.

**Why is the type outside the JSON?** In stage 2 the payload will be encrypted. The receiver must still know the message type without decrypting first.


## 2. Message types

Types are defined in `common/protocol.py` as `MsgType` (an `IntEnum`).
Each range is saved for one stage of the project:

| Range       | Use                                  |
|-------------|--------------------------------------|
| 0x01–0x0F   | Connection and maintenance (stage 1) |
| 0x10–0x1F   | Handshake and encryption             |
| 0x20–0x2F   | Users: register, login               |
| 0x30–0x3F   | Rooms                                |
| 0x40–0x4F   | Chat                                 |
| 0x50–0x5F   | Files                                |
| 0x60–0x6F   | Call signaling (UDP)                 |

### Stage 1 messages

| Type | Name           | Direction           | Required fields                    |
|------|----------------|---------------------|------------------------------------|
| 0x01 | HELLO          | client → server     | `version` (int), `req_id` (int)    |
| 0x02 | WELCOME        | server → client     | `req_id` (int), `client_id` (str)  |
| 0x03 | PING           | both                | `req_id` (int)                     |
| 0x04 | PONG           | both                | `req_id` (int)                     |
| 0x05 | BYE            | both                | none (optional `reason`)           |
| 0x06 | ERROR          | server → client     | `code` (str), `message` (str)      |
| 0x0F | BROADCAST_TEST | client → server → others | `text` (str)                  |

`BROADCAST_TEST` is temporary. It proves that the server can route messages between clients. It will be removed when real chat is added.

**Field types are checked.** `decode_message` rejects a message if a required field is missing **or** has the wrong type. A boolean is never accepted as an `int` (in Python, `True` is also an `int`).




## 3. Message examples

Every message from the client gets a `req_id`. It starts at 1 and goes up by 1.
The server copies the same `req_id` into its answer, so the client knows which request the answer belongs to.

**HELLO** (client → server)
```json
{"version": 1, "req_id": 1}
```

**WELCOME** (server → client)
```json
{"req_id": 1, "client_id": "a3f9c21b"}
```

**PING / PONG**
```json
{"req_id": 2}
```

**BYE** (client → server, or server → client)
```json
{"reason": "server is shutting down"}
```

**ERROR** (server → client)
```json
{"code": "NOT_READY", "message": "send HELLO first", "req_id": 2}
```
`req_id` is included only when the error answers a specific request.

**BROADCAST_TEST**
Client → server:
```json
{"text": "hello", "req_id": 3}
```
Server → every other READY client:
```json
{"from": "a3f9c21b", "text": "hello"}
```


## 4. Client states (server side)

The server keeps a state for every connected client (`ClientState` in `server/client_handler.py`).

```
             valid HELLO
CONNECTED  ───────────────►  READY
    │                          │
    │ bad version / timeout    │ BYE / disconnect / server shutdown
    │ bad data / disconnect    │ bad data
    ▼                          ▼
  CLOSED  ◄────────────────────┘
```

| State     | Meaning                                       | What the client can send            |
|-----------|-----------------------------------------------|-------------------------------------|
| CONNECTED | TCP connection is open, no HELLO yet          | Only `HELLO`. Anything else → `ERROR NOT_READY` (the connection stays open) |
| READY     | Valid HELLO received, `WELCOME` sent          | `PING`, `PONG`, `BYE`, `BROADCAST_TEST` |
| CLOSED    | The connection is ending                      | Nothing. The handler cleans up and closes the socket |

**Rules:**
- A client has `hello_timeout` seconds (default 10) to send `HELLO`. If not, it is disconnected. This stops clients that connect and stay silent to take a place.
- `HELLO` with a wrong `version` → `ERROR BAD_VERSION`, then the connection is closed.
- A second

## 5. Error codes

Error codes are fixed strings, defined in one place: `ErrorCode` in `common/protocol.py`.

| Code          | When the server sends it                                   | After the error          |
|---------------|------------------------------------------------------------|--------------------------|
| `BAD_VERSION` | `HELLO` with a `version` that is not `PROTOCOL_VERSION` (1) | Connection is closed     |
| `NOT_READY`   | Any message except `HELLO` before the client is READY       | Connection stays open    |
| `BAD_MESSAGE` | A second `HELLO`, or a message the client is not allowed to send (`WELCOME`, `ERROR`) | Connection stays open |
| `SERVER_FULL` | A new client connects when `max_clients` are already connected | Connection is closed  |

**When does the server NOT send an error?**
If the data cannot be read at all (bad frame, bad JSON, unknown type, missing or wrong field), the server does not answer. It logs a `WARNING` and closes the connection. A client that sends broken data may be an attacker, so the server does not spend more work on it.