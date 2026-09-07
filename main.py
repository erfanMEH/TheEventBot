import os
import re
import json
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
from telegram.error import RetryAfter
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

DB_FILE = "databases.json"

registration_status = {
    "esfahan": False,
    "tehran": False,
    "shiraz": False,
    "mashhad": False,
    "rasht": False,
    "yazd": False,
}

CITY_DISPLAY_NAMES = {
    "esfahan": "اصفهان",
    "tehran": "تهران",
    "shiraz": "شیراز",
    "mashhad": "مشهد",
    "rasht": "رشت",
    "yazd": "یزد",
}

CITY_NAME_TO_KEY = {v: k for k, v in CITY_DISPLAY_NAMES.items()}

DB_ACTION_LABELS = {
    "set": "📥 تنظیم دیتابیس (جایگزینی)",
    "add": "➕ افزودن به دیتابیس",
    "send": "📤 ارسال پیام به این دیتابیس",
    "collect": "🧲 جمع‌آوری خودکار از پیام‌ها",
    "view": "👁 نمایش آیدی‌ها",
}
DB_LABEL_TO_ACTION = {v: k for k, v in DB_ACTION_LABELS.items()}

CANCEL_LABEL = "🔙 لغو"
STOP_COLLECT_LABEL = "⏹ پایان جمع‌آوری"

# ------------------------- پیام‌های آماده -------------------------

DYNAMIC_CONFIRM_DAY = {
    "tehran": "پنجشنبه",
    "esfahan": "پنجشنبه",
    "shiraz": "جمعه",
    "mashhad": "جمعه",
}

CLOSED_EVENT_MESSAGE = (
    "سلام🌱\n"
    "خوشحالیم که مشتاق حضور در جمع مهدکودک‌بزرگترها هستید🥹\n\n"
    "در حال حاضر، در شهر انتخابی سانس فعالی برای ثبت‌نام نداریم اما می‌تونی با انتخاب کردن گزینه پایین، "
    "اولین کسی باشی که وقتی ثبت‌نام شروع شد ازش با خبر میشه🍀\n"
    "برای دریافت اخبار یا اطلاعات هم یادت نره که حتما به کانالمون سر بزنی✨"
)

TEHRAN_EVENT_MESSAGE = (
    "مهدکودک‌بزرگترها تهران\n\n"
    "👫مخاطب رویداد: بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
    "📅زمان:\n"
    "پنجشنبه، ۲۶ شهریور ۱۴۰۵\n"
    "ساعت ۱۷ الی ۲۰\n\n"
    "📍مکان: \n"
    "محدوده اندرزگو، باغچه کودکی هم‌صدا\n\n"
    "☁️ هزینه: یک میلیون و ششصد و پنجاه هزارتومان\n\n"
    "🔸شرایط ثبت نام با تخفیف:\n"
    "به ازای هر دوستی که همراه با خودتون بیارید ۱۰٪ تخفیف همراهی از ما می‌گیرید.\n\n"
    "نگران تنها اومدن هم نباشید؛ ما اینجا همه باهم دوست میشیم :)"
)

ESFAHAN_EVENT_MESSAGE = (
    "مهدکودک‌بزرگترها اصفهان\n\n"
    "👫مخاطب رویداد: بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
    "📅زمان:\n"
    "پنجشنبه، ۱۹ شهریور ۱۴۰۵\n"
    "ساعت ۱۷ تا ۲۰\n\n"
    "📍مکان: \n"
    "کودکستان و پیش دبستانی باغ طوبی، خیابان دانشگاه\n\n"
    "☁️ هزینه: ۹۸۰ هزارتومان\n\n"
    "🔸شرایط ثبت نام با تخفیف:\n"
    "به ازای هر دوستی که همراه با خودتون بیارید ۱۰٪ تخفیف همراهی از ما می‌گیرید.\n\n"
    "نگران تنها اومدن هم نباشید؛ ما اینجا همه باهم دوست میشیم :)"
)

