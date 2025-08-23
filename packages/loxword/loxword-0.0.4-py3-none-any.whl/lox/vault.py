# vault.py
import os
import json
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend

VAULT_FILE = "vault.bin"

def _derive_key(password: str, salt: bytes) -> bytes:
    # Derive 32 byte key for Fernet using PBKDF2HMAC
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def get_fernet_key(password: str, salt: bytes):
    key = _derive_key(password, salt)
    return Fernet(key)

def load_vault(fernet, user_path):
    vault_path = os.path.join(user_path, VAULT_FILE)
    if not os.path.exists(vault_path):
        return {}
    with open(vault_path, "rb") as f:
        data = f.read()
    try:
        decrypted = fernet.decrypt(data)
        return json.loads(decrypted.decode())
    except Exception:
        # If decryption fails, assume wrong password or corrupted vault
        raise ValueError("Failed to decrypt vault. Possibly wrong master password or corrupted vault.")

def save_vault(vault_dict, fernet, user_path):
    vault_path = os.path.join(user_path, VAULT_FILE)
    data = json.dumps(vault_dict).encode()
    token = fernet.encrypt(data)
    with open(vault_path, "wb") as f:
        f.write(token)
