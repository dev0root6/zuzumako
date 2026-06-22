# Zuzumako

Zuzumako is a self-contained Telegram automation and session-management system. It features a modern, card-based web frontend styled to mirror the **Telegram Web K** sign-in interface, coupled with a robust FastAPI backend. It streamlines session creation using Telethon, stores OTP credentials temporarily, and automates tasks such as direct-message broadcasting, message scheduling, sending, and remote deletion.

---

## Features

- **Web K Interface**: Responsive, premium dark-themed web page for easy phone number submission and OTP entry.
- **Multithreaded Session Handling**: Runs Telegram authentication sessions on isolated event loops on dedicated threads, avoiding conflict with the FastAPI web server.
- **Background Automation Watcher**: Auto-scans for new credentials and triggers custom broadcasts to contacts.
- **Dynamic Messaging Control**: Broadcaster with customizable delay limits, message count caps, and interactive revocation (delete-for-everyone).
- **Session Exports**: Saves permanent Telethon session files (`.session`) to a dedicated directory for reuse in external automation scripts.

---

## Repository Structure

- `server.py`: FastAPI backend that hosts the web client, handles static assets, and drives the initial Telethon connection flow (sending OTP requests).
- `watcher.py`: Background worker that monitors `otp_store.txt` for newly entered OTPs, finishes authentication, saves session files, and runs automated broadcasts.
- `auth.py`: CLI-based authentication script for manual workflows. Handles 2FA (Two-Factor Authentication) prompts.
- `automater.py`: Script to trigger broadcasts for all active session profiles registered in the system.
- `broadcast.py`: Modular utility to send direct messages to contact lists and auto-delete them after a defined cooldown.
- `send.py`: Simple utility to send direct messages to users, groups, or "me" using existing sessions.
- `delete.py`: Utility to search chat history and delete matching messages.
- `run.sh`: Bash script to orchestrate and run both the web server and the background watcher process.
- `ui/`: Frontend assets (HTML, custom CSS, background wallpaper, logos).
- `config/.env`: Core environment variables (API ID, API Hash, etc.).
- `otp_store.txt`: Temporary JSON data store for staging phone numbers, OTPs, hashes, and expiration timestamps.

---

## Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher.
- A Telegram application credentials pair (`api_id` and `api_hash`). You can obtain these from [my.telegram.org](https://my.telegram.org/).

### 2. Install Dependencies
Clone the repository and install the required packages:
```bash
pip install fastapi uvicorn telethon python-dotenv
```

### 3. Configuration
Create a `.env` file under the `config/` directory:
```bash
mkdir -p config
touch config/.env
```

Add the following environment variables to `config/.env`:
```ini
TELEGRAM_API_ID=123456            # Your Telegram API ID
TELEGRAM_API_HASH=your_api_hash   # Your Telegram API Hash
OTP_TTL_SECONDS=120               # How long OTPs remain valid in the store (default: 60)
BROADCAST_LIMIT=5                 # Limit of contacts to message ('all' or integer)
BROADCAST_DELAY_SECONDS=60        # Delay before deleting broadcast messages
BROADCAST_REVOKE=true             # Whether to delete messages for the recipient too
```

---

## Operating Instructions

### Quick Start (Server + Watcher)
Run the orchestrator script to spin up the web server and background watcher simultaneously:
```bash
chmod +x run.sh
./run.sh
```
This launches:
1. **Web UI** at `http://127.0.0.1:8001`
2. **Watcher** process monitoring OTP submissions.

---

### Step-by-Step Walkthrough

#### Step 1: Request OTP
1. Open `http://127.0.0.1:8001` in your browser.
2. Select your country code and enter your Telegram phone number (e.g., `+919999999999`).
3. Click "Next". The backend creates a temporary Telethon client and requests an authentication code from Telegram.

#### Step 2: Submit OTP
1. Enter the login code received on your Telegram app.
2. Click "Submit".
3. The server saves the OTP, phone number, and unique Telegram `phone_code_hash` to `otp_store.txt` and starts a countdown timer on the UI.

#### Step 3: Session Creation & Automatic Broadcast
1. The running `watcher.py` process catches the new entry in `otp_store.txt`.
2. It uses the stored credentials to authenticate the Telegram session.
3. The `.session` file is saved inside the `sessions/` directory.
4. If the user doesn't have 2FA enabled, the watcher immediately sends the broadcast message configured in `broadcast.py` (or `watcher.py`) to the user's contacts and schedules their deletion.

---

## CLI Utilities

You can also run various operations manually via command line:

### 1. Manual Authentication & 2FA Support
If the account has Two-Factor Authentication (2FA) enabled, the automatic watcher cannot bypass the password prompt. You must complete the login manually:
```bash
python auth.py --phone +919999999999
```
It will read the OTP from the store and prompt you inside the terminal to enter your 2FA password.

### 2. Manual Broadcast
To trigger a broadcast manually for all stored profiles:
```bash
python automater.py
```
Or to run a broadcast using the primary saved session:
```bash
python broadcast.py --delay 30
```
Use the `--dry-run` flag to preview matching contacts without sending any messages:
```bash
python broadcast.py --dry-run
```

### 3. Send Message
To send a message using the active session:
```bash
python send.py --to +91XXXXXXXXXX --msg "Hello from Zuzumako"
python send.py --to @username --msg "Hello"
python send.py --to me --msg "Notes to self"
```

### 4. Delete Messages
To delete the last message you sent in a chat:
```bash
python delete.py --to +91XXXXXXXXXX --last
```
To delete all messages matching a specific keyword in a chat:
```bash
python delete.py --to +91XXXXXXXXXX --match "bot"
```