SHIRAZ_EVENT_MESSAGE = (
    "مهدکودک‌بزرگترها شیراز\n\n"
    "👫مخاطب رویداد: بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
    "📅زمان: ۲۰ شهریور\n"
    "ساعت ۱۷:۳۰ الی ۲۰:۳۰\n\n"
    "📍مکان: باغ حوض نبش کوچه۳\n\n"
    "☁️ هزینه: ۱٬۵۵۰ هزارتومان\n\n"
    "🔸شرایط ثبت نام با تخفیف:\n"
    "به ازای هر دوستی که همراه با خودتون بیارید ۱۰٪ تخفیف همراهی از ما می‌گیرید.\n\n"
    "نگران تنها اومدن هم نباشید؛ ما اینجا همه باهم دوست میشیم :)"
)

TEHRAN_RECEIPT_MESSAGE = f"""📝 لطفا قبل از ادامه‌ی مسیر هزینه‌ی رویداد رو براساس تعداد نفرات مشخص کن:

یک نفر : 1.650 هزارتومان
دونفر : 3.135 هزارتومان
سه نفر: 4.620 هزارتومان
چهار نفر: 6.105 هزارتومان
پنج نفر: 7.590 هزارتومان

📤 حالا مبلغ رو به این شماره کارت واریز کن
و فیش واریزت رو به همراه اسم و شماره تماس و تعداد نفرات همینجا بفرست:

{CARD_NUMBER}
به نام {CARD_OWNER}"""

ESFAHAN_RECEIPT_MESSAGE = f"""📝 لطفا قبل از ادامه‌ی مسیر هزینه‌ی رویداد رو براساس تعداد نفرات مشخص کن:

یک نفر : 980 هزارتومان
دونفر : 1.862 هزارتومان
سه نفر: 2.744 هزارتومان
چهار نفر: 3.626 هزارتومان
پنج نفر: 4.508 هزارتومان
و...

📤 حالا مبلغ رو به این شماره کارت واریز کن
و فیش واریزت رو به همراه اسم و شماره تماس و تعداد نفرات همینجا بفرست:

{CARD_NUMBER}
به نام {CARD_OWNER}

💥 راستی، ارسال فیش به معنای قبول کردن قوانین استرداده پس اگه دوست داشتی، یه سر به قوانینمون بزن🫠"""

SHIRAZ_RECEIPT_MESSAGE = f"""📝 لطفا قبل از ادامه‌ی مسیر هزینه‌ی رویداد رو براساس تعداد نفرات مشخص کن:

یک نفر : 1.550 هزارتومان
دونفر :  2.945 هزارتومان
سه نفر: 4.340 هزارتومان
چهار نفر: 5.735 هزارتومان
پنج نفر: 7.130 هزارتومان
و...

📤 حالا مبلغ رو به این شماره کارت واریز کن
و فیش واریزت رو به همراه اسم و شماره تماس و تعداد نفرات همینجا بفرست:

{CARD_NUMBER}
به نام {CARD_OWNER}

💥 راستی، ارسال فیش به معنای قبول کردن قوانین استرداده پس اگه دوست داشتی، یه سر به قوانینمون بزن🫠"""

MASHHAD_EVENT_MESSAGE = (
    "اولین مهدکودک‌بزرگترهای مشهد\n\n"
    "👫مخاطب رویداد: بزرگسالان ۱۸ سال به بالا که دلشون می‌خواد یه کم بچگی کنن\n\n"
    "📅زمان:\n"
    "جمعه، ۲۰ شهریور ۱۴۰۵\n\n"
    "📍مکان: کوثر شمالی ۱، خانه کودک بانی شاد\n\n"
    "☁️ هزینه: ۸۵۰ هزارتومان\n\n"
    "🔸شرایط ثبت نام با تخفیف:\n"
    "به ازای هر دوستی که همراه با خودتون بیارید ۱۰٪ تخفیف همراهی از ما می‌گیرید.\n\n"
    "نگران تنها اومدن هم نباشید؛ ما اینجا همه باهم دوست میشیم :)"
)

