import configparser
from dataclasses import dataclass

from common.errors import ConfigError
@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 31337
    max_clients: int = 4
    max_frame_size: int = 1048576
    hello_timeout: int = 10
    identity_key_file: str = "keys/server_identity.key"
@dataclass
class ClientConfig:
    host: str = "127.0.0.1"
    port: int = 31337
    max_frame_size: int = 1048576
    server_public_key: str = ""

def load_config(path: str = "config/config.ini") -> ServerConfig:
    parser = configparser.ConfigParser()

    #the file exists?
    if not parser.read(path):
        raise ConfigError(f"config file not found: {path}")

    #the [server] section exists ?
    if not parser.has_section("server"):
        raise ConfigError(f"missing [server] section in {path}")
    section = parser["server"]
    defaults = ServerConfig()

    #read values and conver to int
    try:
        config = ServerConfig(
            host = section.get("host", fallback= defaults.host), 
            port = section.getint("port", fallback= defaults.port),
            max_clients= section.getint("max_clients", fallback= defaults.max_clients),
            max_frame_size= section.getint("max_frame_size", fallback= defaults.max_frame_size),
            hello_timeout=section.getint("hello_timeout", fallback=defaults.hello_timeout),
            identity_key_file=section.get("identity_key_file", fallback=defaults.identity_key_file),

        )
    except ValueError as e:
        raise ConfigError(f"Invalid number in {path}: {e}")

    #port in range?
    if not 1024<= config.port <=65535:
        raise ConfigError(f"port must be 1024-65535, got {config.port}")

    return config


def load_client_config(path: str = "config/config.ini") -> ClientConfig:
    parser = configparser.ConfigParser()

    if not parser.read(path):
        raise ConfigError(f"Config file not found: {path}")

    if not parser.has_section("server"):
        raise ConfigError(f"Missing [server] section in {path}")
    
    if not parser.has_section("client"):
        raise ConfigError(f"Missing [client] section in {path}")

    section = parser["server"]
    defaults = ClientConfig()

    try:
        config = ClientConfig(
            host=section.get("host", fallback=defaults.host),
            port=section.getint("port", fallback=defaults.port),
            max_frame_size=section.getint("max_frame_size", fallback=defaults.max_frame_size),
            server_public_key=parser["client"].get("server_public_key", fallback=defaults.server_public_key),
        )
    except ValueError as e:
        raise ConfigError(f"Invalid number in {path}: {e}") from e

    if not 1024 <= config.port <= 65535:
        raise ConfigError(f"Port must be 1024-65535, got {config.port}")


    try:
        key_bytes = bytes.fromhex(config.server_public_key)
    except ValueError:
        raise ConfigError(
            "server_public_key in [client] is not valid hex "
            "— run python -m server.keygen and copy the public key"
        ) from None

    if len(key_bytes) != 32:
        raise ConfigError(
            f"server_public_key in [client] must be 64 hex characters, got {len(config.server_public_key)}"
        )
    
    return config