import os
import asyncio
import jdatetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from datetime import timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "8486591461"))
SUPPORT_USERNAME = 'MahdeKoodakSupport'
CHANNEL_USERNAME = 'bigkidkindergarten'
CARD_NUMBER = '6219861815202733'
CARD_OWNER = 'ثمین دهقانی'

registration_closed_esfahan = False

def support_back_channel(callback_data):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("بازگشت", callback_data=callback_data)],
        [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ])

RECEIPT_MESSAGE = f"""📝 لطفا قبل از ادامه‌ی مسیر هزینه‌ی رویداد رو براساس تعداد نفرات مشخص کن:

یک نفر : ۴۵۰ هزارتومان
دونفر : ۸۵۵ هزارتومان
سه نفر: ۱,۲۶۰ هزارتومان
چهار نفر: ۱,۶۶۵ هزارتومان
پنج نفر: ۲,۰۷۰ هزارتومان

📤 حالا مبلغ رو به این شماره کارت واریز کن و فیش واریزت رو به همراه اسم و شماره تماس و تعداد نفرات همینجا بفرست:

{CARD_NUMBER}
به نام {CARD_OWNER}"""

# مرحله خوشامد و انتخاب مسیر
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✨ شهرتو انتخاب کن", callback_data='event_kindergarten')],
        [InlineKeyboardButton("پشتیبانی", callback_data='support')],
        [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ]

    if update.effective_user.id == ADMIN_CHAT_ID:
        keyboard.append([
            InlineKeyboardButton("🔒 بستن ثبت‌نام اصفهان", callback_data='close_registration_esfahan'),
            InlineKeyboardButton("🔓 باز کردن ثبت‌نام اصفهان", callback_data='open_registration_esfahan')
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    greeting = "سلام 🌱\nخوشحالیم که اومدی! می‌خوای با بات چه کاری انجام بدی؟"

    if update.message:
        await update.message.reply_text(greeting, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(greeting, reply_markup=reply_markup)

# مدیریت دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global registration_closed_esfahan
    query = update.callback_query
    await query.answer()

    # مرحله انتخاب شهر
    if query.data == 'event_kindergarten':
        esfahan_status = "✅" if not registration_closed_esfahan else "❌"
        tehran_status = "❌"
        shiraz_status = "❌"

        keyboard = [
            [InlineKeyboardButton(f"{esfahan_status} اصفهان", callback_data='session_esfahan')],
            [InlineKeyboardButton(f"{tehran_status} تهران", callback_data='session_tehran')],
            [InlineKeyboardButton(f"{shiraz_status} شیراز", callback_data='session_shiraz')],
            [InlineKeyboardButton("بازگشت", callback_data='start')],
            [InlineKeyboardButton("پشتیبانی", callback_data='support')],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await query.edit_message_text("✨ کدوم شهرو می‌خوای شرکت کنی؟", reply_markup=InlineKeyboardMarkup(keyboard))

    # انتخاب اصفهان
    elif query.data == 'session_esfahan':
        context.user_data["city"] = "esfahan"
        context.user_data["ready_for_receipt"] = True
        message = (
            "مهدکودک‌بزرگترها اصفهان\n\n"
            "👫 مخاطب رویداد: بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
            "📅 زمان: ۹ آبان ۱۴۰۴ ساعت ۱۸ الی ۲۱\n"
            "📍 مکان: استودیو یوگا پرانا (خیابان کارگر)\n"
            "☁️ هزینه: ۴۵۰ هزارتومان\n\n"
            "🔸شرایط ثبت نام با تخفیف:\n"
            "به ازای هر دوستی که همراه خودتون بیارید ۱۰٪ تخفیف همراهی از ما می‌گیرید.\n"
            "(نگران تنها اومدن هم نباشید؛ همه باهم دوست میشیم :)"
        )
        keyboard = [
            [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data='start_receipt')],
            [InlineKeyboardButton("بازگشت", callback_data='event_kindergarten')],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    # انتخاب تهران
    elif query.data == 'session_tehran':
        context.user_data["city"] = "tehran"
        context.user_data["ready_for_receipt"] = False
        message = (
            "سلام 🌱\nخوشحالیم که میخواین بیاین!\n\n"
            "👫 مخاطب رویداد: بزرگسالان ۱۸ سال به بالا\n"
            "📅 زمان: در حال برنامه‌ریزی برای تاریخ بعدی\n"
            "📍 مکان: بعدا اعلام می‌شود\n"
            "☁️ هزینه: بعدا اعلام می‌شود"
        )
        keyboard = [
            [InlineKeyboardButton("بازگشت", callback_data='event_kindergarten')],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    # انتخاب شیراز
    elif query.data == 'session_shiraz':
        context.user_data["city"] = "shiraz"
        context.user_data["ready_for_receipt"] = False
        message = (
            "سلام 🌱\nخوشحالیم که میخواین بیاین!\n\n"
            "👫 مخاطب رویداد: بزرگسالان ۱۸ سال به بالا\n"
            "📅 زمان: در حال برنامه‌ریزی برای تاریخ بعدی\n"
            "📍 مکان: بعدا اعلام می‌شود\n"
            "☁️ هزینه: بعدا اعلام می‌شود"
        )
        keyboard = [
            [InlineKeyboardButton("بازگشت", callback_data='event_kindergarten')],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    # شروع ثبت‌نام
    elif query.data == 'start_receipt':
        if registration_closed_esfahan:
            await query.edit_message_text(
                "❌ ثبت‌نام برای رویداد اصفهان بسته شده.\nبرای اطلاعات بیشتر با پشتیبانی تماس بگیرید 💌",
                reply_markup=support_back_channel('event_kindergarten')
            )
            return
        context.user_data["ready_for_receipt"] = True
        await query.edit_message_text(
            RECEIPT_MESSAGE,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ])
        )

    # مدیریت باز و بسته کردن ثبت‌نام اصفهان
    elif query.data == 'close_registration_esfahan':
        registration_closed_esfahan = True
        await query.edit_message_text(
            "❌ ثبت‌نام برای رویداد اصفهان بسته شد.",
            reply_markup=support_back_channel('event_kindergarten')
        )

    elif query.data == 'open_registration_esfahan':
        registration_closed_esfahan = False
        await query.edit_message_text(
            "✅ ثبت‌نام برای رویداد اصفهان باز شد.",
            reply_markup=support_back_channel('event_kindergarten')
        )

    # پشتیبانی
    elif query.data == 'support':
        await query.edit_message_text(
            "اگه سوالی داشتی یا نیاز به کمک داشتی، با آیدی @MahdeKoodakSupport ارتباط بگیر 💌",
            reply_markup=support_back_channel('event_kindergarten')
        )

    # تایید/رد فیش‌ها
    elif query.data.startswith("confirm_"):
        user_id = int(query.data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="✅ ثبت‌نام شما تأیید شد! خوشحالیم که می‌بینیمتون 🌱")
        current_caption = query.message.caption or ""
        now = jdatetime.datetime.now()
        date_str = f"{now.day} {now.strftime('%B')} {now.year}"
        new_caption = f"{current_caption}\n\n✅ تأیید شد در تاریخ {date_str}"
        try:
            await query.edit_message_caption(caption=new_caption)
            await query.edit_message_reply_markup(reply_markup=None)
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
            await query.edit_message_caption(caption="❌ این فیش رد شد (اطلاعات ناقص)")
            await query.edit_message_reply_markup(reply_markup=None)
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
            await query.edit_message_caption(caption="❌ این فیش رد شد (مبلغ اشتباه)")
            await query.edit_message_reply_markup(reply_markup=None)
        except:
            pass

# مدیریت ارسال عکس فیش
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = context.user_data.get("city")
    ready = context.user_data.get("ready_for_receipt", False)

    if city != "esfahan" or not ready or registration_closed_esfahan:
        await update.message.reply_text(
            "❌ ثبت‌نام برای رویداد اصفهان بسته شده یا مسیر ثبت‌نام کامل طی نشده.",
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

    context.user_data["ready_for_receipt"] = False

    await update.message.reply_text(
        "فیش شما با موفقیت دریافت شد 💌\nدر حال بررسی توسط تیم ثبت‌نام هستیم. به‌زودی نتیجه رو بهتون اطلاع می‌دیم 🌱"
    )

# ست کردن دستورات بات
async def set_bot_commands(app):
    await app.bot.set_my_commands([BotCommand("start", "شروع ربات")])

# اجرای ربات
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    await app.initialize()
    await set_bot_commands(app)
    print("ربات در حال اجراست...")
    await app.run_polling()

if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())

