import asyncio
import random
import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
SUBSCRIBERS_FILE = "subscribers.json"

subscribers = set()

def load_subscribers():
    global subscribers
    if os.path.exists(SUBSCRIBERS_FILE):
        try:
            with open(SUBSCRIBERS_FILE, 'r') as f:
                subscribers = set(json.load(f))
        except:
            subscribers = set()

def save_subscribers():
    with open(SUBSCRIBERS_FILE, 'w') as f:
        json.dump(list(subscribers), f)

def generate_apple_grid():
    grid = [["🟫"] * 5 for _ in range(3)]
    
    for row in range(3):
        col = random.randint(0, 4)
        grid[row][col] = "🍎"
    
    grid_str = ""
    for row in grid:
        grid_str += "                         " + "".join(row) + "\n"
    return grid_str

def generate_signal():
    grid = generate_apple_grid()
    
    message = """✅إشارة جديدة✅

‼️ الإشارة هاتشتغل صح فقط مع الناس الي سجلت حساباتهم ب بروموكود A1VIP علي تطبيق MELBET ولازم تكون عامل ايداع اقل مبلغ 200 جنية. غير كده الإشارة هاتكون معاك غلط وخسارة.

⏰الإشارة صالحة لمدة دقيقة فقط من نشرها لا تستخدمها بعد مرور دقيقة من نشرها انتظر الاشارة الجديدة بعد 5 دقائق فقط.

🔔فعل اشعارات البوت عشان يوصل لك إشعار عند نشر الإشارة الجديدة. 

✅الإشارة✅

"""
    message += grid
    message += """
شرح طريقة تنزيل تطبيق MELBET والتسجيل ب بروموكود A1VIP وطريقة الايداع الصح عشان الإشارات تشتغل معاك صح وتجيب أرباح. اضغط علي الرابط عشان يحولك للشرح بالتفاصيل 👇من هنا👇
https://t.me/c/1934476102/253"""
    
    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in subscribers:
        await update.message.reply_text("أنت مشترك بالفعل! ستتلقى الإشارات كل 5 دقائق.")
    else:
        subscribers.add(user_id)
        save_subscribers()
        await update.message.reply_text(
            "مرحباً! تم تسجيلك بنجاح.\n"
            "ستتلقى إشارة صحيحة كل 5 دقائق.\n"
            "لإيقاف الإشارات، أرسل /stop"
        )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in subscribers:
        subscribers.remove(user_id)
        save_subscribers()
        await update.message.reply_text("تم إلغاء اشتراكك. لن تتلقى إشارات بعد الآن.\nلإعادة الاشتراك، أرسل /start")
    else:
        await update.message.reply_text("أنت غير مشترك حالياً. للاشتراك، أرسل /start")

async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    signal = generate_signal()
    await update.message.reply_text(signal)

async def send_signals(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    print(f"📤 إرسال الإشارة - الوقت: {now.strftime('%H:%M:%S')}")
    
    signal = generate_signal()
    
    for user_id in list(subscribers):
        try:
            await context.bot.send_message(chat_id=user_id, text=signal)
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")
            subscribers.discard(user_id)
    
    print(f"✅ تم إرسال الإشارة إلى {len(subscribers)} مشترك")

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable is not set!")
        return
    
    load_subscribers()
    print(f"✅ تم تحميل {len(subscribers)} مشترك")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("signal", signal_now))
    
    job_queue = application.job_queue
    job_queue.run_repeating(send_signals, interval=300)
    
    print("🤖 البوت جاهز ويستقبل الأوامر...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()