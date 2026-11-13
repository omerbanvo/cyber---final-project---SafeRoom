import sys
from pathlib import Path

from common.config import load_config
from common.crypto import fingerprint, generate_identity_key
from common.errors import ConfigError



def main():
    try: 
        config = load_config()
        
    except ConfigError as e:
        print(f"error: {e}")
        sys.exit(1)
    path = Path(config.identity_key_file)
    if path.exists():
        print(f"key already exists at {path} — not overwriting")
        sys.exit(1)
    path.parent.mkdir(parents= True, exist_ok=True)
    key = generate_identity_key()
    path.write_bytes(key.private_bytes_raw())

    public_bytes = key.public_key().public_bytes_raw()
    print(f"public key: {public_bytes.hex()}")
    print(f"fingerprint: {fingerprint(public_bytes)}")

if __name__ == "__main__":
    main()
