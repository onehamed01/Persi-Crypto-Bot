import json
import sqlite3

import requests
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      Update)
from telegram.ext import CallbackQueryHandler, CommandHandler, Updater

# Cache for the base price
base_price = None

def live_price():
    global base_price
    if base_price is None:
        # Fetch the base price from the database and cache it
        with sqlite3.connect('crondata.db') as database:
            cursor_database = database.cursor()
            cursor_database.execute('SELECT * FROM data_table')
            rows = cursor_database.fetchall()
            base_price = rows[0][0]

    # Reuse the same request instead of making a second one
    response = requests.get('https://api.nobitex.ir/v2/orderbook/USDTIRT')
    data = json.loads(response.content)
    usdtirt_price = data['lastTradePrice'][0:-1]
    usdtirt_price = usdtirt_price[:-3] + "," + usdtirt_price[-3:]
    
    return usdtirt_price

def check_status():
    new_price = live_price().replace(",", "")
    calculate = ((int(new_price) - int(base_price)) / int(base_price)) * 100
    calculate = "{:.2f}".format(calculate)

    return calculate 

def start_message(update, context):
    user = update.message.from_user
    options_text = f"سلام {user.first_name} عزیز. توضیحاتی درباره ی کلیدهای زیر بهت داده میشه.\n\n" \
                   "🍂 <b>قیمت</b>: قیمت لحظه ای به شما نمایش داده میشه و توجه داشته باشین که کاهش و افزایش ارز نسبت به 24 ساعت گذشته هست.\n\n" \
                   "🍂 <b>ماشین حساب</b>: میتونید مقدار تتر به تومان و بلعکس را محاسبه کنید.\n\n" \
                   "🍂 <b>تماس با من</b>: انتقاد و  پیشنهادتونو حتما برای بنده بفرستید. با تشکر 🫀\n\n" \
                   "🫀 <b>@onehamed</b>"
    buttons = [
        [InlineKeyboardButton("💸 قیمت", callback_data="money_button")],
        [InlineKeyboardButton("🔄 ماشین حساب", callback_data="calculator_button")],
        [InlineKeyboardButton("✉️ تماس با من", callback_data="contact_button")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    context.bot.send_message(chat_id=update.effective_chat.id, text=options_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

def queries_button(update, context):
    query = update.callback_query
    if query.data == "money_button":
        if "-" in list(str(check_status())):
            level = "ریزش"
            icon = "🔴"
        else:
            level = "افزایش"
            icon = "🟢"

        message = f"💵 <b>{live_price()} تومان</b>\n{icon} <b>%{check_status().replace('-', '')} {level}</b>"
        query.message.reply_text(message, parse_mode=ParseMode.HTML)

def main():
    updater = Updater(token="6172072666:AAGVaxLTgSwljElchqXoaOETvRLqDDxzm9U", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CallbackQueryHandler(queries_button))
    dp.add_handler(CommandHandler('start', start_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
