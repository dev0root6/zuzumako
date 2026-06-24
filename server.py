import os, json, time, asyncio, threading
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from telethon import TelegramClient
from dotenv import load_dotenv

BASE     = Path(__file__).parent
load_dotenv(BASE / "config" / ".env")

API_ID   = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
OTP_TTL  = int(os.getenv("OTP_TTL_SECONDS", "60"))
OTP_FILE = BASE / "otp_store.txt"
TEMP_DIR = BASE / "_temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Clear stale temp sessions on startup to avoid AuthRestartError
for f in TEMP_DIR.glob("*.session*"):
    f.unlink(missing_ok=True)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_state: dict = {}   # phone -> { loop, client, phone_code_hash }

class PhoneReq(BaseModel):
    phone: str

class OTPReq(BaseModel):
    phone: str
    code: str

# ── Run Telethon coroutines on a dedicated thread/loop ────────────────────────
# uvicorn uses uvloop which conflicts with Telethon's asyncio usage.
# Each phone gets its own persistent thread + event loop for the duration
# of the auth session.

def _start_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=loop.run_forever, daemon=True)
    t.start()
    return loop

def _run(loop: asyncio.AbstractEventLoop, coro):
    fut = asyncio.run_coroutine_threadsafe(coro, loop)
    return fut.result(timeout=30)

# ── Routes ────────────────────────────────────────────────────────────────────

@app.post("/api/send-code")
async def send_code(req: PhoneReq):
    phone = req.phone.strip().replace(" ", "")

    # Clean up any previous session for this phone
    if phone in _state:
        try:
            old = _state.pop(phone)
            _run(old["loop"], old["client"].disconnect())
            old["loop"].call_soon_threadsafe(old["loop"].stop)
        except Exception:
            pass

    loop = _start_loop()

    async def _do():
        client = TelegramClient(
            str(TEMP_DIR / phone.replace("+", "")),
            API_ID, API_HASH,
            loop=loop
        )
        await client.connect()
        result = await client.send_code_request(phone)
        return client, result.phone_code_hash

    try:
        client, pch = _run(loop, _do())
        _state[phone] = {"loop": loop, "client": client, "phone_code_hash": pch}
        return {"status": "code_sent"}
    except Exception as e:
        loop.call_soon_threadsafe(loop.stop)
        raise HTTPException(500, str(e))


@app.post("/api/store-otp")
async def store_otp(req: OTPReq):
    phone = req.phone.strip().replace(" ", "")
    if phone not in _state:
        raise HTTPException(400, "Session expired. Re-enter your phone number.")

    now = time.time()
    entry = {
        "phone":      phone,
        "otp":        req.code.strip(),
        "stored_at":  now,
        "expires_at": now + OTP_TTL,
        "ttl_sec":    OTP_TTL,
        "expired":    False,
        "phone_code_hash": _state[phone]["phone_code_hash"]
    }

    entries = []
    if OTP_FILE.exists():
        try:
            entries = json.loads(OTP_FILE.read_text())
        except Exception:
            entries = []
    entries = [e for e in entries if e.get("phone") != phone]
    entries.append(entry)
    OTP_FILE.write_text(json.dumps(entries, indent=2))

    # Disconnect and clean up the thread
    state = _state.pop(phone)
    try:
        _run(state["loop"], state["client"].disconnect())
    except Exception:
        pass
    state["loop"].call_soon_threadsafe(state["loop"].stop)

    return {"status": "stored", "expires_in": OTP_TTL}


@app.get("/api/ttl")
async def get_ttl(phone: str):
    phone = phone.strip().replace(" ", "")
    if not OTP_FILE.exists():
        raise HTTPException(404, "No OTP store found.")
    try:
        entries = json.loads(OTP_FILE.read_text())
    except Exception:
        raise HTTPException(500, "Corrupt OTP store.")
    entry = next((e for e in entries if e["phone"] == phone), None)
    if not entry:
        raise HTTPException(404, "No entry for this number.")

    remaining = max(0, entry["expires_at"] - time.time())
    if remaining == 0 and not entry.get("expired"):
        entry["expired"] = True
        OTP_FILE.write_text(json.dumps(entries, indent=2))

    return {"remaining": int(remaining), "expired": remaining == 0}


app.mount("/", StaticFiles(directory=str(BASE / "ui"), html=True), name="ui")
