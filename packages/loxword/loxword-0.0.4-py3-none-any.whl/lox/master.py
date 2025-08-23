# master.py
import os
import bcrypt
from getpass import getpass
import secrets

MASTER_HASH_FILE = 'master.hash'
SALT_FILE = 'salt.bin'
RECOVERY_HASH_FILE = 'recovery.hash'
RECOVERY_BACKUP = 'recovery_backup.txt'  # a place we advise user to store offline

def set_master_password(user_path):
    while True:
        password = getpass('Set master password: ')
        confirm = getpass("Confirm master password: ")
        if not password:
            print("Password cannot be empty.")
            continue
        if password != confirm:
            print("Passwords do not match. Try again.")
            continue
        break

    # bcrypt hash for master password
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    with open(os.path.join(user_path, MASTER_HASH_FILE), 'wb') as f:
        f.write(password_hash)

    # salt used for deriving Fernet key (random 16 bytes)
    salt = os.urandom(16)
    with open(os.path.join(user_path, SALT_FILE), 'wb') as f:
        f.write(salt)

    # create recovery token (one-time token). Show to user and save a hashed version.
    recovery_token = secrets.token_urlsafe(32)
    recovery_hash = bcrypt.hashpw(recovery_token.encode(), bcrypt.gensalt())
    with open(os.path.join(user_path, RECOVERY_HASH_FILE), 'wb') as f:
        f.write(recovery_hash)

    # Save a local backup (plaintext) and instruct the user to move it offline.
    backup_path = os.path.join(user_path, RECOVERY_BACKUP)
    with open(backup_path, 'w') as f:
        f.write(recovery_token)

    print("\nIMPORTANT: Recovery token created. Save it somewhere safe (offline).")
    print("A local backup was written to:", backup_path)
    print("\nRecovery token (copy and store offline now):")
    print(recovery_token)
    print("\nIf you lose your master password you can use this token to reset it.")
    return password, salt

def verify_master_password(user_path):
    master_hash_path = os.path.join(user_path, MASTER_HASH_FILE)
    salt_path = os.path.join(user_path, SALT_FILE)

    if not os.path.exists(master_hash_path) or not os.path.exists(salt_path):
        raise FileNotFoundError("Master password or salt missing.")

    with open(master_hash_path, 'rb') as f:
        stored_hash = f.read()
    with open(salt_path, 'rb') as f:
        salt = f.read()

    attempts = 3
    while attempts > 0:
        password = getpass('Enter master password: ')
        if bcrypt.checkpw(password.encode(), stored_hash):
            return password, salt
        attempts -= 1
        print(f"Incorrect password. Attempts left: {attempts}")

    print("Too many failed attempts.")
    return None, None

def reset_master_with_recovery(user_path):
    # Ask for recovery token and verify against stored hash
    recovery_hash_path = os.path.join(user_path, RECOVERY_HASH_FILE)
    if not os.path.exists(recovery_hash_path):
        print("No recovery option available for this user.")
        return None, None

    token = getpass("Enter recovery token: ").strip()
    with open(recovery_hash_path, 'rb') as f:
        stored_recovery_hash = f.read()

    if not bcrypt.checkpw(token.encode(), stored_recovery_hash):
        print("Invalid recovery token.")
        return None, None

    # If valid, allow setting a new master password (overwrites old)
    print("Recovery token accepted. Set a new master password.")
    return set_master_password(user_path)
