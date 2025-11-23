import os
import jdatetime
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "8486591461"))
SUPPORT_USERNAME = 'MahdeKoodakSupport'
CHANNEL_USERNAME = 'bigkidkindergarten'
CARD_NUMBER = '6219861815202733'
CARD_OWNER = 'ثمین دهقانی'

bot = Bot(BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)
app = Flask(__name__)

# ------------------------- وضعیت ثبت‌نام شهرها -------------------------
registration_status = {
    "esfahan": False,
    "tehran": False,
    "shiraz": False
}

# ------------------------- پیام‌ها -------------------------
CLOSED_EVENT_MESSAGE = (
    "سلام🌱\n\n"
    "در حال حاضر، در شهر انتخابیتون سانس فعالی برای ثبت‌نام نداریم و می‌تونید از طریق "
    f"کانال تلگراممون از سانس‌های جدید باخبر بشید✨️"
)

TEHRAN_EVENT_MESSAGE = (
    "مهدکودک‌بزرگترها تهران\n\n"
    "👫 مخاطب: بزرگسالان ۱۸+ که دلشون یه کم بچگی می‌خواد\n"
    "📅 جمعه، 23 آبان 1404 ساعت 17-20\n"
    "☁️ هزینه: 590 هزارتومان\n"
)

ESFAHAN_EVENT_MESSAGE = (
    "مهدکودک‌بزرگترها اصفهان\n\n"
    "👫 مخاطب: بزرگسالان ۱۸+ که دلشون یه کم بچگی می‌خواد\n"
    "📅 ۲۹ آبان ۱۴۰۴ ساعت 18-21\n"
    "☁️ هزینه: ۴۵۰ هزارتومان\n"
)

TEHRAN_RECEIPT_MESSAGE = f"""📝 قبل از ادامه هزینه رو مشخص کن:
یک نفر : 590 هزارتومان
دو نفر : 1,121 هزارتومان
سه نفر : 1,652 هزارتومان
واریز به کارت:
{CARD_NUMBER} به نام {CARD_OWNER}
"""

ESFAHAN_RECEIPT_MESSAGE = f"""📝 قبل از ادامه هزینه رو مشخص کن:
یک نفر : ۴۵۰ هزارتومان
دو نفر : ۸۵۵ هزارتومان
واریز به کارت:
{CARD_NUMBER} به نام {CARD_OWNER}
"""

# ------------------------- توابع کمکی -------------------------
def support_back_channel(callback_data):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("بازگشت", callback_data=callback_data)],
        [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ])

# ------------------------- هندلر‌ها -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✨ شهرتو انتخاب کن", callback_data='event_kindergarten')],
        [InlineKeyboardButton("پشتیبانی", callback_data='support')],
        [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ]
    if update.effective_user.id == ADMIN_CHAT_ID:
        keyboard += [
            [InlineKeyboardButton("🔒 بستن اصفهان", callback_data='close_esfahan'),
             InlineKeyboardButton("🔓 باز کردن اصفهان", callback_data='open_esfahan')],
            [InlineKeyboardButton("🔒 بستن تهران", callback_data='close_tehran'),
             InlineKeyboardButton("🔓 باز کردن تهران", callback_data='open_tehran')],
            [InlineKeyboardButton("🔒 بستن شیراز", callback_data='close_shiraz'),
             InlineKeyboardButton("🔓 باز کردن شیراز", callback_data='open_shiraz')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    greeting = "سلام 🌱\nخوشحالم که می‌خواین بیاین تا برای چند لحظه زندگی روزمره رو متوقف کنیم🥰"
    if update.message:
        await update.message.reply_text(greeting, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(greeting, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'event_kindergarten':
        def city_status(city): return "✅" if registration_status[city] else "❌"
        keyboard = [
            [InlineKeyboardButton(f"{city_status('esfahan')} اصفهان", callback_data='session_esfahan')],
            [InlineKeyboardButton(f"{city_status('tehran')} تهران", callback_data='session_tehran')],
            [InlineKeyboardButton(f"{city_status('shiraz')} شیراز", callback_data='session_shiraz')],
            [InlineKeyboardButton("بازگشت", callback_data='start')],
            [InlineKeyboardButton("پشتیبانی", callback_data='support')],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await query.edit_message_text("✨ کدوم شهرو می‌خوای شرکت کنی؟", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == 'session_tehran':
        context.user_data["city"] = "تهران"
        if registration_status["tehran"]:
            keyboard = [[InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data='start_receipt_tehran')],
                        [InlineKeyboardButton("بازگشت", callback_data='event_kindergarten')],
                        [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]]
            await query.edit_message_text(TEHRAN_EVENT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=support_back_channel('event_kindergarten'))
    elif query.data == 'session_esfahan':
        context.user_data["city"] = "اصفهان"
        if registration_status["esfahan"]:
            keyboard = [[InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data='start_receipt_esfahan')],
                        [InlineKeyboardButton("بازگشت", callback_data='event_kindergarten')],
                        [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]]
            await query.edit_message_text(ESFAHAN_EVENT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=support_back_channel('event_kindergarten'))
    elif query.data.startswith("open_") or query.data.startswith("close_"):
        city = query.data.split("_")[1]
        registration_status[city] = query.data.startswith("open_")
        state = "باز شد ✅" if registration_status[city] else "بسته شد ❌"
        await query.edit_message_text(f"ثبت‌نام برای {city} {state}", reply_markup=support_back_channel('start'))
    elif query.data == 'support':
        await query.edit_message_text(f"اگه سوالی داشتی با آیدی @{SUPPORT_USERNAME} ارتباط بگیر 💌", reply_markup=support_back_channel('event_kindergarten'))
    elif query.data == 'start_receipt_tehran':
        await query.edit_message_text(TEHRAN_RECEIPT_MESSAGE, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]
        ]))
    elif query.data == 'start_receipt_esfahan':
        await query.edit_message_text(ESFAHAN_RECEIPT_MESSAGE, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]
        ]))

# ------------------------- هندلر Webhook -------------------------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running!"

# ------------------------- ثبت هندلر‌ها -------------------------
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button_handler))

# ------------------------- اجرای Flask -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)