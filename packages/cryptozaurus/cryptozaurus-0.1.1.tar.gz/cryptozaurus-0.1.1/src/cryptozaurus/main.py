import time

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes, CipherContext
from cryptography.hazmat.backends import default_backend


def is_timestamp_valid(msg: str, secret: str, ttl: int, encrypted_msg_len: int = 32) -> bool:
    encrypted_msg, iv = msg[:encrypted_msg_len], bytes.fromhex(msg[encrypted_msg_len:])
    cipher: Cipher = Cipher(algorithms.AES(secret.encode()), modes.CBC(iv), backend=default_backend())
    return float(_decrypt(encrypted_msg, cipher)) > time.time() - ttl


def _decrypt(encrypted_msg: str, cipher: Cipher) -> str:
    decryptor: CipherContext = cipher.decryptor()
    unpadded_decrypted_msg: bytes = decryptor.update(bytes.fromhex(encrypted_msg)) + decryptor.finalize()
    padding_length: int = unpadded_decrypted_msg[-1]
    decrypted_msg: bytes = unpadded_decrypted_msg[:-padding_length]
    return decrypted_msg.decode()
