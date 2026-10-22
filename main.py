import os, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1776655781
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is Alive!"

# الأسعار الجديدة من MooGold
PACKAGES = {
    "50 💎": "$0.50 - 1,500ج",
    "70 💎": "$0.70 - 2,000ج",
    "140 💎": "$1.40 - 4,000ج",
    "355 💎": "$3.00 - 9,000ج",
    "720 💎": "$6.00 - 18,000ج",
    "عضوية اسبوعية 🔥": "$2.00 - 6,000ج"
}

user_data_temp = {}
PHOTO_URL = "https://cdn.moogold.com/2023/09/Free-Fire-Diamond.jpg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(f"{p}", callback_data=f"pack:{p}")] for p in PACKAGES.keys()]
    # نرسل الصورة مع الباقات
    try:
        await update.message.reply_photo(
            photo=PHOTO_URL,
            caption="🔥 *متجر آلباتشينو - Free Fire* 🔥\nاختر الباقة:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except:
        await update.message.reply_text("🔥 *متجر آلباتشينو* 🔥\nاختر الباقة:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.from_user.id

    if data.startswith("pack:"):
        pack = data.split("pack:")[1]
        user_data_temp[chat_id] = {"pack": pack}
        await query.message.reply_text(f"اخترت {pack}\n📝 أرسل ID فري فاير حقك:")
    elif data in ["bankak", "raseed"]:
        info = user_data_temp.get(chat_id, {})
        pack = info.get("pack", "غير محدد")
        ff_id = info.get("ff_id", "غير محدد")
        if data == "bankak":
            await query.message.reply_text("🏦 *بنكك:* 1234567 - محمد\nبعد تحول رسل الاشعار هنا ✅", parse_mode='Markdown')
        else:
            await query.message.reply_text("📱 *زين:* 090xxxxxxx\nبعد تحول رسل لقطة الشاشة هنا ✅", parse_mode='Markdown')
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"طلب جديد 🔥\n👤 @{query.from_user.username} ({chat_id})\n📦 {pack}\n🆔 {ff_id}\n💳 {data}")
        except Exception as e:
            print(e)

async def handle_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    text = update.message.text
    if chat_id not in user_data_temp:
        await update.message.reply_text("دوس /start أولا")
        return
    user_data_temp[chat_id]["ff_id"] = text
    keyboard = [[InlineKeyboardButton("🏦 بنكك", callback_data="bankak")],[InlineKeyboardButton("📱 رصيد", callback_data="raseed")]]
    await update.message.reply_text(f"ID حقك: {text}\nاختر طريقة الدفع:", reply_markup=InlineKeyboardMarkup(keyboard))

def run_bot():
    if not TOKEN:
        print("BOT_TOKEN EMPTY!")
        return
    print("Starting bot...")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id))
    # ده أهم سطر بخلي البوت يمسح الويب هوك القديم ويشتغل
    application.run_polling(drop_pending_updates=True)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
