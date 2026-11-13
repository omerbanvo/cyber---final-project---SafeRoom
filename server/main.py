import logging
import sys

from common.config import load_config
from common.errors import ConfigError
from common.logger import setup_logging
from server.server import Server
from common.crypto import fingerprint, load_identity_key

logger = logging.getLogger(__name__)

def main():
    setup_logging()
    try:
        config = load_config()
        identity_key = load_identity_key(config.identity_key_file)
    except ConfigError as e:
        logger.error(e)
        sys.exit(1)
    public_bytes = identity_key.public_key().public_bytes_raw()
    logger.info(f"server identity fingerprint: {fingerprint(public_bytes)}")
    logger.info(f"server starting on {config.host}:{config.port}")
    server = Server(config)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("shutting down...")
        server.stop()
    
if __name__ == "__main__":
    main()