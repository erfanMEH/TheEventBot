import os
import asyncio
import jdatetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
)
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

# 🧹 دستور ریست ادمین (پاک کردن پیام‌ها)
async def reset_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ فقط ادمین می‌تونه از این دستور استفاده کنه.")
        return

    await update.message.reply_text("🔄 در حال پاک‌سازی پیام‌های بات و ادمین، لطفاً صبر کنید...")

    try:
        chat = update.effective_chat
        # گرفتن پیام‌های اخیر (حدود 100 پیام)
        async for msg in context.bot.get_chat(chat.id).iter_history(limit=100):
            if msg.from_user and (msg.from_user.is_bot or msg.from_user.id == ADMIN_CHAT_ID):
                try:
                    await context.bot.delete_message(chat.id, msg.message_id)
                except:
                    continue
        await context.bot.send_message(chat.id, "✅ همه‌ی پیام‌های بات و ادمین پاک شدند.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در پاک کردن پیام‌ها: {e}")

# ✅ start
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

# ✅ button handler
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
        message = ("سلام 🌱\nخوشحالیم که می‌خواین بیاین تا برای چند لحظه زندگیِ روزمره رو متوقف کنیم🥰\n\n"
                   "👫 مخاطب رویداد : بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
                   "📅 زمان:\nدر حال برنامه‌ریزی برای تاریخ بعدی رویدادمون هستیم.\n"
                   "اطلاع‌رسانی‌ها از طریق کانال ما به آدرس @bigkidkindergarten انجام میشه ✌🏻\n\n"
                   "📍 مکان:\nهر رویداد در فضای متفاوتی برگزار میشه که بعد از مشخص شدن تاریخ اعلام می‌کنیم.\n\n"
                   "☁️ هزینه:\nواریز هزینه و ثبت‌نام هم بعد از مشخص شدن تاریخ و مکان برگزاری به اطلاع کسانی که می‌خوان ثبت‌نام کنن می‌رسه.")
        await query.edit_message_text(message, reply_markup=support_back_channel('event_kindergarten'))

    elif query.data == 'support':
        await query.edit_message_text(
            "اگه سوالی داشتی یا نیاز به کمک داشتی، با آیدی @MahdeKoodakSupport ارتباط بگیر 💌",
            reply_markup=support_back_channel('event_kindergarten')
        )

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
    await update.message.reply_text("فیش شما با موفقیت دریافت شد 💌\nدر حال بررسی توسط تیم ثبت‌نام هستیم 🌱")

async def set_bot_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "شروع ربات"),
        BotCommand("reset", "پاک کردن پیام‌های بات و ادمین")
    ])

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('reset', reset_messages))
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
