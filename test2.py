]
            await query.edit_message_text("مهدکودک‌بزرگترها شیراز ✨", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(CLOSED_EVENT_MESSAGE, reply_markup=support_back_channel('event_kindergarten'))

    # شروع ثبت‌نام
    elif query.data == 'start_receipt_tehran':
        context.user_data["ready_for_receipt"] = "tehran"
        await query.edit_message_text(
            TEHRAN_RECEIPT_MESSAGE,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]
            ])
        )

    elif query.data == 'start_receipt_esfahan':
        context.user_data["ready_for_receipt"] = "esfahan"
        await query.edit_message_text(
            ESFAHAN_RECEIPT_MESSAGE,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]
            ])
        )

    # کنترل باز/بسته شدن شهرها
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

    # ------------------------- تأیید / رد فیش‌ها -------------------------
    elif query.data.startswith("confirm_"):
        _, user_id, city_name = query.data.split("_")
        user_id = int(user_id)

        confirmation_text = (
            "پرداخت شما تأیید شد 🌱\n"
            "ثبت‌نامتون در رویداد مهدکودک‌بزرگترهای پنجشنبه کامل شد.\n\n"
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
        reason_text = "اطلاعات ناقص" if "reject_info_" in query.data else "مبلغ اشتباه"

        await context.bot.send_message(
            chat_id=user_id,
            text=f"❌ ثبت‌نام شما رد شد ({reason_text}). لطفاً فیش رو دوباره ارسال کنید و نام و شماره تماس رو بنویسید 🌱",
            reply_markup=support_back_channel('event_kindergarten')
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
        [InlineKeyboardButton("✅ تأیید ثبت‌نام", callback_data=f"confirm_{user_id}_{city}")],
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