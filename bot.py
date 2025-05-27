print("✅ Script started")

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, ConversationHandler,
    filters
)

print("✅ Libraries imported")

BOT_TOKEN = "8162817648:AAHtL2CF1sQnvjpTzoU3lDAMFXD_ivmFtIE"

# States for buy_airtime
PHONE, AMOUNT, NETWORK = range(3)

# States for buy_data
DATA_NETWORK, DATA_TYPE, DATA_PLAN, DATA_PHONE = range(3, 7)

# ------------------ /start ------------------ #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to SubwithYusuf!\nUse /buy_airtime or /buy_data to begin.")

# ------------------ /buy_airtime ------------------ #
async def buy_airtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📱 Enter phone number to recharge:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("💰 Enter amount (e.g. 100, 200):")
    return AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text
    keyboard = [["MTN", "Airtel", "Glo", "9mobile"]]
    await update.message.reply_text(
        "📶 Choose the network:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return NETWORK

async def get_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["network"] = update.message.text
    phone = context.user_data["phone"]
    amount = context.user_data["amount"]
    network = context.user_data["network"]
    await update.message.reply_text(
        f"✅ Recharge details:\n📱 Phone: {phone}\n💰 Amount: ₦{amount}\n📶 Network: {network}\n\n(This is a test preview)"
    )
    return ConversationHandler.END

# ------------------ /buy_data ------------------ #
async def buy_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["MTN", "Airtel"]]
    await update.message.reply_text(
        "📶 Select network for data purchase:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return DATA_NETWORK

async def get_data_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    network = update.message.text
    context.user_data["data_network"] = network

    if network == "MTN":
        keyboard = [["SME", "Data Share"]]
    elif network == "Airtel":
        keyboard = [["Direct Gifting", "Awoof Gifting"]]
    else:
        await update.message.reply_text("❌ This network is not yet supported.")
        return ConversationHandler.END

    await update.message.reply_text(
        f"📁 Choose plan type for {network}:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    return DATA_TYPE

async def get_data_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan_type = update.message.text
    context.user_data["data_type"] = plan_type
    plans = []

    if context.user_data["data_network"] == "MTN":
        if plan_type == "SME":
            await update.message.reply_text("🚫 MTN SME is currently unavailable.")
            return ConversationHandler.END
        elif plan_type == "Data Share":
            plans = ["5GB - ₦2500 (30 days)"]
    elif context.user_data["data_network"] == "Airtel":
        if plan_type == "Direct Gifting":
            plans = [
                "500MB - ₦600 (7 days)",
                "1GB - ₦600 (1 day)",
                "1.5GB - ₦1100 (7 days)",
                "2GB - ₦1600 (30 days)",
                "3GB - ₦2400 (30 days)",
                "4GB - ₦3000 (30 days)"
            ]
        elif plan_type == "Awoof Gifting":
            plans = [
                "150MB - ₦100 (1 day)",
                "10GB - ₦3500 (30 days)"
            ]
        else:
            await update.message.reply_text("❌ Invalid Airtel plan type.")
            return ConversationHandler.END

    await update.message.reply_text(
        "📦 Choose a data plan:",
        reply_markup=ReplyKeyboardMarkup([[p] for p in plans], one_time_keyboard=True)
    )
    return DATA_PLAN

async def get_data_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_plan = update.message.text
    context.user_data["data_plan"] = selected_plan
    await update.message.reply_text("📱 Enter recipient phone number:")
    return DATA_PHONE

async def get_data_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    context.user_data["data_phone"] = phone

    network = context.user_data["data_network"]
    plan_type = context.user_data["data_type"]
    plan = context.user_data["data_plan"]

    await update.message.reply_text(
        f"✅ You selected:\n📶 Network: {network}\n📁 Plan type: {plan_type}\n📦 Plan: {plan}\n📱 Phone: {phone}\n\n(This is a test preview)"
    )
    return ConversationHandler.END

# ------------------ cancel ------------------ #
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END

# ------------------ main ------------------ #
if __name__ == '__main__':
    print("✅ Starting bot setup...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))

    # Airtime
    airtime_handler = ConversationHandler(
        entry_points=[CommandHandler("buy_airtime", buy_airtime)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
            NETWORK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_network)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(airtime_handler)

    # Data
    data_handler = ConversationHandler(
        entry_points=[CommandHandler("buy_data", buy_data)],
        states={
            DATA_NETWORK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_data_network)],
            DATA_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_data_type)],
            DATA_PLAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_data_plan)],
            DATA_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_data_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(data_handler)

    print("✅ All handlers added")
    print("🚀 Bot is running...")
    app.run_polling()
