import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, CipherContext, algorithms, modes


def is_timestamp_valid(msg: str, secret: str, ttl: int, encrypted_msg_len: int = 32) -> bool:
    """Checks if timestamp didn't exceed the TTL.

    Args:
        msg: Provided encrypted message
        secret: Secret key, must be same as on the JS side
        ttl: Time to live for an encrypted timestamp
        encrypted_msg_len: Length of a provided message
    Returns:
        Boolean that says whether provided timestamp exceeded the TTL
    """
    encrypted_msg, iv = msg[:encrypted_msg_len], bytes.fromhex(msg[encrypted_msg_len:])
    cipher: Cipher = Cipher(
        algorithms.AES(secret.encode()), modes.CBC(iv), backend=default_backend()
    )
    return float(_decrypt(encrypted_msg, cipher)) > time.time() - ttl


def _decrypt(encrypted_msg: str, cipher: Cipher) -> str:
    """Decrypt provided message with a cipher.

    Args:
        encrypted_msg: Provided encrypted message
        cipher: AES cipher with configured initial vector
    Returns:
        Actual decoded timestamp
    """
    decryptor: CipherContext = cipher.decryptor()
    unpadded_decrypted_msg: bytes = (
        decryptor.update(bytes.fromhex(encrypted_msg)) + decryptor.finalize()
    )
    padding_length: int = unpadded_decrypted_msg[-1]
    decrypted_msg: bytes = unpadded_decrypted_msg[:-padding_length]
    return decrypted_msg.decode()
