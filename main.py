import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================
# BOT TOKEN
# =========================
TOKEN = "8062189638:AAEcn8Es8bscOklkRMtV3E9DwFmdLiEfL0Y"

# =========================
# LOGGING
# =========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# =========================
# TEMP DATABASE
# =========================
users = {}

# =========================
# CREATE USER
# =========================
def create_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "referrals": 0,
            "daily_bonus": False
        }

# =========================
# MAIN MENU
# =========================
def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("💰 Balance", callback_data="balance"),
            InlineKeyboardButton("🔗 Referral", callback_data="referral"),
        ],
        [
            InlineKeyboardButton("🎁 Daily Bonus", callback_data="bonus"),
            InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"),
        ],
        [
            InlineKeyboardButton("📖 How To Earn", callback_data="earn")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    create_user(user_id)

    # Referral System
    if context.args:
        try:
            referrer_id = int(context.args[0])

            if referrer_id != user_id and referrer_id in users:
                users[referrer_id]["balance"] += 5
                users[referrer_id]["referrals"] += 1

                await context.bot.send_message(
                    chat_id=referrer_id,
                    text=(
                        "🎉 New Referral Joined!\n\n"
                        "💰 ₹5 Added To Your Balance."
                    )
                )

        except Exception as e:
            logger.error(e)

    text = f"""
👋 Welcome {user.first_name}!

💸 Earn ₹5 per referral.

Use the buttons below to manage your account.
"""

    await update.message.reply_text(
        text=text,
        reply_markup=main_menu()
    )

# =========================
# BUTTON HANDLER
# =========================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    create_user(user_id)

    # BALANCE
    if query.data == "balance":
        balance = users[user_id]["balance"]
        refs = users[user_id]["referrals"]

        text = (
            f"💰 Your Balance: ₹{balance}\n"
            f"👥 Total Referrals: {refs}"
        )

        await query.message.reply_text(text)

    # REFERRAL
    elif query.data == "referral":
        bot_username = (await context.bot.get_me()).username

        ref_link = f"https://t.me/{bot_username}?start={user_id}"

        text = (
            "🔗 Your Referral Link:\n\n"
            f"{ref_link}\n\n"
            "💸 Earn ₹5 For Every Successful Referral."
        )

        await query.message.reply_text(text)

    # DAILY BONUS
    elif query.data == "bonus":
        if not users[user_id]["daily_bonus"]:
            users[user_id]["balance"] += 2
            users[user_id]["daily_bonus"] = True

            text = (
                "🎁 Daily Bonus Claimed!\n"
                "₹2 Added To Your Balance."
            )
        else:
            text = "❌ You Already Claimed Today's Bonus."

        await query.message.reply_text(text)

    # WITHDRAW
    elif query.data == "withdraw":
        balance = users[user_id]["balance"]

        if balance >= 50:
            users[user_id]["balance"] = 0

            text = (
                "✅ Withdrawal Request Submitted!\n\n"
                "💸 Your payment will be processed soon."
            )
        else:
            text = (
                "❌ Minimum Withdrawal Is ₹50.\n\n"
                f"Current Balance: ₹{balance}"
            )

        await query.message.reply_text(text)

    # HOW TO EARN
    elif query.data == "earn":
        text = (
            "📖 How To Earn Money:\n\n"
            "1️⃣ Share your referral link.\n"
            "2️⃣ Invite friends to join.\n"
            "3️⃣ Earn ₹5 per successful referral.\n"
            "4️⃣ Claim daily bonus.\n"
            "5️⃣ Withdraw after ₹50."
        )

        await query.message.reply_text(text)

# =========================
# NEW MEMBER JOIN
# =========================
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"👋 Welcome {member.first_name}!\n\n"
            "Press /start to begin earning money."
        )

# =========================
# ERROR HANDLER
# =========================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling update:", exc_info=context.error)

# =========================
# MAIN FUNCTION
# =========================
def main():
    app = Application.builder().token(TOKEN).build()

    # COMMANDS
    app.add_handler(CommandHandler("start", start))

    # BUTTONS
    app.add_handler(CallbackQueryHandler(buttons))

    # NEW MEMBERS
    from telegram.ext import MessageHandler, filters

    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member)
    )

    # ERRORS
    app.add_error_handler(error_handler)

    print("Bot is running...")

    # RUN BOT
    app.run_polling()

# =========================
# START BOT
# =========================
if __name__ == "__main__":
    main()