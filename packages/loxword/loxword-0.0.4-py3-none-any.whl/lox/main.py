# main.py
import sys
import time
import threading
import os
import pyperclip

from .master import verify_master_password, set_master_password, reset_master_with_recovery
from .vault import get_fernet_key, load_vault, save_vault
from .utils import list_users, user_path, ensure_users_dir
from getpass import getpass

AUTOLOCK_TIMEOUT = 60  # seconds (adjustable)

SESSION_LOCKED = threading.Event()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def copyAutoClear(data, timeout=20):
    pyperclip.copy(data)
    print(f"Copied to clipboard! (Will clear in {timeout}s)")

    def clear_clipboard():
        time.sleep(timeout)
        pyperclip.copy(' ')
        print("\n[i] Clipboard cleared.")

    threading.Thread(target=clear_clipboard, daemon=True).start()

def choose_user_interactive():
    clear_screen()
    ensure_users_dir()
    users = list_users()
    print("=== Lox — Multi-user selection ===")
    if users:
        print("Existing users:")
        for u in users:
            print(" -", u)
    else:
        print("[No existing users yet]")

    while True:
        print("\nOptions:")
        print("1) Use existing user")
        print("2) Create new user")
        print("3) Exit")
        choice = input("Choose option [1/2/3]: ").strip()
        if choice == "1":
            if not users:
                print("No users available. Choose option 2 to create one.")
                continue
            username = input("Enter username: ").strip()
            if username not in users:
                print("User not found.")
                continue
            return user_path(username), False
        elif choice == "2":
            username = input("New username: ").strip()
            if not username:
                print("Invalid username.")
                continue
            return user_path(username), True
        elif choice == "3":
            sys.exit(0)
        else:
            print("Invalid option.")

def autolock(func):
    def wrapper(*args, **kwargs):
        # create/reset timer inside wrapper and pass reset_timer to function
        timer = None

        def lock():
            print("\n[!] Session locked due to inactivity.")
            SESSION_LOCKED.set()
            # Don't exit here, let the menu handle it

        def reset_timer():
            nonlocal timer
            if SESSION_LOCKED.is_set():
                return  # Don't reset timer if session is already locked
            if timer:
                timer.cancel()
            timer = threading.Timer(AUTOLOCK_TIMEOUT, lock)
            timer.daemon = True
            timer.start()

        # Clear any existing lock state and start timer
        SESSION_LOCKED.clear()
        reset_timer()
        
        try:
            result = func(*args, reset_timer=reset_timer, **kwargs)
        finally:
            if timer:
                timer.cancel()
        return result

    return wrapper

