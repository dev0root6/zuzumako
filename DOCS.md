# Telegram API & Telethon Integration Documentation

This document explains the specific Telegram API calls and Telethon methods used within Zuzumako for authentication, contact retrieval, message broadcasting, and message deletion.

---

## 1. Session Setup and Lifecycle

### Client Initialization
```python
from telethon import TelegramClient

client = TelegramClient(session_path, api_id, api_hash, loop=loop)
```
- **Description**: Creates a Telethon client instance. 
- **Arguments**:
  - `session_path`: String or `Path` to the `.session` SQLite database where authorization keys, server addresses, and entities are cached.
  - `api_id` / `api_hash`: Developer credentials obtained from the Telegram portal.
  - `loop`: Custom event loop. In Zuzumako, we spin up separate event loops on background threads to prevent conflicts with FastAPI's main asyncio loop.

---

## 2. Authentication Flow

### Connection
```python
await client.connect()
```
- **Description**: Connects to Telegram's servers. Must be invoked before issuing API requests.

### Requesting Login Code (OTP)
```python
result = await client.send_code_request(phone)
phone_code_hash = result.phone_code_hash
```
- **Description**: Requests Telegram to send an SMS or in-app verification code to the target phone number.
- **Return Type**: `SentCode` object containing metadata about the sent code.
- **Key Field**: `phone_code_hash` is a unique string tracking this specific OTP request. It is required to finalize the authentication sign-in.

### Completing Authentication
```python
await client.sign_in(phone, otp, phone_code_hash=phone_code_hash)
```
- **Description**: Completes the sign-in procedure using the received OTP code and the tracking `phone_code_hash`.
- **Throws**: `SessionPasswordNeededError` if Two-Factor Authentication (2FA) is active.

### Handling Two-Factor Authentication (2FA)
```python
try:
    await client.sign_in(phone, otp, phone_code_hash=phone_code_hash)
except SessionPasswordNeededError:
    pw = input("2FA password: ")
    await client.sign_in(password=pw)
```
- **Description**: If 2FA is enabled, a secondary `sign_in` call passing the `password` argument is executed to unlock the session.

---

## 3. Account Metadata

### Get Me
```python
me = await client.get_me()
first_name = me.first_name
username = me.username
```
- **Description**: Queries the account owner's user object.
- **Return Type**: `User` object. Used to log successful authentication and verify session validity.

---

## 4. Contact Management

### Get Contacts List
```python
from telethon.tl.functions.contacts import GetContactsRequest

result = await client(GetContactsRequest(hash=0))
contacts = [u for u in result.users if not u.bot and not u.is_self]
```
- **Description**: Calls the low-level Telegram API function `contacts.getContacts`. 
- **Filtering**: We filter `result.users` to exclude bot accounts (`u.bot`) and the authorized user's own profile (`u.is_self`).

---

## 5. Message Interactions

### Get Entity
```python
entity = await client.get_entity(contact_id)
```
- **Description**: Resolves a contact ID, username, or phone number into a full peer entity (User, Chat, or Channel). Resolving entities is required before sending messages to ensure Telethon can construct the correct peer parameters.

### Sending Message
```python
msg = await client.send_message(entity, message_text)
message_id = msg.id
```
- **Description**: Sends a direct text message to the target peer.
- **Return Type**: `Message` object.
- **Key Field**: `msg.id` is cached to enable remote deletion.

### Message History Iteration
```python
async for msg in client.iter_messages(chat_peer, limit=50):
    if msg.sender_id == me.id:
        # Action
```
- **Description**: Crawls through recent messages in a chat. We filter messages where `sender_id == me.id` to identify and target messages sent by the logged-in bot user.

### Deleting and Revoking Messages
```python
await client.delete_messages(entity, [message_id], revoke=True)
```
- **Description**: Deletes a list of message IDs from a specific chat.
- **Arguments**:
  - `revoke`: When set to `True`, the message is deleted for **both** the sender and the recipient (delete-for-everyone / unsend). If `False`, it is only deleted from the sender's chat history.
