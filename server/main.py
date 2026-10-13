import sys

from common.config import load_config
from common.errors import ConfigError


def main():
    try:
        config = load_config()
    except ConfigError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"server starting on {config.host}: {config.port}")
if __name__ == "__main__":
    main()