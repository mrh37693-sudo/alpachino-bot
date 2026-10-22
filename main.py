import os, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1776655781
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is Alive!"

ASK_ID, ASK_PAYMENT = range(2)
PACKAGES = {
    "110 💎": "6,000 جنيه",
    "210 💎": "11,000 جنيه",
    "530 💎": "26,000 جنيه",
    "1080 💎": "51,000 جنيه",
    "2200 💎": "100,000 جنيه"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(f"{p} - {pr}", callback_data=p)] for p, pr in PACKAGES.items()]
    await update.message.reply_text("🔥 *متجر آلباتشينو* 🔥\nاختر الباقة:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def choose_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data['pack'] = q.data
    await q.message.reply_text(f"اخترت {q.data}\n📝 أرسل ID فري فاير:")
    return ASK_ID

async def ask_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ff_id'] = update.message.text
    keyboard = [[InlineKeyboardButton("بنكك", callback_data="bankak")],[InlineKeyboardButton("رصيد", callback_data="raseed")]]
    await update.message.reply_text(f"ID: {update.message.text}\nاختر الدفع:", reply_markup=InlineKeyboardMarkup(keyboard))
    return ASK_PAYMENT

async def ask_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    pack = context.user_data['pack']
    ff_id = context.user_data['ff_id']
    u = q.from_user
    if q.data == "bankak":
        await q.message.reply_text("🏦 بنكك: 1234567 - محمد\nرسل الاشعار هنا ✅")
    else:
        await q.message.reply_text("📱 زين: 090xxxxxxx\nرسل لقطة الشاشة هنا ✅")
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"طلب جديد 🔥\n👤 @{u.username} ({u.id})\n📦 {pack}\n🆔 {ff_id}\n💳 {q.data}")
    except Exception as e:
        print(f"Admin send error: {e}")
    return ConversationHandler.END

def run_bot():
    if not TOKEN:
        print("ERROR: BOT_TOKEN IS EMPTY!")
        return
    print(f"Starting bot with token ...{TOKEN[-10:]}")
    application = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(entry_points=[CallbackQueryHandler(choose_pack)], states={ASK_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_id)], ASK_PAYMENT: [CallbackQueryHandler(ask_payment)]}, fallbacks=[])
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv)
    application.run_polling()

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
