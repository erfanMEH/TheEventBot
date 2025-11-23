import os
import jdatetime
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ------------------------- تنظیمات -------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "8486591461"))
SUPPORT_USERNAME = 'MahdeKoodakSupport'
CHANNEL_USERNAME = 'bigkidkindergarten'
CARD_NUMBER = '6219861815202733'
CARD_OWNER = 'ثمین دهقانی'

bot = Bot(token=BOT_TOKEN)
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
    "خوشحالیم که مشتاق حضور در جمع مهدکودک‌بزرگترها هستید\n\n"
    "در حال حاضر، در شهر انتخابیتون سانس فعالی برای ثبت‌نام نداریم و می‌تونید از طریق "
    f"کانال تلگراممون از سانس‌های جدید باخبر بشید✨️"
)

TEHRAN_EVENT_MESSAGE = (
    "مهدکودک‌بزرگترها تهران\n\n"
    "👫 مخاطب رویداد : بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
    "📅 زمان: جمعه، 23 آبان 1404\nساعت 17 الی 20\n\n"
    "📍 مکان: باغچه کودکی هم‌صدا\n\n"
    "☁️ هزینه: 590 هزارتومان\n\n"
    "🔸 شرایط ثبت نام با تخفیف:\nبه ازای هر دوستی که همراه بیارید ۱۰٪ تخفیف می‌گیرید."
)

ESFAHAN_EVENT_MESSAGE = (
    "مهدکودک‌بزرگترها اصفهان\n\n"
    "👫 مخاطب رویداد : بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
    "📅 زمان: ۲۹ آبان ۱۴۰۴\nساعت ۱۸ الی ۲۱\n\n"
    "📍 مکان: استودیو یوگا پرانا (خیابان کارگر)\n\n"
    "☁️ هزینه: ۴۵۰ هزارتومان\n\n"
    "🔸 شرایط ثبت نام با تخفیف:\nبه ازای هر دوستی که همراه بیارید ۱۰٪ تخفیف می‌گیرید."
)

TEHRAN_RECEIPT_MESSAGE = f"""📝 لطفا قبل از ادامه‌ی مسیر هزینه‌ی رویداد رو براساس تعداد نفرات مشخص کن:

یک نفر : 590 هزارتومان
دونفر : 1,121 هزارتومان
سه نفر: 1,652 هزارتومان
چهار نفر: 2,183 هزارتومان
پنج نفر: 2,741 هزارتومان

📤 حالا مبلغ رو به این شماره کارت واریز کن
و فیش واریزت رو به همراه اسم و شماره تماس و تعداد نفرات همینجا بفرست:

{CARD_NUMBER}
به نام {CARD_OWNER}"""

ESFAHAN_RECEIPT_MESSAGE = f"""📝 لطفا قبل از ادامه‌ی مسیر هزینه‌ی رویداد رو براساس تعداد نفرات مشخص کن:

یک نفر : ۴۵۰ هزارتومان
دونفر : ۸۵۵ هزارتومان
سه نفر: ۱,۲۶۰ هزارتومان
چهار نفر: ۱,۶۶۵ هزارتومان
پنج نفر: ۲,۰۷۰ هزارتومان

📤 حالا مبلغ رو به این شماره کارت واریز کن و فیش واریزت رو به همراه اسم و شماره تماس و تعداد نفرات همینجا بفرست:

{CARD_NUMBER}
به نام {CARD_OWNER}"""

# ------------------------- توابع کمکی -------------------------
def support_back_channel(callback_data):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("بازگشت", callback_data=callback_data)],
        [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ])

# ------------------------- هندلر start -------------------------
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
    greeting = "سلام 🌱\nخوشحالم که می‌خواین بیاین تا برای چند لحظه زندگیِ روزمره رو متوقف کنیم🥰"
    if update.message:
        await update.message.reply_text(greeting, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(greeting, reply_markup=reply_markup)

# ------------------------- هندلر دکمه‌ها -------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # شهرها
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

    elif query.data.startswith("session_"):
        city_map = {
            "session_tehran": ("تهران", TEHRAN_EVENT_MESSAGE, TEHRAN_RECEIPT_MESSAGE),
            "session_esfahan": ("اصفهان", ESFAHAN_EVENT_MESSAGE, ESFAHAN_RECEIPT_MESSAGE),
            "session_shiraz": ("شیراز", "مهدکودک‌بزرگترها شیراز ✨", "Receipt پیام شیراز")
        }
        city_name, event_msg, receipt_msg = city_map[query.data]
        context.user_data["city"] = city_name
        if registration_status.get(city_name.lower(), False):
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data=f'start_receipt_{city_name.lower()}')],
                [InlineKeyboardButton("بازگشت", callback_data='event_kindergarten')],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]
            ]
            await query.edit_message_text(event_msg, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=support_back_channel('event_kindergarten'))

    # باز/بسته کردن ثبت‌نام
    elif query.data.startswith("open_") or query.data.startswith("close_"):
        city = query.data.split("_")[1]
        registration_status[city] = query.data.startswith("open_")
        state = "باز شد ✅" if registration_status[city] else "بسته شد ❌"
        await query.edit_message_text(f"ثبت‌نام برای {city} {state}", reply_markup=support_back_channel('start'))

    # پشتیبانی
    elif query.data == 'support':
        await query.edit_message_text(f"اگه سوالی داشتی با آیدی @{SUPPORT_USERNAME} ارتباط بگیر 💌", reply_markup=support_back_channel('event_kindergarten'))

    # شروع ثبت‌نام / نمایش فیش
    elif query.data.startswith("start_receipt_"):
        city = query.data.split("_")[-1]
        msg = TEHRAN_RECEIPT_MESSAGE if city=="tehran" else ESFAHAN_RECEIPT_MESSAGE
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]
        ]))

# ------------------------- هندلر عکس فیش -------------------------
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = context.user_data.get("city")
    if not city or not registration_status.get(city.lower(), False):
        await update.message.reply_text(
            "❌ ثبت‌نام برای این شهر بسته شده یا مسیر ثبت‌نام کامل طی نشده.\n"
            "لطفا فیش واریزیتون رو ارسال کنید.",
            reply_markup=support_back_channel('event_kindergarten')
        )
        return
    photo = update.message.photo[-1]
    caption = update.message.caption or "بدون کپشن"
    user = update.message.from_user
    user_id = user.id
    full_caption = f"از طرف {user.full_name} (@{user.username or 'بدون نام کاربری'})\n\nکپشن:\n{caption}"

    confirm_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تأیید ثبت‌نام", callback_data=f"confirm_{user_id}_{city}")],
        [InlineKeyboardButton("❌ رد به‌خاطر اطلاعات ناقص", callback_data=f"reject_info_{user_id}")],
        [InlineKeyboardButton("❌ رد به‌خاطر مبلغ اشتباه", callback_data=f"reject_amount_{user_id}")]
    ])

    await bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo.file_id, caption=full_caption, reply_markup=confirm_buttons)
    context.user_data["city"] = None
    await update.message.reply_text(
        "فیش شما با موفقیت دریافت شد 💌\nدر حال بررسی هستیم. به‌زودی اطلاع داده می‌شود 🌱"
    )

# ------------------------- هندلر Webhook -------------------------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running!"

# ------------------------- ثبت هندلرها -------------------------
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(button_handler))
dispatcher.add_handler(MessageHandler(filters.PHOTO, photo_handler))

# ------------------------- اجرای Flask -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)