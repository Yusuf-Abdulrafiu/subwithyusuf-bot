import json
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load plans
with open("plans.json", "r") as f:
    plans_data = json.load(f)

# SmePlug Secret Key
SMEPLUG_SECRET_KEY = "fb9e22ecc3307b65e7502d6e73f8c2f90b156f0fdfb0caad53561c80e98b3057"

# States for conversation
NETWORK, PLAN_TYPE, DATA_PLAN, PHONE = range(4)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to SubwithYusuf!\nUse /buy_airtime or /buy_data to begin.")

# Buy data command
async def buy_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(net.upper(), callback_data=net)] for net in plans_data.keys()]
    await update.message.reply_text("📡 Select network:", reply_markup=InlineKeyboardMarkup(keyboard))
    return NETWORK

async def network_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["network"] = query.data

    keyboard = [[InlineKeyboardButton(ptype.upper(), callback_data=ptype)] for ptype in plans_data[query.data].keys()]
    await query.edit_message_text("📂 Select plan type:", reply_markup=InlineKeyboardMarkup(keyboard))
    return PLAN_TYPE

async def plan_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["plan_type"] = query.data

    plans = plans_data[context.user_data["network"]][query.data]
    keyboard = [
        [InlineKeyboardButton(f"{size} - ₦{price}", callback_data=size)] for size, price in plans.items()
    ]
    await query.edit_message_text("📦 Select data plan:", reply_markup=InlineKeyboardMarkup(keyboard))
    return DATA_PLAN

async def plan_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["plan"] = query.data
    await query.edit_message_text("📱 Enter phone number to receive data:")
    return PHONE

async def phone_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    context.user_data["phone"] = phone

    # Extract values
    network = context.user_data["network"]
    plan_type = context.user_data["plan_type"]
    plan = context.user_data["plan"]

    # Build request
    headers = {
        "Authorization": f"Bearer {SMEPLUG_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "network": network,
        "plan": plan,
        "phone": phone
    }

    # Send request to SmePlug
    try:
        response = requests.post("https://smeplug.ng/api/v1/data", headers=headers, json=payload)
        data = response.json()
        if data.get("success"):
            message = f"✅ {plan} successfully sent to {phone} on {network.upper()} ({plan_type.upper()})"
        else:
            message = f"❌ Failed to send data: {data.get('message', 'Unknown error')}"
    except Exception as e:
        message = f"🚨 Error contacting SmePlug: {str(e)}"

    await update.message.reply_text(message)
    return ConversationHandler.END

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END

# App
app = ApplicationBuilder().token(8162817648:AAHtL2CF1sQnvjpTzoU3lDAMFXD_ivmFtIE).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("buy_data", buy_data)],
    states={
        NETWORK: [CallbackQueryHandler(network_selected)],
        PLAN_TYPE: [CallbackQueryHandler(plan_type_selected)],
        DATA_PLAN: [CallbackQueryHandler(plan_selected)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_entered)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)

# Run
app.run_polling()
