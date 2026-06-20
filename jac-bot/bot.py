#!/usr/bin/env python3
"""
jac — AI Telegram bot (bepul).
Telegram <-> AI miyya (Groq bepul, yoki mahalliy Ollama).
Faqat `requests` kerak. Server kerak emas — noutbukda ishlaydi.
"""
import os, time, requests

# =================== SOZLAMALAR ===================
# 1) Telegram bot token (@BotFather dan olinadi)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "BU_YERGA_TELEGRAM_TOKEN")

# 2) Miyya: "groq" (bepul, internet) yoki "ollama" (mahalliy, oflayn)
PROVIDER = os.environ.get("JAC_PROVIDER", "groq")

# Groq — bepul, karta shart emas:  https://console.groq.com  -> API Keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "BU_YERGA_GROQ_KEY")
GROQ_MODEL   = "llama-3.3-70b-versatile"   # model o'zgarsa console.groq.com dan tekshiring

# Ollama — mahalliy/oflayn (xohlasangiz): https://ollama.com  ->  ollama run qwen2.5:3b
OLLAMA_URL   = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:3b"

# jac shaxsiyati
SYSTEM_PROMPT = (
    "Sen 'jac' — do'stona, halol va foydali AI yordamchisan. "
    "O'zbek tilida, sodda va aniq javob ber. Ortiqcha cho'zma. "
    "Bilmagan narsangni to'g'ri ayt, o'ylab topma. Kerak bo'lsa misol bilan tushuntir."
)

HISTORY_LEN = 8          # har foydalanuvchi uchun eslab qolinadigan xabarlar
histories = {}           # chat_id -> [{role, content}, ...]
API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# =================== MIYYA (AI) ===================
def ai_reply(messages):
    """messages: [{'role','content'}...]  ->  javob matni"""
    if PROVIDER == "ollama":
        r = requests.post(OLLAMA_URL,
                          json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
                          timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    # groq (OpenAI-mos endpoint)
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": GROQ_MODEL, "messages": messages, "temperature": 0.7},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

def get_reply(chat_id, text):
    hist = histories.get(chat_id, [])
    hist.append({"role": "user", "content": text})
    hist = hist[-HISTORY_LEN:]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + hist
    try:
        answer = ai_reply(messages)
    except Exception as e:
        return f"Kechirasiz, miyya bilan aloqa uzildi: {e}"
    hist.append({"role": "assistant", "content": answer})
    histories[chat_id] = hist[-HISTORY_LEN:]
    return answer

# =================== TELEGRAM ===================
def send(chat_id, text):
    try:
        requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=20)
    except Exception as e:
        print("send xato:", e)

def main():
    if "BU_YERGA" in TELEGRAM_TOKEN or (PROVIDER == "groq" and "BU_YERGA" in GROQ_API_KEY):
        print("⚠️  Avval bot.py dagi TELEGRAM_TOKEN va GROQ_API_KEY ni to'ldiring!")
        return
    print("✅ jac bot ishga tushdi. Telegram'da botingizga yozing. (to'xtatish: Ctrl+C)")
    offset = None
    while True:
        try:
            r = requests.get(f"{API}/getUpdates",
                            params={"timeout": 30, "offset": offset}, timeout=40)
            for u in r.json().get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message") or u.get("edited_message")
                if not msg:
                    continue
                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                if not text:
                    continue
                if text.strip() == "/start":
                    histories[chat_id] = []
                    send(chat_id, "Salom! Men jac — sizning AI yordamchingiz 🤖\nIstalgan savolni bering.")
                    continue
                send(chat_id, get_reply(chat_id, text))
        except KeyboardInterrupt:
            print("\nTo'xtatildi.")
            break
        except Exception as e:
            print("Xato:", e)
            time.sleep(3)

if __name__ == "__main__":
    main()
