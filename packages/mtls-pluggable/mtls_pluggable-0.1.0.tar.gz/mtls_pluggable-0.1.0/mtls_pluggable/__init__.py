# mtls_pluggable/__init__.py
from .handshake import server_handshake, client_handshake
from .frames import send_frame, recv_frame
from .crypto import aes_encrypt, aes_decrypt
from .pki import load_cert, load_private_key, load_ca_chain

import socket
from threading import Thread

class MTLSServer:
   
    def __init__(self, host, port, server_cert, server_key, ca_chain, logger=None):
        self.host = host; self.port = port
        self.server_cert = server_cert; self.server_key = server_key; self.ca_chain = ca_chain
        self.handler = None
        self.logger = logger or (lambda tag, msg: None)
        self._sock = None
        self._stop = False

    def route(self, func):
        self.handler = func
        return func

    def start(self, threaded=True):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)
        self._sock = s
        self.logger("startup", f"MTLSServer listening on {self.host}:{self.port}")
        if threaded:
            Thread(target=self._serve_loop, daemon=True).start()
        else:
            self._serve_loop()

    def _serve_loop(self):
        while not self._stop:
            conn, addr = self._sock.accept()
            self.logger("accept", f"conn from {addr}")
            try:
                key = server_handshake(conn, self.server_cert, self.server_key, self.ca_chain, logger=lambda t,m: self.logger(t,m))
                self.logger("handshake", "success")
                # Finished exchange
                enc = recv_frame(conn)
                plain = aes_decrypt(key, enc)
                self.logger("app_recv", plain)
                # call handler
                resp = b""
                if self.handler:
                    result = self.handler(plain)  # handler gets raw bytes
                    if isinstance(result, str):
                        resp = result.encode()
                    elif isinstance(result, bytes):
                        resp = result
                    else:
                        resp = json.dumps(result).encode()
                else:
                    resp = b"OK"
                send_frame(conn, aes_encrypt(key, resp))
            except Exception as e:
                self.logger("ERR", str(e))
            finally:
                try: conn.close()
                except: pass

    def stop(self):
        self._stop = True
        try: self._sock.close()
        except: pass

class MTLSClient:
   
    def __init__(self, ca_chain, client_cert, client_key, logger=None):
        self.ca_chain = ca_chain; self.client_cert = client_cert; self.client_key = client_key
        self.logger = logger or (lambda t,m: None)

    def request(self, host, port, payload: bytes, timeout=10):
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((host, port))
        try:
            key = client_handshake(s, self.client_cert, self.client_key, self.ca_chain, logger=lambda t,m: self.logger(t,m))
            self.logger("handshake", "ok")
            # send finished + app data
            from .frames import send_frame, recv_frame
            from .crypto import aes_encrypt, aes_decrypt
            send_frame(s, aes_encrypt(key, payload))
            resp_enc = recv_frame(s)
            resp = aes_decrypt(key, resp_enc)
            return resp
        finally:
            try: s.close()
            except: pass
