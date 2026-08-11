import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from config import BOT_TOKEN, ADMIN_ID
from database import init_db, add_user, get_balance


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


SERVICES = {
    "tiktok": {
        "name": "🎵 TikTok",
        "items": [
            ("Followers", 1000, 650),
            ("Followers", 2000, 1200),
            ("Followers", 3000, 1800),
            ("Followers", 5000, 3000),
            ("Followers", 10000, 6000),
        ],
    },
    "instagram": {
        "name": "📸 Instagram",
        "items": [
            ("Followers", 1000, 300),
            ("Followers", 2000, 600),
            ("Followers", 3000, 900),
            ("Followers", 5000, 1500),
            ("Followers", 10000, 3000),
        ],
    },
    "youtube": {
        "name": "▶️ YouTube",
        "items": [
            ("Subscribe", 1000, 4000),
            ("Subscribe", 2000, 8000),
            ("Subscribe", 3000, 12000),
            ("Subscribe", 5000, 20000),
            ("Subscribe", 10000, 40000),
        ],
    },
    "facebook": {
        "name": "📘 Facebook",
        "items": [
            ("Followers", 1000, 300),
            ("Followers", 2000, 600),
            ("Followers", 3000, 900),
            ("Followers", 5000, 1500),
            ("Followers", 10000, 3000),
        ],
    },
    "telegram": {
        "name": "✈️ Telegram",
        "items": [
            ("Members", 1000, 300),
            ("Members", 2000, 600),
            ("Members", 3000, 900),
        ],
    },
}


def home_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 TikTok", callback_data="platform:tiktok"),
            InlineKeyboardButton("📸 Instagram", callback_data="platform:instagram"),
        ],
        [
            InlineKeyboardButton("▶️ YouTube", callback_data="platform:youtube"),
            InlineKeyboardButton("📘 Facebook", callback_data="platform:facebook"),
        ],
        [
            InlineKeyboardButton("✈️ Telegram", callback_data="platform:telegram"),
        ],
        [
            InlineKeyboardButton("💰 Balance", callback_data="balance"),
            InlineKeyboardButton("📦 My Orders", callback_data="orders"),
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_user(
        user.id,
        user.username,
        user.first_name,
    )

    await update.message.reply_text(
        "👋 እንኳን ወደ **Digital Gebeya** በደህና መጡ!\n\n"
        "🚀 TikTok • Instagram • YouTube • Facebook • Telegram\n\n"
        "አገልግሎት ለመምረጥ ከታች ይምረጡ።",
        reply_markup=home_keyboard(),
        parse_mode="Markdown",
    )


async def show_platform(query, platform):
    service = SERVICES[platform]

    buttons = []

    for index, (name, quantity, price) in enumerate(service["items"]):
        buttons.append([
            InlineKeyboardButton(
                f"{name} {quantity:,} — {price:,} ETB",
                callback_data=f"package:{platform}:{index}",
            )
        ])

    buttons.append([
        InlineKeyboardButton("🏠 Home", callback_data="home")
    ])

    await query.edit_message_text(
        f"{service['name']}\n\n"
        "የሚፈልጉትን package ይምረጡ፦",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "home":
        await query.edit_message_text(
            "🏠 **Digital Gebeya**\n\n"
            "አገልግሎት ይምረጡ፦",
            reply_markup=home_keyboard(),
            parse_mode="Markdown",
        )
        return

    if data == "balance":
        balance = get_balance(query.from_user.id)

        await query.edit_message_text(
            f"💰 **Your Balance**\n\n"
            f"Balance: **{balance:,.2f} ETB**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Home", callback_data="home")]
            ]),
            parse_mode="Markdown",
        )
        return

    if data == "orders":
        await query.edit_message_text(
            "📦 **My Orders**\n\n"
            "የOrders history ክፍል በቀጣይ እንጨምራለን።",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Home", callback_data="home")]
            ]),
            parse_mode="Markdown",
        )
        return

    if data.startswith("platform:"):
        platform = data.split(":", 1)[1]
        await show_platform(query, platform)
        return

    if data.startswith("package:"):
        _, platform, index = data.split(":")
        index = int(index)

        service = SERVICES[platform]
        name, quantity, price = service["items"][index]

        context.user_data["pending_order"] = {
            "platform": platform,
            "service": name,
            "quantity": quantity,
            "price": price,
        }

        await query.edit_message_text(
            f"✅ **Package selected**\n\n"
            f"Platform: {service['name']}\n"
            f"Service: {name}\n"
            f"Quantity: {quantity:,}\n"
            f"Price: {price:,} ETB\n\n"
            "🔗 አሁን የVideo/Post/Profile link ይላኩ።",
            parse_mode="Markdown",
        )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "pending_order" not in context.user_data:
        await update.message.reply_text(
            "🏠 /start በመጫን ወደ Home ይመለሱ።"
        )
        return

    link = update.message.text.strip()
    order = context.user_data["pending_order"]

    context.user_data["pending_order"]["link"] = link

    await update.message.reply_text(
        "✅ Link received!\n\n"
        f"Platform: {SERVICES[order['platform']]['name']}\n"
        f"Service: {order['service']}\n"
        f"Quantity: {order['quantity']:,}\n"
        f"Price: {order['price']:,} ETB\n\n"
        "⚠️ Order confirmation/API connection በቀጣይ ይጨመራል።"
    )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(
        __import__("telegram.ext", fromlist=["MessageHandler"])
        .MessageHandler(
            __import__("telegram.ext", fromlist=["filters"]).filters.TEXT
            & ~__import__("telegram.ext", fromlist=["filters"]).filters.COMMAND,
            text_handler,
        )
    )

    print("🚀 Digital Gebeya Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
