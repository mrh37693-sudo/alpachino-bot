import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, ConversationHandler

TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0")) # حط ايديك هنا في Render

# أسعارك - عدلها براحتك
PACKAGES = {
    "100": {"diamonds": "100 💎", "price": "3,000 SDG"},
    "310": {"diamonds": "310 💎", "price": "8,500 SDG"},
    "520": {"diamonds": "520 💎", "price": "14,000 SDG"},
    "1060": {"diamonds": "1060 💎", "price": "27,000 SDG"},
    "2180": {"diamonds": "2180 💎", "price": "53,000 SDG"},
}

BANKAK_INFO = """
💳 **للدفع بنكك:**
رقم الحساب: 1234567
الاسم: الباتشينو
"""

ASK_ID, ASK_PAYMENT = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for key, pkg in PACKAGES.items():
        keyboard.append([InlineKeyboardButton(f"{pkg['diamonds']} - {pkg['price']}", callback_data=f"buy_{key}")])
    
    keyboard.append([InlineKeyboardButton("📞 تواصل معنا", callback_data="contact")])
    await update.message.reply_text(
        "🔥 **أهلاً بيك في متجر الباتشينو لجواهر فري فاير** 🔥\n\n"
        "اختر الباقة العايزها:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("buy_"):
        pkg_id = query.data.split("_")[1]
        context.user_data["package"] = pkg_id
        pkg = PACKAGES[pkg_id]
        await query.message.reply_text(
            f"اخترت: {pkg['diamonds']} بسعر {pkg['price']}\n\n"
            f"📝 أرسل **ID حسابك في فري فاير** (الأرقام فقط):"
        )
        return ASK_ID
    
    if query.data == "contact":
        await query.message.reply_text("تواصل واتساب: 09xxxxxxxx\nتيليجرام: @your_username")

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_id = update.message.text.strip()
    if not player_id.isdigit():
        await update.message.reply_text("❌ الـ ID لازم يكون أرقام فقط، حاول تاني:")
        return ASK_ID
    
    context.user_data["player_id"] = player_id
    pkg = PACKAGES[context.user_data["package"]]
    
    keyboard = [
        [InlineKeyboardButton("بنكك 💳", callback_data="pay_bankak")],
        [InlineKeyboardButton("رصيد 📱", callback_data="pay_raseed")],
    ]
    await update.message.reply_text(
        f"تمام! ID: `{player_id}`\nالباقة: {pkg['diamonds']}\n\n"
        f"اختار طريقة الدفع:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ASK_PAYMENT

async def get_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    pkg_id = context.user_data["package"]
    player_id = context.user_data["player_id"]
    pkg = PACKAGES[pkg_id]
    user = query.from_user

    if query.data == "pay_bankak":
        await query.message.reply_text(
            f"{BANKAK_INFO}\n\n"
            f"بعد التحويل، أرسل **صورة إشعار بنكك** هنا، وسيتم الشحن خلال 5-10 دقائق.\n\n"
            f"تفاصيل طلبك:\n"
            f"الباقة: {pkg['diamonds']}\n"
            f"ID: {player_id}\n"
            f"السعر: {pkg['price']}",
            parse_mode="Markdown"
        )
    else:
        await query.message.reply_text("لدفع بالرصيد تواصل معنا: 09xxxxxxxx")

    # رسالة ليك انت كأدمن
    if ADMIN_ID != 0:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🔔 **طلب جديد!**\n\n"
                     f"من: @{user.username or user.first_name} ({user.id})\n"
                     f"الباقة: {pkg['diamonds']}\n"
                     f"ID اللاعب: {player_id}\n"
                     f"السعر: {pkg['price']}\n"
                     f"الدفع: {query.data}",
                parse_mode="Markdown"
            )
        except:
            pass

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم الإلغاء. دوس /start تبدا تاني.")
    return ConversationHandler.END

def main():
    if not TOKEN:
        print("ERROR: BOT_TOKEN not set!")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            ASK_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_id)],
            ASK_PAYMENT: [CallbackQueryHandler(get_payment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    print("Diamond store bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
