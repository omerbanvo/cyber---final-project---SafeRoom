# SafeRoom

An encrypted video-call app with chat and file transfer — 5-unit Cyber final project.

**Current status: Stage 1** — a multi-client TCP server and a text client that talk with a custom protocol.
No encryption yet (that is stage 2).

🇮🇱 [גרסה בעברית](README.he.md)

## Requirements

- Python 3.11 or newer
- No external packages

## Setup

```bash
git clone https://github.com/omerbanvo/cyber---final-project---SafeRoom.git
cd cyber---final-project---SafeRoom
python3 -m venv venv
source venv/bin/activate
cp config/config.example.ini config/config.ini
```

## Configuration

Edit `config/config.ini`:

| Key              | Meaning                                    | Default     |
|------------------|--------------------------------------------|-------------|
| `host`           | Address the server listens on              | `127.0.0.1` |
| `port`           | Port (1024–65535)                          | `31337`     |
| `max_clients`    | How many clients can connect at once       | `4`         |
| `max_frame_size` | Largest allowed frame, in bytes            | `1048576`   |
| `hello_timeout`  | Seconds a new client has to send `HELLO`   | `10`        |

## Running

Always run from the project's root folder, with `-m`:

```bash
python -m server.main      # terminal 1
python -m client.main      # terminal 2, 3, ...
```

Client commands:

| Command       | What it does                          |
|---------------|---------------------------------------|
| `/ping`       | Send PING, get PONG                   |
| `/bc <text>`  | Send text to all other clients        |
| `/bye`        | Disconnect                            |

Stop the server with `Ctrl+C`. It sends `BYE` to every client and closes cleanly.

## Tests

```bash
python -m unittest discover tests
```

Attacker script (the server must be running). It sends bad data and checks that the server closes only that connection:

```bash
python -m tests.attacker
```

## Project structure

```
common/   code used by both server and client (config, framing, protocol, errors)
server/   the server
client/   the client
tests/    unit tests and the attacker script
docs/     protocol documentation
```

## Documentation

- [Protocol](docs/protocol.md) · [פרוטוקול](docs/protocol.he.md)