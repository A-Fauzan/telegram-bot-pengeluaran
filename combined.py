"""
combined.py — Menjalankan Flask API + Telegram Bot dalam satu proses
Bot berjalan di main thread (asyncio), Flask berjalan di background thread (waitress)
"""

import threading
import os
from api import app, init_db


def run_flask():
    """Jalankan Flask API pakai Waitress (production-grade, cocok untuk threading)."""
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    print(f"[API] Flask berjalan di port {port}")
    serve(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    # 1. Inisialisasi database (tambah kolom tipe jika belum ada)
    init_db()

    # 2. Jalankan Flask di background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 3. Jalankan bot Telegram di main thread (blocking — ini yang menjaga proses tetap hidup)
    print("[BOT] Telegram bot berjalan...")
    from bot_v4 import main as bot_main
    bot_main()
