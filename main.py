import os, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1776655781
ASK_ID, ASK_PAYMENT = range(2)

# عدل الأسعار هنا حسب سوقك
PACKAGES = {
    "110 💎": "6,000 جنيه",
    "210 💎": "11,000 جنيه",
    "530 💎": "26,000 جنيه",
    "1080 💎": "51,000 جنيه",
    "2200 💎": "100,000 جنيه"
}

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Free Fire Bot Running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for pack, price in PACKAGES.items():
        keyboard.append([InlineKeyboardButton(f"{pack} - {price}", callback_data=pack)])
    keyboard.append([InlineKeyboardButton("💬 تواصل", url="https://t.me/YourUsername")])
    await update.message.reply_text(
        "🔥 *متجر آلباتشينو لشحن جواهر فري فاير* 🔥\n\n"
        "💎 شحن سريع - آمن 100% - خلال 5 دقائق\n"
        "👇 اختر الباقة:",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown'
    )

async def choose_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['pack'] = query.data
    await query.message.reply_text(f"اخترت باقة *{query.data}*\n\n📝 أرسل ID فري فاير حقك:", parse_mode='Markdown')
    return ASK_ID

async def ask_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ff_id'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("بنكك", callback_data="bankak")],
        [InlineKeyboardButton("رصيد", callback_data="raseed")]
    ]
    await update.message.reply_text(f"تمام ID: `{update.message.text}`\nاختر الدفع:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return ASK_PAYMENT

async def ask_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pay_method = query.data
    pack = context.user_data['pack']
    ff_id = context.user_data['ff_id']
    user = query.from_user

    if pay_method == "bankak":
        await query.message.reply_text("🏦 *بنكك:*\nحساب: 1234567 - محمد\nرسل الاشعار هنا ✅", parse_mode='Markdown')
    else:
        await query.message.reply_text("📱 *رصيد:*\nزين: 090xxxxxxx\nرسل لقطة الشاشة هنا ✅", parse_mode='Markdown')

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"طلب جديد 🔥\n\n👤 @{user.username} ({user.id})\n📦 {pack}\n🆔 {ff_id}\n💳 {pay_method}")
    except: pass
    return ConversationHandler.END

def run_bot():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(entry_points=[CallbackQueryHandler(choose_pack)], states={ASK_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_id)], ASK_PAYMENT: [CallbackQueryHandler(ask_payment)]}, fallbacks=[])
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app_flask.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
