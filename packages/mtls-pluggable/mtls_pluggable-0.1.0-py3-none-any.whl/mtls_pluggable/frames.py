# mtls_pluggable/frames.py
import socket

def send_frame(conn: socket.socket, b: bytes):
    length = len(b).to_bytes(4, "big")
    conn.sendall(length + b)

def recv_frame(conn: socket.socket) -> bytes:
    hdr = b""
    while len(hdr) < 4:
        chunk = conn.recv(4 - len(hdr))
        if not chunk:
            raise ConnectionError("connection closed while reading length")
        hdr += chunk
    length = int.from_bytes(hdr, "big")
    payload = b""
    while len(payload) < length:
        chunk = conn.recv(min(4096, length - len(payload)))
        if not chunk:
            raise ConnectionError("connection closed while reading payload")
        payload += chunk
    return payload