@autolock
def menu(fernet, user_path, reset_timer):
    try:
        vault = load_vault(fernet, user_path)
    except ValueError as e:
        print(str(e))
        # if vault cannot be decrypted, allow user to exit or reset via recovery
        while True:
            print("\n1) Try again (re-login)")
            print("2) Reset master password with recovery token")
            print("3) Exit")
            c = input("Choose: ").strip()
            if c == "1":
                return "retry"  # return to login
            elif c == "2":
                pw_salt = reset_master_with_recovery(user_path)
                return "retry"
            elif c == "3":
                sys.exit(1)
            else:
                print("Invalid option.")
        return

    while True:
        # Check if session is locked at the start of each loop iteration
        if SESSION_LOCKED.is_set():
            clear_screen()
            print("\n[!] Session locked due to inactivity. Please re-login.")
            return "locked"

        clear_screen()
        print("\n--- THE LOX ---")
        print("\nWelcome to the Lox: Your personal vault, in your terminal")
        print("1. Get Secret")
        print("2. Create/Update Entry")
        print("3. Delete Entry")
        print("4. List Entries")
        print("5. Change Master Password")
        print("6. Logout")
        print("7. Exit")
        
        # Check for lock before getting input
        if SESSION_LOCKED.is_set():
            clear_screen()
            print("\n[!] Session locked due to inactivity. Please re-login.")
            return "locked"
            
        choice = input("Choose option: ").strip()
        reset_timer()

        # Check for lock after user input
        if SESSION_LOCKED.is_set():
            clear_screen()
            print("\n[!] Session locked due to inactivity. Please re-login.")
            return "locked"

        clear_screen()

        if choice == "1":
            name = input("Entry name: ").strip()
            reset_timer()
            if SESSION_LOCKED.is_set():
                clear_screen()
                print("\n[!] Session locked due to inactivity. Please re-login.")
                return "locked"
            if name in vault:
                copyAutoClear(vault[name])
            else:
                print("No entry found.")
                
        elif choice == "2":
            name = input("Entry name: ").strip()
            reset_timer()
            if SESSION_LOCKED.is_set():
                clear_screen()
                print("\n[!] Session locked due to inactivity. Please re-login.")
                return "locked"
                
            
            pswd = getpass("Secret: ")
            reset_timer()
            if SESSION_LOCKED.is_set():
                clear_screen()
                print("\n[!] Session locked due to inactivity. Please re-login.")
                return "locked"
                
            confirm = getpass("Confirm Secret: ")
            reset_timer()
            if SESSION_LOCKED.is_set():
                clear_screen()
                print("\n[!] Session locked due to inactivity. Please re-login.")
                return "locked"
                
            if pswd != confirm:
                print("Secrets do not match. Entry not saved.")
                continue
            vault[name] = pswd
            save_vault(vault, fernet, user_path)
            print("Entry saved/updated.")
            
        elif choice == "3":
            name = input("Entry name: ").strip()
            reset_timer()
            if SESSION_LOCKED.is_set():
                clear_screen()
                print("\n[!] Session locked due to inactivity. Please re-login.")
                return "locked"
                
            if name in vault:
                confirm = input(f"Are you sure you want to delete entry '{name}'? (y/N): ").strip().lower()
                reset_timer()
                if SESSION_LOCKED.is_set():
                    clear_screen()
                    print("\n[!] Session locked due to inactivity. Please re-login.")
                    return "locked"
                    
                if confirm == "y":
                    del vault[name]
                    save_vault(vault, fernet, user_path)
                    print(f"Entry '{name}' deleted.")
                else:
                    print("Deletion cancelled.")
            else:
                print("No such entry.")
                
        elif choice == "4":
            if vault:
                print("Entries:")
                for entry in sorted(vault.keys()):
                    print("-", entry)
            else:
                print("Vault is empty.")
                
        elif choice == "5":
            # change master password flow
            
            print("Change master password (requires current password).")
            # require current password verification
            
            cur_pw, _ = verify_master_password(user_path)
            reset_timer()
            if SESSION_LOCKED.is_set():
                clear_screen()
                print("\n[!] Session locked due to inactivity. Please re-login.")
                return "locked"
                
            if cur_pw is None:
                print("Failed to verify current password. Aborting.")
            else:
                print("Set new master password:")
                new_pw, new_salt = set_master_password(user_path)
                reset_timer()
                if SESSION_LOCKED.is_set():
                    clear_screen()
                    print("\n[!] Session locked due to inactivity. Please re-login.")
                    return "locked"
                    
                # re-encrypt vault with new key
                new_fernet = get_fernet_key(new_pw, new_salt)
                save_vault(vault, new_fernet, user_path)
                fernet = new_fernet
                print("Master password updated and vault re-encrypted.")
                
        elif choice == "6":
            clear_screen()
            print("Logging out...")
            return "logout"  # return to login
            
        elif choice == "7":
            clear_screen()
            print("Goodbye.")
            return "exit"
        else:
            print("Invalid option.")

        # Check for lock before continuing
        if SESSION_LOCKED.is_set():
            clear_screen()
            print("\n[!] Session locked due to inactivity. Please re-login.")
            return "locked"
            
        input("\nPress Enter to continue...")
        reset_timer()

def main():
    clear_screen()
    ensure_users_dir()
    print("Welcome to Lox (Your personal vault, in your terminal)")

    while True:
        user_path_selected, is_new_user = choose_user_interactive()

        master_hash_path = os.path.join(user_path_selected, 'master.hash')
        salt_path = os.path.join(user_path_selected, 'salt.bin')

        if is_new_user or not (os.path.exists(master_hash_path) and os.path.exists(salt_path)):
            clear_screen()
            print("No master password found for this user. Set up master password, or use recovery to reset.")
            while True:
                print("\n1) Set master password")
                print("2) Reset using recovery token")
                print("3) Back")
                c = input("Choose: ").strip()
                if c == "1":
                    master_pw, salt = set_master_password(user_path_selected)
                    break
                elif c == "2":
                    master_pw, salt = reset_master_with_recovery(user_path_selected)
                    if master_pw:
                        break
                    else:
                        continue
                elif c == "3":
                    break
                else:
                    print("Invalid option.")

            if not os.path.exists(master_hash_path) or not os.path.exists(salt_path):
                # maybe user chose back — go to user selection again
                continue
        else:
            master_pw, salt = verify_master_password(user_path_selected)
            if master_pw is None:
                # verification failed
                clear_screen()
                print("\n1) Try again")
                print("2) Reset using recovery token")
                print("3) Back to user selection")
                c = input("Choose: ").strip()
                if c == "1":
                    continue
                elif c == "2":
                    master_pw, salt = reset_master_with_recovery(user_path_selected)
                    if not master_pw:
                        continue
                else:
                    continue

        # got master password and salt; get fernet and enter menu
        fernet = get_fernet_key(master_pw, salt)
        result = menu(fernet, user_path_selected)

        # Handle different menu return values
        if result == "locked":
            clear_screen()
            print("Session locked. Please re-login.")
            continue  # Go back to password verification
        elif result == "logout" or result == "retry":
            # user logged out normally or needs to retry — offer options
            clear_screen()
            print("\n1) Login again")
            print("2) Choose another user") 
            print("3) Exit")
            c = input("Choose: ").strip()
            clear_screen()
            if c == "1":
                continue  # Go back to password verification for same user
            elif c == "2":
                continue  # Will go to user selection
            else:
                clear_screen()
                print("Goodbye.")
                break
        elif result == "exit":
            break
        else:
            # Default case - treat as logout
            continue

if __name__ == "__main__":
    main()