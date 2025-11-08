import os
import asyncio
import jdatetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from datetime import timedelta

# ------------------------- تنظیمات ثابت -------------------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "8486591461"))
SUPPORT_USERNAME = 'MahdeKoodakSupport'
CHANNEL_USERNAME = 'bigkidkindergarten'
CARD_NUMBER = '6219861815202733'
CARD_OWNER = 'ثمین دهقانی'

# ------------------------- وضعیت ثبت‌نام شهرها -------------------------

registration_status = {
    "esfahan": False,
    "tehran": False,
    "shiraz": False
}

# ------------------------- پیام‌های آماده -------------------------

CLOSED_EVENT_MESSAGE = (
    "سلام🌱\n\n"
    "خوشحالیم که مشتاق حضور در جمع مهدکودک‌بزرگترها هستید\n\n"
    "در حال حاضر، در شهر انتخابیتون سانس فعالی برای ثبت‌نام نداریم و می‌تونید از طریق "
    "کانال تلگراممون از سانس‌های جدیدی که گذاشته میشه باخبر بشید✨️"
)

TEHRAN_EVENT_MESSAGE = (
    "مهدکودک‌بزرگترها تهران\n\n"
    "👫 مخاطب رویداد : بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
    "📅 زمان:\nپنجشنبه، 22 آبان 1404\nساعت 17 الی 20\n\n"
    "📍 مکان:\nباغچه کودکی هم‌صدا\n\n"
    "☁️ هزینه: 590 هزارتومان\n\n"
    "🔸 شرایط ثبت نام با تخفیف:\n"
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

# پیام فیش اصفهان (اگر باز بشه)
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

# ------------------------- شروع /start -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✨ شهرتو انتخاب کن", callback_data='event_kindergarten')],
        [InlineKeyboardButton("پشتیبانی", callback_data='support')],
        [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ]

    # دکمه‌های مخصوص ادمین برای کنترل وضعیت شهرها
    if update.effective_user.id == ADMIN_CHAT_ID:
        keyboard.append([
            InlineKeyboardButton("🔒 بستن اصفهان", callback_data='close_esfahan'),
            InlineKeyboardButton("🔓 باز کردن اصفهان", callback_data='open_esfahan')
        ])
        keyboard.append([
            InlineKeyboardButton("🔒 بستن تهران", callback_data='close_tehran'),
            InlineKeyboardButton("🔓 باز کردن تهران", callback_data='open_tehran')
        ])
        keyboard.append([
            InlineKeyboardButton("🔒 بستن شیراز", callback_data='close_shiraz'),
            InlineKeyboardButton("🔓 باز کردن شیراز", callback_data='open_shiraz')
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

    city_data = {
        "esfahan": "session_esfahan",
        "tehran": "session_tehran",
        "shiraz": "session_shiraz"
    }

    # مرحله انتخاب شهر
    if query.data == 'event_kindergarten':
        def city_status(city):
            return "✅" if registration_status[city] else "❌"

        keyboard = [
            [InlineKeyboardButton(f"{city_status('esfahan')} اصفهان", callback_data='session_esfahan')],
            [InlineKeyboardButton(f"{city_status('tehran')} تهران", callback_data='session_tehran')],
            [InlineKeyboardButton(f"{city_status('shiraz')} شیراز", callback_data='session_shiraz')],
            [InlineKeyboardButton("بازگشت", callback_data='start')],
            [InlineKeyboardButton("پشتیبانی", callback_data='support')],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await query.edit_message_text("✨ کدوم شهرو می‌خوای شرکت کنی؟", reply_markup=InlineKeyboardMarkup(keyboard))

    # رویداد تهران
    elif query.data == 'session_tehran':
        context.user_data["city"] = "tehran"
        if registration_status["tehran"]:
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data='start_receipt_tehran')],
                [InlineKeyboardButton("بازگشت", callback_data='event_kindergarten')],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ]
            await query.edit_message_text(TEHRAN_EVENT_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=support_back_channel('event_kindergarten'))

    # رویداد اصفهان
    elif query.data == 'session_esfahan':
        context.user_data["city"] = "esfahan"
        if registration_status["esfahan"]:
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data='start_receipt_esfahan')],
                [InlineKeyboardButton("بازگشت", callback_data='event_kindergarten')],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ]
            await query.edit_message_text("مهدکودک‌بزرگترها اصفهان ✨", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=support_back_channel('event_kindergarten'))

    # رویداد شیراز
    elif query.data == 'session_shiraz':
        context.user_data["city"] = "shiraz"
        if registration_status["shiraz"]:
            keyboard = [
                [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data='start_receipt_shiraz')],
                [InlineKeyboardButton("بازگشت", callback_data='event_kindergarten')],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ]
            await query.edit_message_text("مهدکودک‌بزرگترها شیراز ✨", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=support_back_channel('event_kindergarten'))

    # شروع ثبت‌نام (تهران)
    elif query.data == 'start_receipt_tehran':
        context.user_data["ready_for_receipt"] = "tehran"
        await query.edit_message_text(
            TEHRAN_RECEIPT_MESSAGE,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ])
        )

    # شروع ثبت‌نام (اصفهان)
    elif query.data == 'start_receipt_esfahan':
        context.user_data["ready_for_receipt"] = "esfahan"
        await query.edit_message_text(
            ESFAHAN_RECEIPT_MESSAGE,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ])
        )

    # مدیریت باز و بسته کردن شهرها توسط ادمین
    elif query.data.startswith("open_") or query.data.startswith("close_"):
        city = query.data.split("_")[1]
        registration_status[city] = query.data.startswith("open_")
        state = "باز شد ✅" if registration_status[city] else "بسته شد ❌"
        await query.edit_message_text(
            f"ثبت‌نام برای {city} {state}",
            reply_markup=support_back_channel('start')
        )

    # پشتیبانی
    elif query.data == 'support':
        await query.edit_message_text(
            "اگه سوالی داشتی یا نیاز به کمک داشتی، با آیدی @MahdeKoodakSupport ارتباط بگیر 💌",
            reply_markup=support_back_channel('event_kindergarten')
        )

    # تأیید / رد فیش‌ها
    elif query.data.startswith("confirm_"):
        user_id = int(query.data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="✅ ثبت‌نام شما تأیید شد! خوشحالیم که می‌بینیمتون 🌱")
        now = jdatetime.datetime.now()
        date_str = f"{now.day} {now.strftime('%B')} {now.year}"
        new_caption = f"{query.message.caption}\n\n✅ تأیید شد در تاریخ {date_str}"
        try:
            await query.edit_message_caption(caption=new_caption, reply_markup=None)
        except:
            pass

    elif query.data.startswith("reject_info_"):
        user_id = int(query.data.split("_")[2])
        await context.bot.send_message(
            chat_id=user_id,
            text="ثبت‌نام شما رد شد. لطفاً فیش رو دوباره ارسال کنید و نام و شماره تماس رو بنویسید 🌱",
            reply_markup=support_back_channel('event_kindergarten')
        )
        try:
            await query.edit_message_caption(caption="❌ این فیش رد شد (اطلاعات ناقص)", reply_markup=None)
        except:
            pass

    elif query.data.startswith("reject_amount_"):
        user_id = int(query.data.split("_")[2])
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ مبلغ واریزی با تعرفه هماهنگ نبود. برای بررسی با پشتیبانی تماس بگیر 💌",
            reply_markup=support_back_channel('event_kindergarten')
        )
        try:
            await query.edit_message_caption(caption="❌ این فیش رد شد (مبلغ اشتباه)", reply_markup=None)
        except:
            pass

