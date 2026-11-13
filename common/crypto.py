import hashlib

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pathlib import Path

from common.errors import ConfigError


def generate_identity_key():
    return Ed25519PrivateKey.generate()


def fingerprint(public_bytes): 
    digest = hashlib.sha256(public_bytes).hexdigest()
    h = digest[:16]
    return " ".join(h[i:i+4] for i in range(0, 16, 4))

     
def load_identity_key(path):
    path = Path(path)
    if  not path.exists():
        raise ConfigError(f"identity key not found at {path} — run: python -m server.keygen")
    data = path.read_bytes()
    if len(data) != 32:
        raise ConfigError(f"identity key at {path} is corrupted")
    return Ed25519PrivateKey.from_private_bytes(data)
