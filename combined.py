"""
combined.py — Menjalankan Flask API + Telegram Bot dalam satu proses
Flask berjalan di main thread (agar Railway health check terpenuhi)
Bot Telegram berjalan di background thread
"""

import threading
import asyncio
import os
from api import app, init_db


def run_bot():
    """Jalankan bot Telegram di background thread dengan event loop sendiri."""
    from bot_v4 import main as bot_main
    print("[BOT] Telegram bot berjalan di background thread...")
    # Buat event loop baru untuk thread ini
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        bot_main()
    except Exception as e:
        print(f"[BOT] Error: {e}")


if __name__ == "__main__":
    # 1. Inisialisasi database
    init_db()

    # 2. Jalankan bot di background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("[BOT] Thread bot dimulai.")

    # 3. Jalankan Flask di main thread (Railway health check butuh ini)
    from waitress import serve
    port = int(os.environ.get("PORT", 8080))
    print(f"[API] Flask berjalan di port {port}...")
    serve(app, host="0.0.0.0", port=port)

