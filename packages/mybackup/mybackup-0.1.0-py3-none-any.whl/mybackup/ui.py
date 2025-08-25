from .core import site_info, create_backup, list_backups, delete_backup
from .utils import is_valid_domain
import json
import datetime

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
CYAN = "\033[96m"

LOG_FILE = "mybackup_session.log"

def log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} - {text}\n")

def print_menu():
    menu = f"""
{GREEN}==========================================
           BACKUP TOOL V2 - Enhanced
==========================================

 [1] Get FULL Website/IP Info
 [2] Create Website Backup (HTML)
 [3] List Backup Files
 [4] Delete Backup File
 [5] View Session Log
 [6] Exit

=========================================={RESET}
"""
    print(menu)

def print_colored(text, color):
    print(f"{color}{text}{RESET}")

def print_site_info(info):
    print_colored("="*50, GREEN)
    for key, val in info.items():
        print_colored(f"\n>>> {key}:", CYAN)
        if isinstance(val, (dict, list)):
            print(json.dumps(val, indent=2))
        else:
            print(val)
    print_colored("="*50, GREEN)

def main_ui():
    while True:
        print_menu()
        choice = input(f"{YELLOW}Enter choice: {RESET}").strip()
        if choice == '1':
            target = input(f"{YELLOW}Enter website (no http/https) or IP: {RESET}").strip()
            if not is_valid_domain(target):
                print_colored("Invalid domain or IP!", RED)
                continue
            print_colored(f"Fetching data for: {target} ...", GREEN)
            info = site_info(target)
            print_site_info(info)
            log(f"INFO fetched for {target}")
        elif choice == '2':
            target = input(f"{YELLOW}Enter website to backup: {RESET}").strip()
            if not is_valid_domain(target):
                print_colored("Invalid domain.", RED)
                continue
            result = create_backup(target)
            print_colored(result, GREEN if "created" in result else RED)
            log(f"Backup result: {result}")
        elif choice == '3':
            backups = list_backups()
            if backups:
                print_colored("Backups available:", CYAN)
                for b in backups:
                    print(b)
            else:
                print_colored("No backups found.", RED)
        elif choice == '4':
            fname = input(f"{YELLOW}Enter backup filename to delete: {RESET}").strip()
            if fname:
                result = delete_backup(fname)
                print_colored(result, GREEN if "Deleted" in result else RED)
                log(f"Delete backup: {result}")
            else:
                print_colored("No filename provided.", RED)
        elif choice == '5':
            print_colored(f"Showing last 20 lines from {LOG_FILE}:", CYAN)
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-20:]
                    for line in lines:
                        print(line.strip())
            except FileNotFoundError:
                print_colored("Log file not found.", RED)
        elif choice == '6':
            print_colored("Exiting. Goodbye!", GREEN)
            break
        else:
            print_colored("Invalid choice. Please select 1-6.", RED)