MASHHAD_RECEIPT_MESSAGE = f"""📝 لطفا قبل از ادامه‌ی مسیر هزینه‌ی رویداد رو براساس تعداد نفرات مشخص کن:

یک نفر : 850 هزارتومان
دونفر : 1.615 هزارتومان
سه نفر: 2.380 هزارتومان
چهار نفر: 3.145 هزارتومان
پنج نفر: 3.910 هزارتومان
و...

📤 حالا مبلغ رو به این شماره کارت واریز کن
و فیش واریزت رو به همراه اسم و شماره تماس و تعداد نفرات همینجا بفرست:

{CARD_NUMBER}
به نام {CARD_OWNER}

💥 راستی، ارسال فیش به معنای قبول کردن قوانین استرداده پس اگه دوست داشتی، یه سر به قوانینمون بزن🫠"""

REFUND_RULES_MESSAGE = (
    "🧸 قوانین استرداد ثبت‌نام «مهدکودک بزرگترها»\n\n"
    "ما توی مهدکودک بزرگترها می‌خوایم هم برنامه‌هامون منظم باشه، هم شما با خیال راحت ثبت‌نام کنید. "
    "برای همین قوانین استرداد رو اینجا کامل براتون نوشتیم🫶🏻:\n\n"
    "📅 ۱. بازه زمانی استرداد\n\n"
    "اگر تا ۴۸ ساعت قبل از شروع برنامه انصراف بدید، هزینه‌تون به‌صورت کامل قابل استرداده.\n"
    "(بزرگسالیم و قول‌ و قرار داریم😌)\n\n"
    "💸 ۲. نحوه استرداد\n\n"
    "در بازه‌ی مجاز، هزینه به انتخاب شما:\n"
    "کامل بازپرداخت میشه.\n"
    "یا\n"
    "تبدیل میشه به اعتبار برای شرکت در برنامه‌های بعدی.\n"
    "(برای اونایی که هی دلشون می‌خواد برگردن مهد 🤭)\n\n"
    "⏱️ ۳. سرعت بررسی\n\n"
    "درخواست استرداد شما در کمتر از ۶ ساعت بررسی میشه.\n"
    "(چون می‌دونیم حوصله معطلی ندارین.)\n\n"
    "🤧 ۴. استثنا: مریضی\n\n"
    "اگه قبل از برنامه مریض شدید و تا ۲۴ ساعت قبل به ما اطلاع بدید، هزینه همچنان قابل استرداده.\n"
    "سلامتی‌تون مهم‌تر از هر برنامه‌ایه ❤️\n\n"
    "🛎️ ۵. مسیر درخواست استرداد\n\n"
    "برای ثبت درخواست فقط کافیه به پشتیبانی پیام بدید:\n"
    f"@{SUPPORT_USERNAME}\n"
    "(پشتیبانی ما از مربیای مهربون مهد هم مهربون‌تره 🥺)"
)

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

# ------------------------- توابع دیتابیس شهرها -------------------------

def load_databases():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_databases(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def city_selection_keyboard() -> ReplyKeyboardMarkup:
    items = list(CITY_DISPLAY_NAMES.items())
    rows = []
    for i in range(0, len(items), 2):
        row = [KeyboardButton(items[i][1])]
        if i + 1 < len(items):
            row.append(KeyboardButton(items[i + 1][1]))
        rows.append(row)
    rows.append([KeyboardButton(CANCEL_LABEL)])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)

def db_action_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(DB_ACTION_LABELS["set"])],
            [KeyboardButton(DB_ACTION_LABELS["add"])],
            [KeyboardButton(DB_ACTION_LABELS["send"])],
            [KeyboardButton(DB_ACTION_LABELS["collect"])],
            [KeyboardButton(DB_ACTION_LABELS["view"])],
            [KeyboardButton(CANCEL_LABEL)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def collecting_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[KeyboardButton(STOP_COLLECT_LABEL)]], resize_keyboard=True)

