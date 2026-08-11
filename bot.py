import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")


def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🎵 TikTok", callback_data="tiktok"),
            InlineKeyboardButton("📸 Instagram", callback_data="instagram"),
        ],
        [
            InlineKeyboardButton("▶️ YouTube", callback_data="youtube"),
            InlineKeyboardButton("📘 Facebook", callback_data="facebook"),
        ],
        [
            InlineKeyboardButton("✈️ Telegram", callback_data="telegram"),
        ],
        [
            InlineKeyboardButton("💰 Balance", callback_data="balance"),
            InlineKeyboardButton("🛒 My Orders", callback_data="orders"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    text = (
        f"👋 እንኳን ወደ Digital Gebeya በደህና መጡ, {user.first_name}!\n\n"
        "🚀 TikTok, Instagram, YouTube, Facebook እና Telegram "
        "SMM services በቀላሉ ይዘዙ።\n\n"
        "ከታች ካሉት አማራጮች ይምረጡ።"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "balance":
        await query.edit_message_text(
            "💰 Balance\n\n"
            "የአሁኑ ቀሪ ሂሳብ፦ 0 ETB\n\n"
            "Deposit ክፍሉ በቀጣይ እንጨምራለን።"
        )

    elif query.data == "orders":
        await query.edit_message_text(
            "🛒 My Orders\n\n"
            "እስካሁን ያዘዙት order የለም።"
        )

    elif query.data in {
        "tiktok",
        "instagram",
        "youtube",
        "facebook",
        "telegram",
    }:
        names = {
            "tiktok": "🎵 TikTok",
            "instagram": "📸 Instagram",
            "youtube": "▶️ YouTube",
            "facebook": "📘 Facebook",
            "telegram": "✈️ Telegram",
        }

        await query.edit_message_text(
            f"{names[query.data]}\n\n"
            "Service ለመምረጥ ይህን ክፍል በቀጣይ እንጨምራለን።"
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Digital Gebeya Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
