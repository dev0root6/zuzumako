# Zuzumako

### Telegram Phishing Simulation & Security Awareness Research

Zuzumako is a cybersecurity research project designed to demonstrate Telegram-themed phishing techniques and the security risks associated with credential harvesting, OTP interception, session authentication, and unauthorized account access.

## Overview

The project demonstrates how a Telegram Web-style authentication interface can be replicated for controlled phishing simulations and security awareness research.

It combines a web interface, FastAPI backend, and Telethon-based authentication components to illustrate the risks associated with entering authentication credentials into untrusted interfaces.

## Research Objectives

- Demonstrate Telegram-themed phishing interface techniques.
- Understand OTP-based authentication workflows.
- Examine the security implications of exposing authentication material.
- Demonstrate risks associated with persistent authentication sessions.
- Study unauthorized messaging and account misuse scenarios.
- Improve phishing awareness and credential security education.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend implementation |
| FastAPI | HTTP API and web server |
| Telethon | Telegram API integration |
| HTML / CSS / JavaScript | Frontend interface |
| AsyncIO | Asynchronous execution |
| Threading | Background execution |
| SQLite | Telethon session storage |

## Repository Structure

```text
zuzumako/
├── auth.py
├── automater.py
├── broadcast.py
├── delete.py
├── run.sh
├── send.py
├── server.py
├── watcher.py
├── DOCS.md
├── README.md
└── ui/
    ├── index.html
    ├── t-wall.png
    └── telegramlogo.png
```

## Architecture

| Component | Description |
|---|---|
| `ui/` | Telegram-themed demonstration interface |
| `server.py` | FastAPI backend and authentication workflow |
| `watcher.py` | Background authentication workflow |
| `auth.py` | Manual authentication component |
| `broadcast.py` | Messaging and deletion demonstration |
| `automater.py` | Session-based automation |
| `send.py` | Direct messaging utility |
| `delete.py` | Message deletion utility |
| `run.sh` | Application startup orchestration |

## Installation

### Prerequisites

- Python 3.8+
- Telegram API ID
- Telegram API Hash
- Linux environment recommended

### Install Dependencies

```bash
pip install fastapi uvicorn telethon python-dotenv
```

### Configuration

Create the configuration directory:

```bash
mkdir -p config
```

Create `config/.env`:

```ini
TELEGRAM_API_ID=YOUR_API_ID
TELEGRAM_API_HASH=YOUR_API_HASH

OTP_TTL_SECONDS=120

BROADCAST_LIMIT=5
BROADCAST_DELAY_SECONDS=60
BROADCAST_REVOKE=true
```

Keep API credentials and authentication material out of version control.

## Running the Application

```bash
chmod +x run.sh
./run.sh
```

The application starts:

- FastAPI server: `http://127.0.0.1:8001`
- Background authentication watcher.

## Security Research Areas

### 1. Phishing Interface Simulation

Demonstrates how familiar authentication interfaces can be replicated to investigate user trust and phishing susceptibility.

### 2. OTP Authentication

Examines OTP-based authentication, authentication hashes, and the risks of exposing verification credentials.

### 3. Session Security

Demonstrates how persistent authentication sessions can introduce account-security risks when improperly protected.

### 4. Social Engineering Awareness

Highlights how attackers can exploit familiar branding and authentication workflows to manipulate users.

### 5. Unauthorized Account Activity

Examines the potential consequences of compromised authentication sessions, including unauthorized messaging and account misuse.

## Security Considerations

The existing implementation handles:

- Phone numbers.
- Telegram OTP values.
- Telegram authentication hashes.
- Persistent Telethon session files.
- Contact information.
- Message-sending and deletion operations.

These are highly sensitive capabilities.

Research deployments must use explicitly authorized test accounts, informed participants, and isolated environments. Do not collect credentials from unsuspecting users or deploy the interface as an official Telegram authentication service.

## Disclaimer

Zuzumako is a cybersecurity research and phishing-awareness demonstration.

It is not affiliated with, endorsed by, or associated with Telegram.

All testing must be conducted in controlled environments with explicit authorization.

**Research Focus:** Phishing Simulation | Credential Security | OTP Authentication | Session Security | Social Engineering Awareness