def cancel_only_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[KeyboardButton(CANCEL_LABEL)]], resize_keyboard=True, one_time_keyboard=True)

def clear_db_flow(context: ContextTypes.DEFAULT_TYPE):
    context.user_data["db_flow"] = None
    context.user_data["db_city"] = None
    context.user_data["db_action"] = None

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
        keyboard.append([
            InlineKeyboardButton("🔒 بستن مشهد", callback_data="close_mashhad"),
            InlineKeyboardButton("🔓 باز کردن مشهد", callback_data="open_mashhad"),
        ])
        keyboard.append([
            InlineKeyboardButton("🔒 بستن رشت", callback_data="close_rasht"),
            InlineKeyboardButton("🔓 باز کردن رشت", callback_data="open_rasht"),
        ])
        keyboard.append([
            InlineKeyboardButton("🔒 بستن یزد", callback_data="close_yazd"),
            InlineKeyboardButton("🔓 باز کردن یزد", callback_data="open_yazd"),
        ])
        keyboard.append([
            InlineKeyboardButton("🗂 مدیریت دیتابیس‌های شهرها", callback_data="db_menu"),
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    greeting = (
        "سلام 🌱\n"
        "خوشحالیم که می‌خوای بیای تا برای چند لحظه زندگی روزمره رو متوقف کنیم🥰"
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

    elif query.data == "db_menu":
        if update.effective_user.id != ADMIN_CHAT_ID:
            return
        context.user_data["db_flow"] = "choosing_city"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="کدوم شهر رو می‌خوای مدیریت کنی؟",
            reply_markup=city_selection_keyboard(),
        )

    elif query.data == "event_kindergarten":
        def city_status(city):
            return "✅ " if registration_status[city] else ""

        keyboard = [
            [
                InlineKeyboardButton(f"{city_status('esfahan')}اصفهان", callback_data="session_esfahan"),
                InlineKeyboardButton(f"{city_status('tehran')}تهران", callback_data="session_tehran"),
            ],
            [
                InlineKeyboardButton(f"{city_status('shiraz')}شیراز", callback_data="session_shiraz"),
                InlineKeyboardButton(f"{city_status('mashhad')}مشهد", callback_data="session_mashhad"),
            ],
            [
                InlineKeyboardButton(f"{city_status('rasht')}رشت", callback_data="session_rasht"),
                InlineKeyboardButton(f"{city_status('yazd')}یزد", callback_data="session_yazd"),
            ],
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
            await query.edit_message_text(SHIRAZ_EVENT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=closed_event_keyboard("shiraz"))

    elif query.data == "session_mashhad":
        context.user_data["city"] = "مشهد"
        if registration_status["mashhad"]:
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data="start_receipt_mashhad")],
                [InlineKeyboardButton("بازگشت", callback_data="event_kindergarten")],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            ]
            await query.edit_message_text(MASHHAD_EVENT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=closed_event_keyboard("mashhad"))

    elif query.data == "session_rasht":
        context.user_data["city"] = "رشت"
        if registration_status["rasht"]:
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data="start_receipt_rasht")],
                [InlineKeyboardButton("بازگشت", callback_data="event_kindergarten")],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            ]
            await query.edit_message_text(TEHRAN_EVENT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=closed_event_keyboard("rasht"))

    elif query.data == "session_yazd":
        context.user_data["city"] = "یزد"
        if registration_status["yazd"]:
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data="start_receipt_yazd")],
                [InlineKeyboardButton("بازگشت", callback_data="event_kindergarten")],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            ]
            await query.edit_message_text(TEHRAN_EVENT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=closed_event_keyboard("yazd"))

    elif query.data == "start_receipt_tehran":
        context.user_data["ready_for_receipt"] = "tehran"
        keyboard = [
            [InlineKeyboardButton("🧸 قوانین استرداد", callback_data="rules_tehran")],
            [InlineKeyboardButton("بازگشت", callback_data="session_tehran")],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
        ]
        await query.edit_message_text(TEHRAN_RECEIPT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "start_receipt_esfahan":
        context.user_data["ready_for_receipt"] = "esfahan"
        keyboard = [
            [InlineKeyboardButton("🧸 قوانین استرداد", callback_data="rules_esfahan")],
            [InlineKeyboardButton("بازگشت", callback_data="session_esfahan")],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
        ]
        await query.edit_message_text(ESFAHAN_RECEIPT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "start_receipt_shiraz":
        context.user_data["ready_for_receipt"] = "shiraz"
        keyboard = [
            [InlineKeyboardButton("🧸 قوانین استرداد", callback_data="rules_shiraz")],
            [InlineKeyboardButton("بازگشت", callback_data="session_shiraz")],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
        ]
        await query.edit_message_text(
            SHIRAZ_RECEIPT_MESSAGE,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "start_receipt_mashhad":
        context.user_data["ready_for_receipt"] = "mashhad"
        keyboard = [
            [InlineKeyboardButton("🧸 قوانین استرداد", callback_data="rules_mashhad")],
            [InlineKeyboardButton("بازگشت", callback_data="session_mashhad")],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
        ]
        await query.edit_message_text(MASHHAD_RECEIPT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "start_receipt_rasht":
        context.user_data["ready_for_receipt"] = "rasht"
        keyboard = [
            [InlineKeyboardButton("🧸 قوانین استرداد", callback_data="rules_rasht")],
            [InlineKeyboardButton("بازگشت", callback_data="session_rasht")],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
        ]
        await query.edit_message_text(TEHRAN_RECEIPT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "start_receipt_yazd":
        context.user_data["ready_for_receipt"] = "yazd"
        keyboard = [
            [InlineKeyboardButton("🧸 قوانین استرداد", callback_data="rules_yazd")],
            [InlineKeyboardButton("بازگشت", callback_data="session_yazd")],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
        ]
        await query.edit_message_text(TEHRAN_RECEIPT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("rules_"):
        current_city = query.data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("بازگشت به نهایی کردن ثبت‌نام", callback_data=f"start_receipt_{current_city}")]
        ]
        await query.edit_message_text(REFUND_RULES_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("open_") or query.data.startswith("close_"):
        city = query.data.split("_")[1]
        registration_status[city] = query.data.startswith("open")
        state = "باز شد ✅" if registration_status[city] else "بسته شد ❌"
        await query.edit_message_text(f"ثبت‌نام برای {city} {state}", reply_markup=support_back_channel("start"))

    elif query.data.startswith("notify_"):
        city_key = query.data.split("_", 1)[1]
        context.user_data["notify_city"] = city_key
        city_name = CITY_DISPLAY_NAMES.get(city_key, city_key)

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

    sender_info = f"از طرف {user.full_name} (@{user.username or 'بدون نام کاربری'})\nآیدی عددی: {user_id}"
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

# ------------------------- ارسال پیام دستی توسط ادمین -------------------------

async def send_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text("فرمت درست: /send <آیدی عددی> <متن پیام>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ آیدی باید عددی باشه.")
        return

    message_text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=target_id, text=message_text)
        await update.message.reply_text("✅ پیام ارسال شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ ارسال ناموفق بود: {e}")

# ------------------------- ارسال پیام به چند نفر -------------------------

async def broadcast_to_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text("فرمت درست: /broadcast <آیدی۱> <آیدی۲> ... <متن پیام>")
        return

    target_ids = []
    message_words = []
    for i, word in enumerate(context.args):
        if word.isdigit():
            target_ids.append(int(word))
        else:
            message_words = context.args[i:]
            break

    if not target_ids or not message_words:
        await update.message.reply_text("فرمت درست: /broadcast <آیدی۱> <آیدی۲> ... <متن پیام>")
        return

    message_text = " ".join(message_words)

    success, failed = [], []
    for uid in target_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=message_text)
            success.append(uid)
        except Exception as e:
            failed.append(f"{uid} ({e})")

    result = f"✅ ارسال شد به: {', '.join(map(str, success)) or 'هیچکس'}"
    if failed:
        result += f"\n❌ ناموفق: {', '.join(failed)}"
    await update.message.reply_text(result)

# ------------------------- مدیریت دیتابیس‌های شهرها -------------------------

async def db_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    context.user_data["db_flow"] = "choosing_city"
    await update.message.reply_text("کدوم شهر رو می‌خوای مدیریت کنی؟", reply_markup=city_selection_keyboard())


async def list_databases_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    databases = load_databases()
    lines = ["📊 دیتابیس‌های ثبت‌شده:"]
    for key, name in CITY_DISPLAY_NAMES.items():
        count = len(databases.get(key, []))
        lines.append(f"{name}: {count} نفر")
    await update.message.reply_text("\n".join(lines))


async def admin_db_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    flow = context.user_data.get("db_flow")
    if not flow:
        return

    text = update.message.text.strip()

    if text == CANCEL_LABEL:
        clear_db_flow(context)
        await update.message.reply_text("لغو شد.", reply_markup=ReplyKeyboardRemove())
        return

    if flow == "choosing_city":
        city_key = CITY_NAME_TO_KEY.get(text)
        if not city_key:
            await update.message.reply_text("لطفا یکی از دکمه‌های شهر رو انتخاب کن.")
            return
        context.user_data["db_city"] = city_key
        context.user_data["db_flow"] = "choosing_action"
        await update.message.reply_text(
            f"شهر انتخابی: {text}\nحالا چیکار کنیم؟",
            reply_markup=db_action_keyboard(),
        )
        return

    if flow == "choosing_action":
        city_key = context.user_data.get("db_city")
        action = DB_LABEL_TO_ACTION.get(text)
        if not action:
            await update.message.reply_text("لطفا یکی از دکمه‌ها رو انتخاب کن.")
            return
        context.user_data["db_action"] = action

        if action == "view":
            databases = load_databases()
            ids = databases.get(city_key, [])
            clear_db_flow(context)
            if not ids:
                city_name = CITY_DISPLAY_NAMES.get(city_key, city_key)
                await update.message.reply_text(
                    f"دیتابیس «{city_name}» خالیه.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                return
            lines = [f"{i + 1}. {uid}" for i, uid in enumerate(ids)]
            chunks, current_chunk, current_len = [], [], 0
            for line in lines:
                if current_len + len(line) + 1 > 3500:
                    chunks.append("\n".join(current_chunk))
                    current_chunk, current_len = [], 0
                current_chunk.append(line)
                current_len += len(line) + 1
            if current_chunk:
                chunks.append("\n".join(current_chunk))
            for idx, chunk_text in enumerate(chunks):
                markup = ReplyKeyboardRemove() if idx == 0 else None
                await update.message.reply_text(chunk_text, reply_markup=markup)
            return

        if action == "collect":
            context.user_data["db_flow"] = "collecting"
            await update.message.reply_text(
                "حالا هر پیامی که آیدی عددی توش باشه رو بفرست یا فوروارد کن (مثل پیام‌های فیش یا اطلاع‌رسانی).\n"
                "به محض تموم شدن، «⏹ پایان جمع‌آوری» رو بزن.",
                reply_markup=collecting_keyboard(),
            )
            return

        context.user_data["db_flow"] = "awaiting_input"
        if action == "send":
            prompt = "متن پیامی که می‌خوای ارسال بشه رو بفرست:"
        else:
            prompt = "آیدی‌های عددی رو بفرست (هر تعداد که می‌خوای، با فاصله یا خط جدید جدا کن):"
        await update.message.reply_text(prompt, reply_markup=cancel_only_keyboard())
        return

    if flow == "collecting":
        city_key = context.user_data.get("db_city")
        city_name = CITY_DISPLAY_NAMES.get(city_key, city_key)

        if text == STOP_COLLECT_LABEL:
            databases = load_databases()
            total = len(databases.get(city_key, []))
            clear_db_flow(context)
            await update.message.reply_text(
                f"✅ جمع‌آوری برای «{city_name}» تموم شد. تعداد کل فعلی: {total}",
                reply_markup=ReplyKeyboardRemove(),
            )
            return

        found_ids = [int(x) for x in re.findall(r"آیدی عددی:\s*(\d+)", text)]
        if not found_ids:
            await update.message.reply_text("❌ توی این پیام آیدی عددی پیدا نشد. پیام بعدی رو بفرست.")
            return

        databases = load_databases()
        existing = set(databases.get(city_key, []))
        new_ones = [uid for uid in found_ids if uid not in existing]
        existing.update(found_ids)
        databases[city_key] = list(existing)
        save_databases(databases)

        await update.message.reply_text(
            f"➕ اضافه شد: {', '.join(map(str, found_ids))}"
            + (f" (جدید: {', '.join(map(str, new_ones))})" if new_ones != found_ids else "")
            + f"\nمجموع فعلی «{city_name}»: {len(existing)}"
        )
        return

    if flow == "awaiting_input":
        city_key = context.user_data.get("db_city")
        action = context.user_data.get("db_action")
        city_name = CITY_DISPLAY_NAMES.get(city_key, city_key)
        databases = load_databases()

        if action in ("set", "add"):
            ids = [int(tok) for tok in text.replace(",", " ").split() if tok.isdigit()]
            if not ids:
                await update.message.reply_text("هیچ آیدی معتبری پیدا نشد. دوباره امتحان کن یا لغو بزن.")
                return
            if action == "set":
                databases[city_key] = list(dict.fromkeys(ids))
            else:
                existing = set(databases.get(city_key, []))
                existing.update(ids)
                databases[city_key] = list(existing)
            save_databases(databases)
            await update.message.reply_text(
                f"✅ دیتابیس «{city_name}» به‌روز شد. تعداد کل: {len(databases[city_key])}",
                reply_markup=ReplyKeyboardRemove(),
            )

        elif action == "send":
            target_ids = list(dict.fromkeys(databases.get(city_key, [])))
            if not target_ids:
                await update.message.reply_text(
                    f"دیتابیسی برای «{city_name}» ثبت نشده.",
                    reply_markup=ReplyKeyboardRemove(),
                )
            else:
                success_count = 0
                failed_ids = []
                for uid in target_ids:
                    for attempt in range(2):
                        try:
                            await context.bot.send_message(chat_id=uid, text=text)
                            success_count += 1
                            break
                        except RetryAfter as e:
                            await asyncio.sleep(e.retry_after + 1)
                        except Exception:
                            failed_ids.append(uid)
                            break
                    await asyncio.sleep(0.05)
                result_text = f"✅ ارسال شد به {success_count} نفر از دیتابیس «{city_name}» (بدون تکرار)"
                if failed_ids:
                    result_text += f"\n❌ ناموفق برای {len(failed_ids)} نفر:\n" + "\n".join(map(str, failed_ids))
                await update.message.reply_text(result_text, reply_markup=ReplyKeyboardRemove())

        clear_db_flow(context)
        return

# ------------------------- تنظیمات بات و Flask -------------------------

async def set_bot_commands(app):
    await app.bot.set_my_commands([BotCommand("start", "شروع ربات")])

telegram_app = ApplicationBuilder().token(BOT_TOKEN).post_init(set_bot_commands).build()
app = Flask(__name__)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("send", send_to_user))
telegram_app.add_handler(CommandHandler("broadcast", broadcast_to_users))
telegram_app.add_handler(CommandHandler("db", db_menu_command))
telegram_app.add_handler(CommandHandler("listdb", list_databases_command))
telegram_app.add_handler(CallbackQueryHandler(button_handler))
telegram_app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
telegram_app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
telegram_app.add_handler(MessageHandler(filters.Regex("^انصراف$"), cancel_notify_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_db_text_handler))

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def _startup():
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
        loop.run_until_complete(telegram_app.process_update(update))
        return "OK", 200
    return "Server is running!", 200

if __name__ == "__main__":
    loop.run_until_complete(_startup())
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
