#!/bin/bash
cd "$(dirname "$0")"

echo "╔══════════════════════════════════════╗"
echo "║             zuzumako                 ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Cleanup on exit ───────────────────────────────────────────────────────────
cleanup() {
    echo ""
    echo "[zuzumako] Shutting down…"
    kill $PID_SERVER $PID_WATCHER 2>/dev/null
    wait $PID_SERVER $PID_WATCHER 2>/dev/null
    echo "[zuzumako] All processes stopped."
    exit 0
}
trap cleanup SIGINT SIGTERM

# ── Start Zuzumako server ─────────────────────────────────────────────────────
echo "[1/2] Starting Zuzumako UI    → http://127.0.0.1:8001"
uvicorn server:app --host 127.0.0.1 --port 8001 --reload &
PID_SERVER=$!
sleep 2

# ── Start watcher ─────────────────────────────────────────────────────────────
echo "[2/2] Starting watcher        → scanning otp_store.txt every 2s"
python watcher.py &
PID_WATCHER=$!

echo ""
echo "  UI        → http://127.0.0.1:8001"
echo "  Send      → python send.py --to +91XXXXXXXXXX --msg 'hello'"
echo "  Delete    → python delete.py --to +91XXXXXXXXXX --match 'text'"
echo "  Broadcast → python broadcast.py"
echo ""
echo "  Press Ctrl+C to stop all processes."
echo ""

# ── Wait for both ─────────────────────────────────────────────────────────────
wait $PID_SERVER $PID_WATCHER
