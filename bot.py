import asyncio, requests, threading
from telegram import Bot
from datetime import datetime, timedelta, timezone
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

TOKEN = "9266653853:AAFpf9kwzoyvspyGzl9tx_swERivkHXYB0Y"
CHAT = "@brightfx555"

PAIRS = [
 ("EUR/USD", "EURUSD=X", "🇪🇺 / 🇺🇸"),
 ("GBP/USD", "GBPUSD=X", "🇬🇧 / 🇺🇸"),
 ("USD/JPY", "USDJPY=X", "🇺🇸 / 🇯🇵"),
 ("AUD/USD", "AUDUSD=X", "🇦🇺 / 🇺🇸"),
 ("USD/CAD", "USDCAD=X", "🇺🇸 / 🇨🇦"),
 ("USD/CHF", "USDCHF=X", "🇺🇸 / 🇨🇭"),
 ("NZD/USD", "NZDUSD=X", "🇳🇿 / 🇺🇸"),
 ("EUR/GBP", "EURGBP=X", "🇪🇺 / 🇬🇧"),
 ("EUR/JPY", "EURJPY=X", "🇪🇺 / 🇯🇵"),
 ("GBP/JPY", "GBPJPY=X", "🇬🇧 / 🇯🇵"),
 ("AUD/JPY", "AUDJPY=X", "🇦🇺 / 🇯🇵"),
 ("CHF/JPY", "CHFJPY=X", "🇨🇭 / 🇯🇵"),
 ("EUR/AUD", "EURAUD=X", "🇪🇺 / 🇦🇺"),
 ("GBP/AUD", "GBPAUD=X", "🇬🇧 / 🇦🇺"),
 ("AUD/CAD", "AUDCAD=X", "🇦🇺 / 🇨🇦"),
 ("AUD/CHF", "AUDCHF=X", "🇦🇺 / 🇨🇭"),
 ("CAD/JPY", "CADJPY=X", "🇨🇦 / 🇯🇵"),
 ("NZD/JPY", "NZDJPY=X", "🇳🇿 / 🇯🇵"),
 ("EUR/CAD", "EURCAD=X", "🇪🇺 / 🇨🇦"),
 ("GBP/CAD", "GBPCAD=X", "🇬🇧 / 🇨🇦"),
 ("EUR/CHF", "EURCHF=X", "🇪🇺 / 🇨🇭"),
 ("GBP/CHF", "GBPCHF=X", "🇬🇧 / 🇨🇭"),
 ("NZD/CAD", "NZDCAD=X", "🇳🇿 / 🇨🇦"),
 ("AUD/NZD", "AUDNZD=X", "🇦🇺 / 🇳🇿"),
 ("EUR/NZD", "EURNZD=X", "🇪🇺 / 🇳🇿"),
]

async def run():
    bot = Bot(token=TOKEN)
    print("Bot don start... 25 PAIRS, 3 Sessions")
    while True:
        try:
            now = datetime.now(timezone(timedelta(hours=1)))
            h = now.hour
            if not (h in [9, 10, 15, 16, 17, 21, 22]):
                print(f"Outside session {now.strftime('%I:%M %p')} - Sleeping")
                await asyncio.sleep(60)
                continue
            entry = (now + timedelta(minutes=2)).replace(second=0, microsecond=0)
            end = entry + timedelta(minutes=2)
            l1 = end
            l2 = end + timedelta(minutes=2)
            fmt = lambda d: d.strftime('%I:%M %p').lstrip('0')
            best = None
            for name, sym, flag in PAIRS:
                try:
                    u = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1d&interval=2m"
                    d = None
                    for _ in range(3):
                        try:
                            d = requests.get(u, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()
                            break
                        except:
                            await asyncio.sleep(2)
                    if not d:
                        continue
                    c = d["chart"]["result"][0]["indicators"]["quote"][0]["close"]
                    c = [x for x in c if x][-100:]
                    g = [max(c[i]-c[i-1], 0) for i in range(1, len(c))]
                    l = [max(c[i-1]-c[i], 0) for i in range(1, len(c))]
                    a = sum(g[-14:])/14; b = sum(l[-14:])/14
                    r = 100-(100/(1+a/b)) if b else 50
                    if r < 30:
                        conf = int(min(95, 75 + (30-r)*1.2))
                        direction = "HIGHER ⬆️"; box = "🟩"
                    elif r > 70:
                        conf = int(min(95, 75 + (r-70)*1.2))
                        direction = "LOWER ⬇️"; box = "🟥"
                    else:
                        continue
                    if conf < 82:
                        continue
                    if best is None or conf > best[0]:
                        best = (conf, name, flag, direction, box)
                except Exception as e:
                    print(name, "Error", e)
                await asyncio.sleep(1)
            if best:
                conf, name, flag, direction, box = best
                m = f"""🚀 SPECIAL AI SIGNAL

🤖 AI Confidence: {conf}%
📈 {name} (REAL) {flag}
🕒 Timeframe: 2 min expiry
⏰ Entry Time: {fmt(entry)} - {fmt(end)}
{box} {direction}

📊 Martingale level:
- Level 1 → {fmt(l1)}
- Level 2 → {fmt(l2)}
🛑 STOP at Level 2 - Good Profit Prediction ✅

💰 Profit Plan: Win Level 1 = +85% | Win Level 2 = Cover + Profit, STOP"""
                await bot.send_message(chat_id=CHAT, text=m)
                print("Sent BEST", name, conf, "Entry", fmt(entry))
            else:
                print("No strong signal this round")
        except Exception as e:
            print("Error", e)
        await asyncio.sleep(300)

asyncio.run(run())
