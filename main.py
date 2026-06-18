import os
import asyncio
import jdatetime
from flask import Flask, request
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ------------------------- تنظیمات ثابت -------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "8486591461"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

SUPPORT_USERNAME = "MahdeKoodakSupport"
CHANNEL_USERNAME = "bigkidkindergarten"
CARD_NUMBER = "6219861815202733"
CARD_OWNER = "ثمین دهقانی"

registration_status = {
    "esfahan": False,
    "tehran": False,
    "shiraz": False,
}

CITY_DISPLAY_NAMES = {
    "esfahan": "اصفهان",
    "tehran": "تهران",
    "shiraz": "شیراز",
}

# ------------------------- پیام‌های آماده -------------------------

DYNAMIC_CONFIRM_DAY = {
    "tehran": "جمعه",
    "esfahan": "سه‌شنبه",
    "shiraz": "رویداد شیراز",
}

CLOSED_EVENT_MESSAGE = (
    "سلام🌱\n"
    "خوشحالیم که مشتاق حضور در جمع مهدکودک‌بزرگترها هستید🥹\n\n"
    "در حال حاضر، در شهر انتخابی سانس فعالی برای ثبت‌نام نداریم اما می‌تونی با انتخاب کردن گزینه پایین، "
    "اولین کسی باشی که وقتی ثبت‌نام شروع شد ازش با خبر میشه🍀\n\n"
    "برای دریافت اخبار یا اطلاعات هم یادت نره که حتما به کانالمون سر بزنی✨"
)

TEHRAN_EVENT_MESSAGE = (
    "مهدکودک‌بزرگترها تهران\n\n"
    "👫 مخاطب رویداد : بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
    "📅 زمان:\nجمعه، 23 آبان 1404\nساعت 17 الی 20\n\n"
    "📍 مکان:\nباغچه کودکی هم‌صدا\n\n"
    "☁️ هزینه: 590 هزارتومان\n\n"
    "🔸 شرایط ثبت نام با تخفیف:\n"
    "به ازای هر دوستی که همراه با خودتون بیارید ۱۰٪ تخفیف همراهی از ما می‌گیرید.\n\n"
    "(نگران تنها اومدن هم نباشید؛ ما اینجا همه باهم دوست میشیم :)"
)

ESFAHAN_EVENT_MESSAGE = (
    "مهدکودک‌بزرگترها اصفهان\n\n"
    "👫مخاطب رویداد : بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
    "📅زمان:\n۴ آذر ۱۴۰۴\nساعت ۱۷ الی ۲۰\n\n"
    "📍مکان: \nخونه‌نقطه🌱\n\n"
    "☁️ هزینه: ۴۵۰ هزارتومان \n\n"
    "🔸شرایط ثبت نام با تخفیف:\n"
    "به ازای هر دوستی که همراه با خودتون بیارید ۱۰٪ تخفیف همراهی از ما می‌گیرید.\n\n"
    "(نگران تنها اومدن هم نباشید؛ ما اینجا همه باهم دوست میشیم :)"
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

ESFAHAN_RECEIPT_MESSAGE = f"""📝 لطفا قبل از ادامه‌ی مسیر هزینه‌ی رویداد رو براساس تعداد نفرات محاسبه کن:

یک نفر: ۸۵۰ هزارتومان
دو نفر: یک میلیون و ۶۱۵ هزارتومان
سه نفر: دو میلیون و ۳۸۰ هزارتومان
چهار نفر: سه میلیون و ۱۴۵ هزارتومان
پنج نفر: سه میلیون و ۹۱۰ هزارتومان
و ...

📤 حالا مبلغ رو به این شماره کارت واریز کن و فیش واریزت رو به همراه اسم و شماره تماس و تعداد نفرات همینجا بفرست:

{CARD_NUMBER}
به نام {CARD_OWNER}"""

# ------------------------- توابع کمکی -------------------------

def support_back_channel(callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("بازگشت", callback_data=callback_data)],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")],
        ]
    )

def closed_event_keyboard(city_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔔 می‌خوای زودتر از بقیه خبردار شی؟", callback_data=f"notify_{city_key}")],
            [InlineKeyboardButton("بازگشت", callback_data="event_kindergarten")],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")],
        ]
    )

