import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
import struct

def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a 64-byte key using PBKDF2 (32 for encryption, 32 for HMAC)."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=64, # 64 bytes total
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password.encode())

def encrypt_message(message: bytes, password: str) -> bytes:
    """
    Encrypts a message using ChaCha20 and protects integrity via HMAC.
    Returns: Header (4 bytes) + salt (16) + nonce (8) + ciphertext + HMAC (32)
    """
    salt = os.urandom(16)
    nonce = os.urandom(16)
    master_key = derive_key(password, salt)
    
    enc_key = master_key[:32]
    mac_key = master_key[32:]

    cipher = Cipher(algorithms.ChaCha20(enc_key, nonce), mode=None)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message)

    # Core payload to authenticate
    payload = salt + nonce + ciphertext
    
    # Calculate HMAC over the payload
    h = hmac.HMAC(mac_key, hashes.SHA256())
    h.update(payload)
    mac = h.finalize() # Generates 32 bytes
    
    # Final package
    final_payload = payload + mac
    
    # Prefix the length of the package as a 4-byte header (unsigned int)
    length_header = struct.pack(">I", len(final_payload))
    
    return length_header + final_payload

def decrypt_message(packet: bytes, password: str) -> bytes:
    """
    Verifies HMAC integrity and then decrypts the packet.
    Assumes packet shape: salt(16) + nonce(8) + ciphertext + HMAC(32).
    """
    if len(packet) < 16 + 16 + 32:
        raise ValueError("Packet is too short or corrupted.")

    mac_received = packet[-32:]
    payload = packet[:-32]

    salt = payload[:16]
    nonce = payload[16:32]
    ciphertext = payload[32:]

    master_key = derive_key(password, salt)
    enc_key = master_key[:32]
    mac_key = master_key[32:]

    # Step 1: Verify HMAC Integrity!
    h = hmac.HMAC(mac_key, hashes.SHA256())
    h.update(payload)
    try:
        h.verify(mac_received)
    except Exception:
        raise ValueError("Integrity check failed! (Wrong password or corrupted data)")

    # Step 2: Decrypt if verified
    cipher = Cipher(algorithms.ChaCha20(enc_key, nonce), mode=None)
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext)

    return plaintext

