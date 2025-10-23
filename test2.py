from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os

# ==============================
# تنظیمات اصلی
# ==============================
BOT_TOKEN = "8146614293:AAHVlFdm1R1tqgtlAjGYLZ_5McMPa3lJwuU"
ADMIN_CHAT_ID = 6687139776
SUPPORT_USERNAME = 'samin_dh'
CHANNEL_USERNAME = 'bigkidkindergarten'
CARD_NUMBER = '6219861815202733'
CARD_OWNER = 'ثمین دهقانی'

registration_closed_esfahan = False

# ==============================
# کیبورد پشتیبانی
# ==============================
def support_back_channel(callback_data):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("بازگشت", callback_data=callback_data)],
        [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
    ])

# ==============================
# استارت
# ==============================
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

# ==============================
# هندلر دکمه‌ها
# ==============================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global registration_closed_esfahan
    query = update.callback_query
    await query.answer()

    # ----------------- انتخاب شهر -----------------
    if query.data == 'event_kindergarten':
        keyboard = [
            [InlineKeyboardButton("اصفهان", callback_data='session_esfahan')],
            [InlineKeyboardButton("تهران", callback_data='session_tehran')],
            [InlineKeyboardButton("پشتیبانی", callback_data='support')],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await query.edit_message_text("✨️ از ایونت کدوم شهرمون می‌خوای باخبر بشی؟", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'session_esfahan':
        context.user_data["city"] = "esfahan"
        context.user_data["ready_for_receipt"] = False
        message = (
            "🎪 مهدکودک‌بزرگترها اصفهان\n\n"
            "👫 مخاطب رویداد : بزرگسالان ۱۸ سال به بالا که دلشون یه کم بچگی می‌خواد\n"
            "📅 زمان: ۸ آبان ۱۴۰۴ ساعت ۱۸ الی ۲۱\n"
            "📍 مکان: استودیو یوگا پرانا (خیابان کارگر)\n"
            "☁️ هزینه: ۴۵۰ هزارتومان\n\n"
            "🔸 شرایط ثبت نام با تخفیف:\n"
            "به ازای هر دوستی که همراه با خودتون بیارید ۱۰٪ تخفیف همراهی از ما می‌گیرید.\n"
            "(نگران تنها اومدن هم نباشید؛ ما اینجا همه باهم دوست میشیم :)"
        )
        keyboard = [
            [InlineKeyboardButton("ارسال فیش ثبت‌نام", callback_data='start_receipt')],
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'start_receipt':
        if registration_closed_esfahan:
            await query.edit_message_text(
                "❌ ظرفیت ایونت اصفهان تموم شده 💔\nبرای اطلاع از رویدادهای بعدیمون با ما همراه باش🌱",
                reply_markup=support_back_channel('event_kindergarten')
            )
            return

        context.user_data["ready_for_receipt"] = True
        await query.edit_message_text(
            "📝 لطفا مبلغ ثبت‌نام رو واریز کن و فیش رو به همراه نام و شماره تماس ارسال کن 🌱\n\n"
            f"{CARD_NUMBER} به نام {CARD_OWNER}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("بازگشت", callback_data='session_esfahan')],
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ])
        )

    elif query.data == 'session_tehran':
        await query.edit_message_text(
            "✨️ رویداد تهران هنوز در حال برنامه‌ریزیه. به‌زودی از طریق کانال اطلاع‌رسانی میشه 🌱",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ])
        )

    elif query.data == 'support':
        await query.edit_message_text(
            f"اگه سوالی داشتی با آیدی @{SUPPORT_USERNAME} در تماس باش 💌",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ])
        )

    # ----------------- دکمه‌های ادمین -----------------
    elif query.data == 'close_registration_esfahan':
        registration_closed_esfahan = True
        await context.bot.send_message(ADMIN_CHAT_ID, "❌ ثبت‌نام برای رویداد اصفهان بسته شد.")
        await query.answer("ثبت‌نام بسته شد ✅")

    elif query.data == 'open_registration_esfahan':
        registration_closed_esfahan = False
        await context.bot.send_message(ADMIN_CHAT_ID, "✅ ثبت‌نام برای رویداد اصفهان دوباره باز شد.")
        await query.answer("ثبت‌نام باز شد ✅")

    elif query.data.startswith("confirm_"):
        user_id = int(query.data.split("_")[1])
        await context.bot.send_message(user_id, "✅ ثبت‌نامت تأیید شد! خوشحالیم که قراره باهامون باشی 🎉")
        await context.bot.send_message(ADMIN_CHAT_ID, f"✅ ثبت‌نام کاربر {user_id} تأیید شد.")
        await query.message.edit_reply_markup(reply_markup=None)

    elif query.data.startswith("reject_"):
        user_id = int(query.data.split("_")[2])
        reason = "اطلاعات ناقص" if "info" in query.data else "مبلغ اشتباه"
        await context.bot.send_message(
            user_id,
            f"❌ فیش شما رد شد به‌خاطر {reason}.\nلطفاً دوباره با اطلاعات کامل ارسال کن 🌱"
        )
        await context.bot.send_message(ADMIN_CHAT_ID, f"❌ فیش کاربر {user_id} رد شد ({reason}).")
        await query.message.edit_reply_markup(reply_markup=None)

# ==============================
# هندلر عکس فیش
# ==============================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if registration_closed_esfahan:
        await update.message.reply_text(
            "❌ ظرفیت ایونت اصفهان تموم شده 💔\nبرای اطلاع از رویدادهای بعدیمون با ما همراه باش🌱",
            reply_markup=support_back_channel('event_kindergarten')
        )
        return

    city = context.user_data.get("city")
    ready = context.user_data.get("ready_for_receipt", False)

    if city != "esfahan" or not ready:
        await update.message.reply_text(
            "❌ لطفاً اول شهر و مسیر ثبت‌نام رو انتخاب کن 🌱",
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
        [InlineKeyboardButton("❌ رد - اطلاعات ناقص", callback_data=f"reject_info_{user_id}")],
        [InlineKeyboardButton("❌ رد - مبلغ اشتباه", callback_data=f"reject_amount_{user_id}")]
    ])

    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo.file_id,
        caption=full_caption,
        reply_markup=confirm_buttons
    )

    await update.message.reply_text(
        "✅ فیشت دریافت شد! در حال بررسیه، کمی صبر کن 🌱",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("ورود به کانال", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ])
    )
    context.user_data["ready_for_receipt"] = False

# ==============================
# تنظیم دستور /start
# ==============================
async def set_bot_commands(app):
    commands = [BotCommand("start", "شروع ربات")]
    await app.bot.set_my_commands(commands)

# ==============================
# اجرای ربات
# ==============================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    async def after_start(app):
        await set_bot_commands(app)

    app.post_init = after_start

    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()
