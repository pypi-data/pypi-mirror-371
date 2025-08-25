# mtls_pluggable/handshake.py
import json, secrets
from .frames import send_frame, recv_frame
from .pki import load_cert, load_private_key, load_ca_chain, verify_cert_chain
from .crypto import gen_x25519_pair, x25519_shared, derive_key, aes_encrypt, aes_decrypt, sign_data, verify_signature

def server_handshake(conn, server_cert_path, server_key_path, ca_chain_path, logger=None):
    server_cert = load_cert(server_cert_path)
    server_priv = load_private_key(server_key_path)
    ca_certs = load_ca_chain(ca_chain_path)

    # send nonce
    nonce = secrets.token_bytes(16)
    send_frame(conn, b"NONCE:" + nonce)
    if logger: logger("sent_nonce", nonce.hex())

    # receive client payload
    raw = recv_frame(conn)
    obj = json.loads(raw.decode())
    client_cert_pem = obj["cert"].encode()
    client_epub = bytes.fromhex(obj["epub"])
    sig_client = bytes.fromhex(obj["sig"])

    client_cert = x509_load_pem_bytes(client_cert_pem)
    if not verify_cert_chain(client_cert, ca_certs):
        raise ValueError("client cert chain verification failed")
    if not verify_signature(client_cert.public_key(), sig_client, nonce + client_epub):
        raise ValueError("client signature invalid")

    # server ephemeral
    serv_priv, serv_pub = gen_x25519_pair()
    transcript = nonce + client_epub + serv_pub
    sig_server = sign_data(server_priv, transcript)

    resp = {"cert": open(server_cert_path, "r").read(), "epub": serv_pub.hex(), "sig": sig_server.hex()}
    send_frame(conn, json.dumps(resp).encode())

    shared = x25519_shared(serv_priv, client_epub)
    key = derive_key(shared, salt=nonce)
    return key

def client_handshake(conn, client_cert_path, client_key_path, ca_chain_path, logger=None):
    client_cert = load_cert(client_cert_path)
    client_priv = load_private_key(client_key_path)
    ca_certs = load_ca_chain(ca_chain_path)

    # recv nonce
    raw = recv_frame(conn)
    if not raw.startswith(b"NONCE:"):
        raise ValueError("expected nonce")
    nonce = raw.split(b"NONCE:")[1]

    # ephemeral
    client_priv_eph, client_pub = gen_x25519_pair()
    sig_client = sign_data(client_priv, nonce + client_pub)
    payload = {"cert": open(client_cert_path, "r").read(), "epub": client_pub.hex(), "sig": sig_client.hex()}
    send_frame(conn, json.dumps(payload).encode())

    # server response
    raw2 = recv_frame(conn)
    resp = json.loads(raw2.decode())
    server_cert_pem = resp["cert"].encode()
    srv_pub = bytes.fromhex(resp["epub"])
    srv_sig = bytes.fromhex(resp["sig"])

    server_cert = x509_load_pem_bytes(server_cert_pem)
    if not verify_cert_chain(server_cert, ca_certs):
        raise ValueError("server cert verification failed")
    if not verify_signature(server_cert.public_key(), srv_sig, nonce + client_pub + srv_pub):
        raise ValueError("server signature invalid")

    shared = x25519_shared(client_priv_eph, srv_pub)
    key = derive_key(shared, salt=nonce)
    return key

# small helper: import x509 loader here to avoid circular import
from cryptography import x509
from cryptography.hazmat.backends import default_backend
def x509_load_pem_bytes(pem_bytes: bytes) -> x509.Certificate:
    return x509.load_pem_x509_certificate(pem_bytes, default_backend())
