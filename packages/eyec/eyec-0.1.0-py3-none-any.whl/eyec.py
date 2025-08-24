#!/usr/bin/env python3
import pyperclip
import time
import sys
import os

HISTORY_FILE = os.path.expanduser("~/.clipboard_history")

def monitor_clipboard():
    seen = set()
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            seen.update(line.strip() for line in f)

    print("[*] Welcome to Doom-s Clipboard \\\n  monitor started. Press Ctrl+C to stop.")
    try:
        while True:
            text = pyperclip.paste()
            if text and text not in seen:
                seen.add(text)
                with open(HISTORY_FILE, "a") as f:
                    f.write(text + "\n")
                print(f"[+] New entry saved: {text}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Exiting...")

def search_history(term):
    if not os.path.exists(HISTORY_FILE):
        print("No history yet.")
        return
    with open(HISTORY_FILE, "r") as f:
        matches = [line.strip() for line in f if term.lower() in line.lower()]
    if matches:
        print("\n".join(matches))
    else:
        print(f"No matches for '{term}'")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        if len(sys.argv) < 3:
            print("Usage: eyec search <term>")
        else:
            search_history(sys.argv[2])
    else:
        monitor_clipboard()

if __name__ == "__main__":
    main()