# ------------------------- شروع /start -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✨ شهرتو انتخاب کن", callback_data="event_kindergarten")],
        [InlineKeyboardButton("پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")],
    ]

    if update.effective_user and update.effective_user.id == ADMIN_CHAT_ID:
        keyboard.append([
            InlineKeyboardButton("🔒 بستن اصفهان", callback_data="close_esfahan"),
            InlineKeyboardButton("🔓 باز کردن اصفهان", callback_data="open_esfahan"),
        ])
        keyboard.append([
            InlineKeyboardButton("🔒 بستن تهران", callback_data="close_tehran"),
            InlineKeyboardButton("🔓 باز کردن تهران", callback_data="open_tehran"),
        ])
        keyboard.append([
            InlineKeyboardButton("🔒 بستن شیراز", callback_data="close_shiraz"),
            InlineKeyboardButton("🔓 باز کردن شیراز", callback_data="open_shiraz"),
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    greeting = (
        "سلام 🌱\n"
        "خوشحالم که می‌خواین بیاین تا برای چند لحظه زندگیِ روزمره رو متوقف کنیم🥰"
    )

    if update.message:
        await update.message.reply_text(greeting, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(greeting, reply_markup=reply_markup)

# ------------------------- هندلر دکمه‌ها -------------------------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        await start(update, context)

    elif query.data == "event_kindergarten":
        def city_status(city):
            return "✅ " if registration_status[city] else ""

        keyboard = [
            [InlineKeyboardButton(f"{city_status('esfahan')}اصفهان", callback_data="session_esfahan")],
            [InlineKeyboardButton(f"{city_status('tehran')}تهران", callback_data="session_tehran")],
            [InlineKeyboardButton(f"{city_status('shiraz')}شیراز", callback_data="session_shiraz")],
            [InlineKeyboardButton("بازگشت", callback_data="start")],
            [InlineKeyboardButton("پشتیبانی", callback_data="support")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")],
        ]
        await query.edit_message_text("✨ کدوم شهرو می‌خوای شرکت کنی؟", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "session_tehran":
        context.user_data["city"] = "تهران"
        if registration_status["tehran"]:
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data="start_receipt_tehran")],
                [InlineKeyboardButton("بازگشت", callback_data="event_kindergarten")],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            ]
            await query.edit_message_text(TEHRAN_EVENT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=closed_event_keyboard("tehran"))

    elif query.data == "session_esfahan":
        context.user_data["city"] = "اصفهان"
        if registration_status["esfahan"]:
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data="start_receipt_esfahan")],
                [InlineKeyboardButton("بازگشت", callback_data="event_kindergarten")],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            ]
            await query.edit_message_text(ESFAHAN_EVENT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=closed_event_keyboard("esfahan"))

    elif query.data == "session_shiraz":
        context.user_data["city"] = "شیراز"
        if registration_status["shiraz"]:
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data="start_receipt_shiraz")],
                [InlineKeyboardButton("بازگشت", callback_data="event_kindergarten")],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            ]
            await query.edit_message_text("مهدکودک‌بزرگترها شیراز ✨", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=closed_event_keyboard("shiraz"))

    elif query.data == "start_receipt_tehran":
        context.user_data["ready_for_receipt"] = "tehran"
        await query.edit_message_text(
            TEHRAN_RECEIPT_MESSAGE,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]]),
        )

    elif query.data == "start_receipt_esfahan":
        context.user_data["ready_for_receipt"] = "esfahan"
        await query.edit_message_text(
            ESFAHAN_RECEIPT_MESSAGE,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]]),
        )

    elif query.data.startswith("open_") or query.data.startswith("close_"):
        city = query.data.split("_")[1]
        registration_status[city] = query.data.startswith("open")
        state = "باز شد ✅" if registration_status[city] else "بسته شد ❌"
        await query.edit_message_text(f"ثبت‌نام برای {city} {state}", reply_markup=support_back_channel("start"))

    elif query.data.startswith("notify_"):
        city_key = query.data.split("_", 1)[1]
        context.user_data["notify_city"] = city_key
        city_name = CITY_DISPLAY_NAMES.get(city_key, city_key)

        # حذف دکمه‌ی «خبردار شو» از پیام قبلی تا کاربر دوبار روش نزنه
        await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=support_back_channel("event_kindergarten"))

        contact_keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("📱 اشتراک‌گذاری شماره تلفن", request_contact=True)],
                ["انصراف"],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"عالیه 🌱 برای اینکه به محض باز شدن ثبت‌نام «{city_name}» زودتر از بقیه خبردار بشی، "
                "با دکمه‌ی پایین شماره تماستو با ما به اشتراک بگذار 📱"
            ),
            reply_markup=contact_keyboard,
        )

    elif query.data == "support":
        await query.edit_message_text(
            "اگه سوالی داشتی یا نیاز به کمک داشتی، با آیدی @MahdeKoodakSupport ارتباط بگیر 💌",
            reply_markup=support_back_channel("event_kindergarten"),
        )

    elif query.data.startswith("confirm_"):
        parts = query.data.split("_")
        user_id = int(parts[1])
        city = parts[2] if len(parts) > 2 else None
        event_day = DYNAMIC_CONFIRM_DAY.get(city, "رویداد پیش‌رو")

        confirmation_text = (
            "پرداخت شما تأیید شد 🌱\n"
            f"ثبت‌نامتون در رویداد مهدکودک‌بزرگترهای **{event_day}** کامل شد.\n\n"
            "اطلاعات تکمیلی رویداد،‌ یک روز قبل از اون براتون ارسال میشه✨\n\n"
            "منتظرتون هستیم 💛"
        )
        await context.bot.send_message(chat_id=user_id, text=confirmation_text)

        msg = query.message
        caption = msg.caption or ""
        today_shamsi = jdatetime.date.today().strftime("%Y/%m/%d")
        new_caption = f"{caption}\n\n✅ تایید شده در تاریخ {today_shamsi}"
        await query.edit_message_caption(caption=new_caption, reply_markup=None)

    elif query.data.startswith("reject_info_") or query.data.startswith("reject_amount_"):
        user_id = int(query.data.split("_")[2])
        is_info_reject = "reject_info" in query.data

        if is_info_reject:
            reason_text = "اطلاعات ناقص"
            reject_message = (
                "❌ ثبت‌نام شما به دلیل اطلاعات ناکافی، رد شد. لطفا مراحل ثبت‌نام رو از اول طی کنید "
                "و فیشتون رو دوباره ارسال کنید. در کپشن عکس، نام و شماره تماستون رو بنویسید 🌱"
            )
        else:
            reason_text = "مبلغ اشتباه"
            reject_message = (
                "❌ ثبت‌نام شما به دلیل واریز مبلغ اشتباه رد شد. "
                "با اکانت پشتیبانی به آیدی @MahdeKoodakSupport در تماس باشید."
            )

        await context.bot.send_message(
            chat_id=user_id,
            text=reject_message,
            reply_markup=support_back_channel("event_kindergarten"),
        )

        msg = query.message
        caption = msg.caption or ""
        today_shamsi = jdatetime.date.today().strftime("%Y/%m/%d")
        new_caption = f"{caption}\n\n❌ رد شده ({reason_text}) در تاریخ {today_shamsi}"
        await query.edit_message_caption(caption=new_caption, reply_markup=None)

