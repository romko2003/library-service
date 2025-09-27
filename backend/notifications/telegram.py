import os, requests
BOT = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text: str) -> None:
    if not (BOT and CHAT): return
    url = f"https://api.telegram.org/bot{BOT}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT, "text": text}, timeout=5)
    except Exception:
        pass