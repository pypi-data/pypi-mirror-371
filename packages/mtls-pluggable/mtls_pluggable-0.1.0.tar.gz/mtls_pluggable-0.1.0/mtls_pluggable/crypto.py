# mtls_pluggable/crypto.py
import os
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding, ec, ed25519, rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

def gen_x25519_pair() -> Tuple[X25519PrivateKey, bytes]:
    priv = X25519PrivateKey.generate()
    pub = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return priv, pub

def x25519_shared(priv: X25519PrivateKey, peer_pub_bytes: bytes) -> bytes:
    peer = X25519PublicKey.from_public_bytes(peer_pub_bytes)
    return priv.exchange(peer)

def derive_key(shared: bytes, salt: bytes, info: bytes = b"mtls-demo", length: int = 32) -> bytes:
    hkdf = HKDF(algorithm=hashes.SHA256(), length=length, salt=salt, info=info)
    return hkdf.derive(shared)

def aes_encrypt(key: bytes, plaintext: bytes) -> bytes:
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plaintext, None)
    return nonce + ct

def aes_decrypt(key: bytes, data: bytes) -> bytes:
    aes = AESGCM(key)
    nonce = data[:12]
    ct = data[12:]
    return aes.decrypt(nonce, ct, None)

def sign_data(priv, data: bytes) -> bytes:
    # supports RSA, ECDSA, Ed25519
    if hasattr(priv, "sign"):
        try:
            if isinstance(priv, rsa.RSAPrivateKey) or getattr(priv, "key_size", None):
                return priv.sign(data, padding.PKCS1v15(), hashes.SHA256())
        except Exception:
            pass
        try:
            return priv.sign(data, ec.ECDSA(hashes.SHA256()))
        except Exception:
            pass
        try:
            return priv.sign(data)
        except Exception:
            pass
    raise ValueError("Unsupported private key type for signing")

def verify_signature(pub, signature: bytes, data: bytes) -> bool:
    try:
        pub.verify(signature, data, padding.PKCS1v15(), hashes.SHA256())
        return True
    except Exception:
        pass
    try:
        pub.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        pass
    try:
        pub.verify(signature, data)
        return True
    except Exception:
        pass
    return False
