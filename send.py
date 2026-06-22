#!/usr/bin/env python3
"""
zuzumako / send.py
───────────────────
Sends a message using the saved Telethon session.
No phone number required — picks the session automatically.

Usage:
  python send.py --to +919019616856 --msg "hello"
  python send.py --to @username --msg "hello"
  python send.py --to me --msg "hello"
"""

import argparse, sys, os
from pathlib import Path
from dotenv import load_dotenv

BASE = Path(__file__).parent
load_dotenv(BASE / "config" / ".env")

API_ID   = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSIONS = BASE / "sessions"

def get_session():
    sessions = list(SESSIONS.glob("*.session"))
    if not sessions:
        sys.exit("✗  No session found. Run auth.py first.")
    # If multiple sessions, pick the first one
    return str(sessions[0]).replace(".session", "")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--to",  required=True, help="Recipient phone, @username, or 'me'")
    parser.add_argument("--msg", required=True, help="Message text")
    args = parser.parse_args()

    session = get_session()
    print(f"[send] → {args.to}")

    from telethon.sync import TelegramClient
    with TelegramClient(session, API_ID, API_HASH, sequential_updates=True) as client:
        client.send_message(args.to, args.msg)
        print(f"[send] ✓  Sent.")

if __name__ == "__main__":
    main()
