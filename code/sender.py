# sender.py
import socket
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.decrepit.ciphers.modes import CFB
import pickle

# Load recipient's public key
with open("public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())
# Message to send
message = b"brr brr patatim"
# 1. Generate random AES key and IV
aes_key = os.urandom(32)  # AES-256
iv = os.urandom(16)
# 2. Encrypt message with AES (CFB mode)
cipher = Cipher(algorithms.AES(aes_key), CFB(iv))
encryptor = cipher.encryptor()
encrypted_message = encryptor.update(message) + encryptor.finalize()
# 3. Encrypt AES key with RSA (recipient's public key)
encrypted_key = public_key.encrypt(  # type: ignore
    aes_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
# 4. Package: (encrypted_key, iv, encrypted_message)
payload = pickle.dumps((encrypted_key, iv, encrypted_message))
# 5. Send via socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(("localhost", 65432))
    s.sendall(payload)
    print("✅ Encrypted message sent!")