# ------------------------- دریافت عکس فیش -------------------------

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = context.user_data.get("ready_for_receipt")

    # اگر شهر بسته است یا کاربر مستقیماً فیش فرستاده
    if not city or not registration_status.get(city, False):
        await update.message.reply_text(
            "❌ ثبت‌نام برای این شهر بسته شده یا مسیر ثبت‌نام کامل طی نشده.",
            reply_markup=support_back_channel('event_kindergarten')
        )
        return

    photo = update.message.photo[-1]
    caption = update.message.caption or "بدون کپشن"
    user = update.message.from_user
    user_id = user.id

    sender_info = f"از طرف {user.full_name} (@{user.username or 'بدون نام کاربری'})"
    full_caption = f"{sender_info}\n\nکپشن:\n{caption}"

    confirm_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تأیید ثبت‌نام", callback_data=f"confirm_{user_id}")],
        [InlineKeyboardButton("❌ رد به‌خاطر اطلاعات ناقص", callback_data=f"reject_info_{user_id}")],
        [InlineKeyboardButton("❌ رد به‌خاطر مبلغ اشتباه", callback_data=f"reject_amount_{user_id}")]
    ])

    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo.file_id,
        caption=full_caption,
        reply_markup=confirm_buttons
    )

    context.user_data["ready_for_receipt"] = None

    await update.message.reply_text(
        "فیش شما با موفقیت دریافت شد 💌\nدر حال بررسی توسط تیم ثبت‌نام هستیم. به‌زودی نتیجه رو بهتون اطلاع می‌دیم 🌱"
    )

# ------------------------- تنظیم دستورات ربات -------------------------

async def set_bot_commands(app):
    await app.bot.set_my_commands([BotCommand("start", "شروع ربات")])

# ------------------------- اجرای ربات -------------------------

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    await app.initialize()
    await set_bot_commands(app)
    print("✅ ربات در حال اجراست...")
    await app.run_polling()

if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())