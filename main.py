import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# تنظیمات اصلی ربات
BOT_TOKEN = "8634629192:AAHevdhY4qo7inj1gS0jQiPoc-gfpPpZk68"
ADMIN_ID = 48460135

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! به صرافی آنلاین ارمنستان خوش آمدید. 🇦🇲\n\n"
        "برای ثبت سفارش، استعلام نرخ و خرید و فروش درام، روی دکمه «صرافی آنلاین 🇦🇲» در پایین صفحه کلیک کنید."
    )
    await update.message.reply_text(welcome_text)

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.message.web_app_data.data)
    user = update.message.from_user
    
    if data.get("action") == "submit_order":
        name = data.get("name")
        whatsapp = data.get("whatsapp")
        amount = data.get("amount")
        trade_type = "خرید درام" if data.get("trade_type") == "buy" else "فروش درام"
        total_price = data.get("total_price")
        
        msg_for_admin = (
            f"📥 **سفارش جدید دریافت شد!**\n\n"
            f"👤 **نام مشتری:** {name}\n"
            f"📱 **واتس‌اپ:** `{whatsapp}`\n"
            f"🔄 **نوع معامله:** {trade_type}\n"
            f"💰 **مبلغ (درام):** {amount}\n"
            f"💵 **مبلغ کل (تومان):** {total_price}\n"
            f"🆔 **آیدی تلگرام:** `{user.id}`\n"
            f"👤 **یوزرنیم:** @{user.username if user.username else 'ندارد'}"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ تایید سفارش", callback_data=f"app_{user.id}_{amount}"),
                InlineKeyboardButton("❌ رد سفارش", callback_data=f"rej_{user.id}")
            ]
        ]
        
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg_for_admin, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.reply_text("✅ سفارش شما با موفقیت ثبت شد و پس از بررسی توسط مدیریت صرافی، تایید خواهد شد.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("_")
    action = data[0]
    user_id = int(data[1])
    
    if action == "app":
        try:
            await context.bot.send_message(chat_id=user_id, text="🎉 سفارش شما توسط مدیریت صرافی تایید شد.")
        except Exception:
            pass
        await query.edit_message_text(text=f"{query.message.text}\n\n✅ **این سفارش توسط شما تایید شد.**")
        
    elif action == "rej":
        try:
            await context.bot.send_message(chat_id=user_id, text="❌ متاسفانه سفارش شما رد شد. جهت پیگیری با پشتیبانی تماس بگیرید.")
        except Exception:
            pass
        await query.edit_message_text(text=f"{query.message.text}\n\n❌ **این سفارش رد شد.**")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("ربات آماده اجرا است...")
    app.run_polling()

if __name__ == "__main__":
    main()
