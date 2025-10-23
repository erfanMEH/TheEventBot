import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==========================
# اطلاعات ربات و متغیرها
# ==========================
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # امن: از Environment Variable بخون
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "6687139776"))
SUPPORT_USERNAME = 'samin_dh'
CHANNEL_USERNAME = 'bigkidkindergarten'

# ظرفیت و وضعیت ثبت‌نام رویداد اصفهان
confirmed_users_esfahan = set()
registration_closed_esfahan = False

MAX_CAPACITY_ESFAHAN = None  # الان غیرفعاله، کنترل دستی داری

CARD_NUMBER = '6219861815202733'
CARD_OWNER = 'ثمین دهقانی'

# ==========================
# دکمه‌های بازگشت و پشتیبانی
# ==========================
def support_back_channel(callback_data):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("بازگشت", callback_data=callback_data)],
        [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ])

# ==========================
# پیام فیش ثابت
# ==========================
RECEIPT_MESSAGE = f"""📝 لطفا قبل از ادامه‌ی مسیر هزینه‌ی رویداد رو براساس تعداد نفرات مشخص کن:

یک نفر : ۴۵۰ هزارتومان
دونفر : ۸۵۵ هزارتومان
سه نفر: ۱,۲۶۰ هزارتومان
چهار نفر: ۱,۶۶۵ هزارتومان 
پنج نفر: ۲,۰۷۰ هزارتومان

📤 حالا مبلغ رو به این شماره کارت واریز کن و فیش واریزت رو به همراه اسم و شماره تماس و تعداد نفرات همینجا بفرست:

{CARD_NUMBER}
به نام {CARD_OWNER}"""

# ==========================
# شروع ربات
# ==========================
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

    greeting = (
        "سلام 🌱\n"
        "خوشحالم که می‌خواین بیاین تا برای چند لحظه زندگیِ روزمره رو متوقف کنیم🥰"
    )

    if update.message:
        await update.message.reply_text(greeting, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(greeting, reply_markup=reply_markup)

# ==========================
# هندلر دکمه‌ها
# ==========================
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
        await query.edit_message_text(
            "✨️ از ایونت کدوم شهرمون می‌خوای باخبر بشی؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'session_esfahan':
        context.user_data["city"] = "esfahan"
        context.user_data["ready_for_receipt"] = True
        keyboard = [
            [InlineKeyboardButton("ارسال فیش ثبت‌نام", callback_data='start_receipt')],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        message = RECEIPT_MESSAGE
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'start_receipt':
        context.user_data["ready_for_receipt"] = True
        await query.edit_message_text(RECEIPT_MESSAGE,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("بازگشت", callback_data='session_esfahan')],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ])
        )

    elif query.data == 'session_tehran':
        context.user_data["city"] = "tehran"
        context.user_data["ready_for_receipt"] = False
        message = (
            "سلام 🌱\n"
            "خوشحالیم که می‌خواین بیاین تا برای چند لحظه زندگیِ روزمره رو متوقف کنیم🥰\n\n"
            "👫 مخاطب رویداد : بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n\n"
            "📅 زمان:\n"
            "در حال برنامه‌ریزی برای تاریخ بعدی رویدادمون هستیم.\n"
            "اطلاع‌رسانی‌ها از طریق کانال ما به آدرس @bigkidkindergarten انجام میشه ✌🏻\n\n"
            "📍 مکان:\n"
            "هر رویداد در فضای متفاوتی برگزار میشه که بعد از مشخص شدن تاریخ اعلام می‌کنیم.\n\n"
            "☁️ هزینه:\n"
            "واریز هزینه و ثبت‌نام هم بعد از مشخص شدن تاریخ و مکان برگزاری به اطلاع کسانی که می‌خوان ثبت‌نام کنن می‌رسه."
        )
        keyboard = [
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'support':
        await query.edit_message_text(
            f"اگه سوالی داشتی یا نیاز به کمک داشتی، با آیدی @{SUPPORT_USERNAME} تماس بگیر 💌",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ])
        )

    elif query.data == 'close_registration_esfahan':
        registration_closed_esfahan = True
        await query.edit_message_text("❌ ثبت‌نام برای رویداد اصفهان بسته شد.")

    elif query.data == 'open_registration_esfahan':
        registration_closed_esfahan = False
        await query.edit_message_text(RECEIPT_MESSAGE,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ارسال فیش ثبت‌نام", callback_data='start_receipt')],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ])
        )

# ==========================
# هندلر دریافت عکس فیش
# ==========================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = context.user_data.get("city")
    ready = context.user_data.get("ready_for_receipt", False)

    if city != "esfahan" or not ready:
        await update.message.reply_text(
            "❌ لطفاً ابتدا از مسیر ثبت‌نام، شهر رو انتخاب و دکمه «ارسال فیش ثبت‌نام» رو بزنید 🌱",
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

    # پیام فیش همیشه نمایش داده بشه
    await update.message.reply_text(RECEIPT_MESSAGE,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ])
    )

# ==========================
# تنظیم دستور /start
# ==========================
async def set_bot_commands(app):
    commands = [BotCommand("start", "شروع ربات")]
    await app.bot.set_my_commands(commands)

# ==========================
# اجرای ربات
# ==========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    app.post_init = set_bot_commands

    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()
