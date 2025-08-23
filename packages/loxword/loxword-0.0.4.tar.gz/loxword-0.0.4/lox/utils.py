# utils.py
import os

USERS_DIR = "users"

def ensure_users_dir():
    os.makedirs(USERS_DIR, exist_ok=True)

def list_users():
    ensure_users_dir()
    return [d for d in os.listdir(USERS_DIR) if os.path.isdir(os.path.join(USERS_DIR, d))]

def user_path(username):
    ensure_users_dir()
    path = os.path.join(USERS_DIR, username)
    os.makedirs(path, exist_ok=True)
    return path
