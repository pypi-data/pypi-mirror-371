# mtls_pluggable/pki.py
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from typing import List

def load_cert(path: str) -> x509.Certificate:
    with open(path, "rb") as f:
        return x509.load_pem_x509_certificate(f.read(), default_backend())

def load_private_key(path: str):
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    with open(path, "rb") as f:
        return load_pem_private_key(f.read(), password=None, backend=default_backend())

def load_ca_chain(path: str) -> List[x509.Certificate]:
    with open(path, "rb") as f:
        raw = f.read()
    parts = raw.split(b"-----END CERTIFICATE-----")
    certs = []
    for p in parts:
        if b"BEGIN CERTIFICATE" in p:
            pem = p + b"-----END CERTIFICATE-----\n"
            try:
                certs.append(x509.load_pem_x509_certificate(pem, default_backend()))
            except Exception:
                continue
    return certs

def verify_cert_chain(leaf: x509.Certificate, ca_certs: List[x509.Certificate]) -> bool:
    # Simplified signature check: verify leaf's signature with each CA pubkey
    from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec, ed25519
    alg = leaf.signature_hash_algorithm
    sig = leaf.signature
    tbs = leaf.tbs_certificate_bytes
    for ca in ca_certs:
        pub = ca.public_key()
        try:
            if hasattr(pub, "key_size"):  # probably RSA
                pub.verify(sig, tbs, padding.PKCS1v15(), alg)
                return True
        except Exception:
            pass
        try:
            # ECDSA
            pub.verify(sig, tbs, ec.ECDSA(alg))
            return True
        except Exception:
            pass
        try:
            # Ed25519
            pub.verify(sig, tbs)
            return True
        except Exception:
            pass
    return False
