import os, asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "1776655781"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
RATE = 10100

class Order(StatesGroup):
    choosing_category = State()
    choosing_game = State()
    choosing_package = State()
    choosing_service = State()
    waiting_receipt = State()

GAMES = ["Clash of Clans","Free Fire","PUBG Mobile","eFootball Mobile (PES)","Mobile Legends: Bang Bang","Call of Duty: Mobile","Clash Royale"]
PACKAGES = {
    "Clash of Clans": [("80 Gems", 1), ("500 Gems", 5), ("1200 Gems", 10), ("2500 Gems", 20)],
    "Free Fire": [("110 Diamonds", 1), ("530 Diamonds", 5), ("1080 Diamonds", 10), ("2200 Diamonds", 20)],
    "PUBG Mobile": [("60 UC", 1), ("325 UC", 5), ("660 UC", 10), ("1800 UC", 25)],
    "eFootball Mobile (PES)": [("100 Coins", 1), ("550 Coins", 5), ("1040 Coins", 9), ("2130 Coins", 18)],
    "Mobile Legends: Bang Bang": [("86 Diamonds", 1), ("344 Diamonds", 5), ("706 Diamonds", 10), ("1446 Diamonds", 20)],
    "Call of Duty: Mobile": [("80 CP", 1), ("400 CP", 5), ("800 CP", 10), ("2000 CP", 24)],
    "Clash Royale": [("80 Gems", 1), ("500 Gems", 5), ("1200 Gems", 10), ("2500 Gems", 20)],
}
SERVICES = {"Netflix": [("شهر واحد", 5), ("3 شهور", 14)],"Shahid Plus": [("شهر", 3), ("سنة", 25)],"Gemini Pro": [("شهر", 10), ("سنة", 80)],"ChatGPT Plus": [("شهر", 20)],"Google Play Pass": [("شهر", 5)],"Google One": [("100GB شهر", 2), ("2TB شهر", 10)],}

def main_kb(): return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="🎮 اختيار لعبة"), types.KeyboardButton(text="🎬 اختيار خدمة")]], resize_keyboard=True)
def back_kb(): return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="🔙 رجوع")]], resize_keyboard=True)
def games_kb(): 
    kb = [[types.KeyboardButton(text=g)] for g in GAMES]
    kb.append([types.KeyboardButton(text="🔙 رجوع")])
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
def services_kb():
    kb = [[types.KeyboardButton(text=s)] for s in SERVICES.keys()]
    kb.append([types.KeyboardButton(text="🔙 رجوع")])
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def start(m: types.Message, state: FSMContext):
    await state.set_state(Order.choosing_category)
    await m.answer("أهلاً بيك في متجر آلباتشينو 🔥\nاختار نوع الخدمة:", reply_markup=main_kb())

@dp.message(F.text == "🔙 رجوع")
async def back(m: types.Message, state: FSMContext):
    await state.set_state(Order.choosing_category)
    await m.answer("رجعت للقائمة الرئيسية 👇", reply_markup=main_kb())

@dp.message(F.text == "🎮 اختيار لعبة")
async def choose_game_cat(m: types.Message, state: FSMContext):
    await state.set_state(Order.choosing_game)
    await m.answer("اختار اللعبة (بالإنجليزي):", reply_markup=games_kb())

@dp.message(F.text == "🎬 اختيار خدمة")
async def choose_service_cat(m: types.Message, state: FSMContext):
    await state.set_state(Order.choosing_service)
    await m.answer("اختار الخدمة:", reply_markup=services_kb())

@dp.message(Order.choosing_game)
async def show_game_packages(m: types.Message, state: FSMContext):
    game = m.text
    if game not in GAMES: return
    await state.update_data(game=game)
    await state.set_state(Order.choosing_package)
    buttons = []
    for name, usd in PACKAGES[game]:
        sdg = usd * RATE
        buttons.append([types.KeyboardButton(text=f"{name} - ${usd} / {sdg:,} SDG")])
    buttons.append([types.KeyboardButton(text="🔙 رجوع")])
    await m.answer(f"باقات {game} 👇\n1$ = {RATE:,} SDG\nاختار الباقة:", reply_markup=types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True))

@dp.message(Order.choosing_service)
async def show_service_packages(m: types.Message, state: FSMContext):
    serv = m.text
    if serv not in SERVICES: return
    await state.update_data(service=serv)
    await state.set_state(Order.choosing_package)
    buttons = []
    for name, usd in SERVICES[serv]:
        sdg = usd * RATE
        buttons.append([types.KeyboardButton(text=f"{serv} {name} - ${usd} / {sdg:,} SDG")])
    buttons.append([types.KeyboardButton(text="🔙 رجوع")])
    await m.answer(f"باقات {serv} 👇\nاختار الباقة:", reply_markup=types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True))

@dp.message(Order.choosing_package)
async def payment_method(m: types.Message, state: FSMContext):
    if "🔙" in m.text: return await back(m, state)
    await state.update_data(package=m.text)
    await state.set_state(Order.waiting_receipt)
    await m.answer(f"✅ اخترت: {m.text}\n\n💳 طريقة الدفع:\n🏦 بنكك - 7534659\nالاسم: متجر آلباتشينو\n\nبعد التحويل، 📸 ارسل صورة الاشعار هنا.", reply_markup=back_kb())

@dp.message(Order.waiting_receipt, F.photo)
async def receipt_received(m: types.Message, state: FSMContext):
    data = await state.get_data()
    await m.answer("⏳ إنتظر من فضلك العملية قيد المراجعة... سيتم تأكيد طلبك خلال دقائق ✅", reply_markup=main_kb())
    caption = f"🔔 طلب جديد!\n👤 العميل: @{m.from_user.username or m.from_user.id} ({m.from_user.id})\n🎮 اللعبة/الخدمة: {data.get('game') or data.get('service')}\n📦 الباقة: {data.get('package')}\n💰 تم ارسال اشعار بنكك 👇"
    try: await bot.send_photo(chat_id=OWNER_ID, photo=m.photo[-1].file_id, caption=caption)
    except: print("OWNER_ID error")
    await state.clear()
    await state.set_state(Order.choosing_category)

@dp.message(Order.waiting_receipt)
async def need_photo(m: types.Message): await m.answer("⚠️ لازم ترسل صورة اشعار بنكك.")

# ---- ده الحل لمشكلة البورت في Render ----
async def handle(request): return web.Response(text="Bot is running")
async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 10000)))
    await site.start()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
