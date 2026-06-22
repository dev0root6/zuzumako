#!/usr/bin/env python3
"""
zuzumako / delete.py
─────────────────────
Deletes a message from your Telegram account by matching content.

Usage:
  python delete.py --to +91XXXXXXXXXX --match "hello"
  python delete.py --to +91XXXXXXXXXX --last          # delete last sent msg
"""

import argparse, sys, os, asyncio
from pathlib import Path
from dotenv import load_dotenv

BASE     = Path(__file__).parent
load_dotenv(BASE / "config" / ".env")

API_ID   = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSIONS = BASE / "sessions"

def get_session():
    sessions = list(SESSIONS.glob("*.session"))
    if not sessions:
        sys.exit("✗  No session found. Run auth.py first.")
    return str(sessions[0]).replace(".session", "")

async def do_delete(to, match, last, limit):
    from telethon import TelegramClient

    session = get_session()

    async with TelegramClient(session, API_ID, API_HASH) as client:
        me = await client.get_me()

        print(f"[delete] Searching messages in chat with {to}…")
        deleted = 0

        async for msg in client.iter_messages(to, limit=limit):
            # Only look at messages sent by me
            if msg.sender_id != me.id:
                continue

            if last:
                await msg.delete()
                print(f"[delete] ✓  Deleted last sent message: \"{msg.text}\"")
                return

            if match and match.lower() in (msg.text or "").lower():
                await msg.delete()
                print(f"[delete] ✓  Deleted: \"{msg.text}\"")
                deleted += 1

        if not last and deleted == 0:
            print(f"[delete] ✗  No message matching \"{match}\" found in last {limit} messages.")
        elif not last:
            print(f"[delete] Done — {deleted} message(s) deleted.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--to",    required=True, help="Chat to search in (phone, @username, or 'me')")
    parser.add_argument("--match", default=None,  help="Text to match against your sent messages")
    parser.add_argument("--last",  action="store_true", help="Delete the last message you sent")
    parser.add_argument("--limit", type=int, default=50, help="How many messages to scan (default 50)")
    args = parser.parse_args()

    if not args.match and not args.last:
        sys.exit("✗  Provide either --match 'text' or --last")

    asyncio.run(do_delete(args.to, args.match, args.last, args.limit))

if __name__ == "__main__":
    main()