# ------------------------- دریافت عکس فیش -------------------------

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = context.user_data.get("ready_for_receipt")

    if not city or not registration_status.get(city, False):
        await update.message.reply_text(
            "❌ ثبت‌نام برای این شهر بسته شده یا مسیر ثبت‌نام کامل طی نشده.\n"
            "لطفا فیش واریزیتون رو به همراه نام و نام خانوادگی در کپشن عکس، بعد از انتخاب کردن «نهایی کردن ثبت‌نام» ارسال کنید.",
            reply_markup=support_back_channel("event_kindergarten"),
        )
        return

    photo = update.message.photo[-1]
    caption = update.message.caption or "بدون کپشن"
    user = update.message.from_user
    user_id = user.id

    sender_info = f"از طرف {user.full_name} (@{user.username or 'بدون نام کاربری'})"
    full_caption = f"{sender_info}\n\nکپشن:\n{caption}"

    confirm_buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ تأیید ثبت‌نام", callback_data=f"confirm_{user_id}_{city}")],
            [InlineKeyboardButton("❌ رد به‌خاطر اطلاعات ناقص", callback_data=f"reject_info_{user_id}")],
            [InlineKeyboardButton("❌ رد به‌خاطر مبلغ اشتباه", callback_data=f"reject_amount_{user_id}")],
        ]
    )

    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo.file_id,
        caption=full_caption,
        reply_markup=confirm_buttons,
    )

    context.user_data["ready_for_receipt"] = None

    await update.message.reply_text(
        "فیش شما با موفقیت دریافت شد 💌\nدر حال بررسی توسط تیم ثبت‌نام هستیم. به‌زودی نتیجه رو بهتون اطلاع می‌دیم 🌱"
    )

