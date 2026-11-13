import hashlib

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey



def generate_identity_key():
    return Ed25519PrivateKey.generate()

def fingerprint(public_bytes): 
    digest = hashlib.sha256(public_bytes).hexdigest()
    h = digest[:16]
    return " ".join(h[i:i+4] for i in range(0, 16, 4))
     

