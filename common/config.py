import configparser
from dataclasses import dataclass

from common.errors import ConfigError
@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 31337
    max_clients: int = 4
    max_frame_size: int = 1048576


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
            max_frame_size= section.getint("max_frame_size", fallback= defaults.max_frame_size)

        )
    except ValueError as e:
        raise ConfigError(f"Invalid number in {path}: {e}")

    #port in range?
    if not 1024<= config.port <=65535:
        raise ConfigError(f"port must be 1024-65535, got {config.port}")

    return config