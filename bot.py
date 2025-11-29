import random
import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
SUBSCRIBERS_FILE = "subscribers.json"
subscribers = set()

def load_subscribers():
    global subscribers
    if os.path.exists(SUBSCRIBERS_FILE):
        try:
            with open(SUBSCRIBERS_FILE, 'r') as f:
                data = json.load(f)
                subscribers = set(data) if data else set()
        except:
            subscribers = set()
    else:
        subscribers = set()

def save_subscribers():
    with open(SUBSCRIBERS_FILE, 'w') as f:
        json.dump(list(subscribers), f)

def generate_signal():
    grid = [["🟫"] * 5 for _ in range(3)]
    for row in range(3):
        col = random.randint(0, 4)
        grid[row][col] = "🍎"
    grid_str = "\n".join("".join(row) for row in grid)
    
    return f"""✅إشارة جديدة✅

‼️ الإشارة هاتشتغل صح فقط مع الناس الي سجلت حساباتهم ب بروموكود A1VIP علي تطبيق MELBET ولازم تكون عامل ايداع اقل مبلغ 200 جنية.

⏰الإشارة صالحة لمدة دقيقة فقط

✅الإشارة✅

{grid_str}

https://t.me/c/1934476102/253"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in subscribers:
        subscribers.add(user_id)
        save_subscribers()
    await update.message.reply_text("✅ تم تسجيلك!")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in subscribers:
        subscribers.remove(user_id)
        save_subscribers()
    await update.message.reply_text("✅ تم إيقافك")

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_signal())

async def send_signals(context: ContextTypes.DEFAULT_TYPE):
    if not subscribers:
        return
    signal = generate_signal()
    for user_id in list(subscribers):
        try:
            await context.bot.send_message(chat_id=user_id, text=signal)
        except:
            subscribers.discard(user_id)
    save_subscribers()

async def main():
    if not TELEGRAM_BOT_TOKEN:
        print("❌ خطأ: لم يتم تعيين TELEGRAM_BOT_TOKEN")
        return
    
    load_subscribers()
    print(f"✅ تم تحميل {len(subscribers)} مشترك")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("signal", signal_command))
    
    app.job_queue.run_repeating(send_signals, interval=300, first=10)
    
    print("🤖 البوت جاهز ويستقبل الأوامر...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