# ------------------------- دریافت شماره تماس برای اطلاع‌رسانی زودهنگام -------------------------

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_key = context.user_data.get("notify_city")

    if not city_key:
        # کانتکتی که بدون طی کردن مسیر «خبردار شو» اومده رو نادیده می‌گیریم
        return

    contact = update.message.contact
    user = update.message.from_user
    city_name = CITY_DISPLAY_NAMES.get(city_key, city_key)
    full_name = f"{contact.first_name or ''} {contact.last_name or ''}".strip()

    admin_text = (
        "🔔 درخواست اطلاع‌رسانی زودهنگام\n\n"
        f"شهر: {city_name}\n"
        f"نام: {full_name or 'نامشخص'}\n"
        f"شماره تماس: {contact.phone_number}\n"
        f"یوزرنیم: @{user.username or 'ندارد'}\n"
        f"آیدی عددی: {user.id}"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text)

    await update.message.reply_text(
        f"ثبت شد 🌱 به محض باز شدن ثبت‌نام «{city_name}»، اول از همه به تو خبر می‌دیم 💛",
        reply_markup=ReplyKeyboardRemove(),
    )

    context.user_data["notify_city"] = None


async def cancel_notify_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("notify_city"):
        context.user_data["notify_city"] = None
        await update.message.reply_text("باشه، فعلاً بی‌خیال 🌱", reply_markup=ReplyKeyboardRemove())

# ------------------------- تنظیمات بات و Flask -------------------------

async def set_bot_commands(app):
    await app.bot.set_my_commands([BotCommand("start", "شروع ربات")])

# ساخت اپلیکیشن تلگرام
telegram_app = ApplicationBuilder().token(BOT_TOKEN).post_init(set_bot_commands).build()

# ایجاد برنامه Flask
app = Flask(__name__)

# رجیستر کردن هندلرهای تلگرام
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))
telegram_app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
telegram_app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
telegram_app.add_handler(MessageHandler(filters.Regex("^انصراف$"), cancel_notify_handler))


# یک event loop واحد برای کل عمر اپلیکیشن می‌سازیم و هیچ‌وقت نمی‌بندیمش.
# (اگه به‌جای این از asyncio.run() در هر ریکوئست استفاده کنیم، چون asyncio.run
#  هر بار loop رو می‌بنده ولی کلاینت HTTP داخلی تلگرام به همون loop وصل می‌مونه،
#  در ریکوئست بعدی خطای "Event loop is closed" می‌گیریم.)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def _startup():
    """
    این تابع فقط یک‌بار، قبل از بالا آمدن سرور اجرا می‌شه:
    - اپلیکیشن تلگرام رو initialize می‌کنه (روی همون loop واحد)
    - وب‌هوک رو ست می‌کنه (اگه WEBHOOK_URL ست شده باشه)
    """
    await telegram_app.initialize()
    if WEBHOOK_URL:
        await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
        print(f"✅ Webhook successfully set to: {WEBHOOK_URL}")
    else:
        print("⚠️ WEBHOOK_URL تنظیم نشده؛ وب‌هوک ست نشد.")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.get_json()
        update = Update.de_json(data, telegram_app.bot)
        # همیشه از همون loop واحد استفاده می‌کنیم، نه یک loop تازه در هر ریکوئست
        loop.run_until_complete(telegram_app.process_update(update))
        return "OK", 200
    return "Server is running!", 200


if __name__ == "__main__":
    loop.run_until_complete(_startup())
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
