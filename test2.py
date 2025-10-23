import os
import asyncio
import jdatetime
import pytz
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✨️ از ایونت کدوم شهرمون می‌خوای باخبر بشی؟", callback_data='event_kindergarten')],
        [InlineKeyboardButton("پشتیبانی", callback_data='support')],
        [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ]
    if update.effective_user.id == ADMIN_CHAT_ID:
        keyboard.append([
            InlineKeyboardButton("🔒 بستن ثبت‌نام اصفهان", callback_data='close_registration_esfahan'),
            InlineKeyboardButton("🔓 باز کردن ثبت‌نام اصفهان", callback_data='open_registration_esfahan')
        ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    greeting = "سلام 🌱\nخوشحالم که می‌خواین بیاین تا برای چند لحظه زندگیِ روزمره رو متوقف کنیم🥰"
    if update.message:
        await update.message.reply_text(greeting, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(greeting, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global registration_closed_esfahan
    query = update.callback_query
    await query.answer()

    if query.data == 'event_kindergarten':
        keyboard = [
            [InlineKeyboardButton("اصفهان", callback_data='session_esfahan')],
            [InlineKeyboardButton("تهران", callback_data='session_tehran')],
            [InlineKeyboardButton("پشتیبانی", callback_data='support')],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await query.edit_message_text("✨️ از ایونت کدوم شهرمون می‌خوای باخبر بشی؟",
                                      reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'session_esfahan':
        context.user_data["city"] = "esfahan"
        context.user_data["ready_for_receipt"] = True
        message = (
            "مهدکودک‌بزرگترها اصفهان\n\n"
            "👫مخاطب رویداد : بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
            "📅زمان:\n۸ آبان ۱۴۰۴\nساعت ۱۸ الی ۲۱\n\n"
            "📍مکان:\nاستودیو یوگا پرانا (خیابان کارگر)\n\n"
            "☁️ هزینه: ۴۵۰ هزارتومان\n\n"
            "🔸شرایط ثبت نام با تخفیف:\n"
            "به ازای هر دوستی که همراه با خودتون بیارید ۱۰٪ تخفیف همراهی از ما می‌گیرید.\n\n"
            "(نگران تنها اومدن هم نباشید؛ ما اینجا همه باهم دوست میشیم :)"
        )
        keyboard = [
            [InlineKeyboardButton("نهایی کردن ثبت‌نام", callback_data='start_receipt')],
            [InlineKeyboardButton("بازگشت", callback_data='event_kindergarten')],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'start_receipt':
        if registration_closed_esfahan:
            await query.edit_message_text(
                "❌ ثبت‌نام برای رویداد اصفهان بسته شده.\nبرای اطلاعات بیشتر با پشتیبانی تماس بگیرید 💌",
                reply_markup=support_back_channel('event_kindergarten')
            )
            return

        context.user_data["ready_for_receipt"] = True
        await query.edit_message_text(RECEIPT_MESSAGE,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ])
        )

    elif query.data == 'close_registration_esfahan':
        registration_closed_esfahan = True
        await query.edit_message_text("❌ ثبت‌نام برای رویداد اصفهان بسته شد.",
                                      reply_markup=support_back_channel('event_kindergarten'))

    elif query.data == 'open_registration_esfahan':
        registration_closed_esfahan = False
        await query.edit_message_text("✅ ثبت‌نام برای رویداد اصفهان باز شد.",
                                      reply_markup=support_back_channel('event_kindergarten'))

    elif query.data == 'session_tehran':
        context.user_data["city"] = "tehran"
        context.user_data["ready_for_receipt"] = False
        message = ("سلام 🌱\nخوشحالیم که می‌خواین بیاین تا برای چند لحظه زندگیِ روزمره رو متوقف کنیم🥰\n\n"
                   "👫 مخاطب رویداد : بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
                   "📅 زمان:\nدر حال برنامه‌ریزی برای تاریخ بعدی رویدادمون هستیم.\n"
                   "اطلاع‌رسانی‌ها از طریق کانال ما به آدرس @bigkidkindergarten انجام میشه ✌🏻\n\n"
                   "📍 مکان:\nهر رویداد در فضای متفاوتی برگزار میشه که بعد از مشخص شدن تاریخ اعلام می‌کنیم.\n\n"
                   "☁️ هزینه:\nواریز هزینه و ثبت‌نام هم بعد از مشخص شدن تاریخ و مکان برگزاری به اطلاع کسانی که می‌خوان ثبت‌نام کنن می‌رسه.")
        keyboard = [
            [InlineKeyboardButton("بازگشت", callback_data='event_kindergarten')],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'support':
        await query.edit_message_text(
            "اگه سوالی داشتی یا نیاز به کمک داشتی، با آیدی @MahdeKoodakSupport ارتباط بگیر 💌",
            reply_markup=support_back_channel('event_kindergarten')
        )

    # ✅ تایید فیش با تاریخ و ساعت شمسی ایران (تهران)
    elif query.data.startswith("confirm_"):
        user_id = int(query.data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="✅ ثبت‌نام شما تأیید شد! خوشحالیم که می‌بینیمتون 🌱")

        current_caption = query.message.caption or ""

        # گرفتن زمان دقیق تهران
        tehran_tz = pytz.timezone("Asia/Tehran")
        now = datetime.now(tehran_tz)
        now_j = jdatetime.datetime.fromgregorian(datetime=now)

        date_str = f"{now_j.day} {now_j.strftime('%B')} {now_j.year}"
        time_str = now_j.strftime("%H:%M")

        new_caption = f"{current_caption}\n\n✅ تأیید شد در تاریخ {date_str} - ساعت {time_str}"

        try:
            await query.edit_message_caption(caption=new_caption)
        except:
            pass
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except:
            pass

    elif query.data.startswith("reject_info_"):
        user_id = int(query.data.split("_")[2])
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "ثبت‌نام شما رد شد. متاسفانه اطلاعات کپشن کامل نبود.\n"
                "لطفاً فیش رو دوباره ارسال کنید و در کپشن عکس، نام و نام خانوادگی و شماره تماس رو بنویسید 🌱"
            ),
            reply_markup=support_back_channel('event_kindergarten')
        )
        try:
            await query.edit_message_caption(caption="❌ این فیش رد شد (اطلاعات ناقص)")
        except:
            pass
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except:
            pass

   elif query.data.startswith("reject_amount_"):
        user_id = int(query.data.split("_")[2])
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ ثبت‌نام شما رد شد، مبلغ واریزی با تعرفه‌ی رویداد هماهنگ نبود.\n"
                "برای بررسی و تأیید نهایی، لطفاً با پشتیبانی ارتباط بگیرید 💌"
            ),
            reply_markup=support_back_channel('event_kindergarten')
        )
        try:
            await query.edit_message_caption(caption="❌ این فیش رد شد (مبلغ اشتباه)")
        except:
            pass
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except:
            pass


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = context.user_data.get("city")
    ready = context.user_data.get("ready_for_receipt", False)

    if city == "tehran":
        await update.message.reply_text(
            "هنوز رویدادی برای تهران برنامه‌ریزی نشده.\n"
            "اگر برای رویداد اصفهان ثبت‌نام کردید، نهایی کردن ثبت‌نام رو با انتخاب رویداد اصفهان انجام داده و دوباره فیش را ارسال کنید 🌱",
            reply_markup=support_back_channel('event_kindergarten')
        )
        return

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


async def set_bot_commands(app):
    await app.bot.set_my_commands([BotCommand("start", "شروع ربات")])


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

