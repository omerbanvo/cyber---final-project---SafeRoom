import logging
import sys

from common.config import load_config
from common.errors import ConfigError
from common.logger import setup_logging
from server.server import Server

logger = logging.getLogger(__name__)

def main():
    setup_logging()
    try:
        config = load_config()
    except ConfigError as e:
        logger.error(e)
        sys.exit(1)
    logger.info(f"server starting on {config.host}:{config.port}")
    server = Server(config)
    server.start()
    
if __name__ == "__main__":
    main()