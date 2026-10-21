import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
TOKEN = "8921211417:AAH5ujgsFoNlGGNM56g_ocGX47LJE9qI7fI"
PRODUCTS = {"تيشيرت آلباتشينو":9000,"قميص آلباتشينو":9000,"بنطلون آلباتشينو":9000}
logging.basicConfig(level=logging.INFO)
async def start(update, context):
    keyboard = [[InlineKeyboardButton(f"{n} - {p} جنيه", callback_data=n)] for n,p in PRODUCTS.items()]
    await update.message.reply_text("مرحبا في متجر آلباتشينو كل المنتجات 9000 جنيه:", reply_markup=InlineKeyboardMarkup(keyboard))
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(f"اخترت: {query.data} - للطلب ارسل اسمك")
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
if __name__ == "__main__": main()
