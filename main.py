import json
import os
from flask import Flask, jsonify
import telebot

# توکن اختصاصی ربات شما
TOKEN = "8634629192:AAHevdhY4qo7inj1gS0jQiPoc-gfpPpZk68"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 48460135
SETTINGS_FILE = "settings.json"

# تنظیمات پیش‌فرض
DEFAULT_SETTINGS = {
    "base_rate": 720,
    "buy_fee": 10,
    "sell_fee": 10,
    "balance_toman": "7,000,000,000 تومان",
    "balance_dram": "10,000,000 درام"
}

def load_settings():
    """خواندن تنظیمات از فایل روی سرور"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("خطا در خواندن تنظیمات:", e)
    return DEFAULT_SETTINGS

def save_settings_to_file(settings):
    """ذخیره تنظیمات روی سرور"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print("خطا در ذخیره تنظیمات:", e)
        return False

# اپلیکیشن وب برای پاسخ‌گویی به مینی‌اپ
app = Flask(__name__)

@app.route('/get_settings', methods=['GET'])
def get_settings():
    """ارسال تنظیمات زنده به تمام گوشی‌ها و کاربران"""
    settings = load_settings()
    return jsonify(settings)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "سلام! به صرافی آنلاین ارمنستان خوش آمدید.\n"
        "جهت مشاهده نرخ‌های آنلاین و ثبت سفارش، از دکمه مینی‌اپ پایین استفاده کنید."
    )

@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get("action")
        
        # ۱. آپدیت سراسری تنظیمات از پنل مدیریت
        if action == "update_settings":
            new_settings = {
                "base_rate": float(data.get("base_rate", 720)),
                "buy_fee": float(data.get("buy_fee", 10)),
                "sell_fee": float(data.get("sell_fee", 10)),
                "balance_toman": str(data.get("balance_toman", "7,000,000,000 تومان")),
                "balance_dram": str(data.get("balance_dram", "10,000,000 درام"))
            }
            
            if save_settings_to_file(new_settings):
                response_text = (
                    "✅ **تنظیمات سراسری صرافی با موفقیت روی سرور ذخیره شد:**\n\n"
                    f"🔹 نرخ پایه: {new_settings['base_rate']} تومان\n"
                    f"🔹 کارمزد خرید از مشتری: {new_settings['buy_fee']}%\n"
                    f"🔹 کارمزد فروش به مشتری: {new_settings['sell_fee']}%\n"
                    f"🔹 موجودی تومان: {new_settings['balance_toman']}\n"
                    f"🔹 موجودی درام: {new_settings['balance_dram']}\n\n"
                    "📌 **این تغییرات برای همگی کاربران روی تمام گوشی‌ها هم‌اکنون اعمال گردید.**"
                )
            else:
                response_text = "❌ خطا در ذخیره‌سازی تنظیمات روی سرور."
                
            bot.send_message(message.chat.id, response_text, parse_mode="Markdown")
            
        # ۲. ثبت سفارش مشتری
        elif action == "submit_order":
            order_id = data.get("order_id")
            name = data.get("name")
            whatsapp = data.get("whatsapp")
            amount = data.get("amount")
            trade_type = data.get("trade_type")
            total_price = data.get("total_price")
            
            admin_msg = (
                f"📥 **سفارش جدید ثبت شد!**\n\n"
                f"🆔 **کد پیگیری:** `{order_id}`\n"
                f"👤 **نام مشتری:** {name}\n"
                f"📱 **واتس‌اپ:** {whatsapp}\n"
                f"🔄 **نوع معامله:** {trade_type}\n"
                f"💰 **مبلغ معامله:** {amount} درام\n"
                f"💵 **مبلغ کل:** {total_price}"
            )
            
            bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
            bot.send_message(
                message.chat.id,
                f"✅ سفارش شما با کد پیگیری `{order_id}` با موفقیت ثبت شد.\n"
                f"کارشناسان صرافی به زودی جهت هماهنگی با شما تماس خواهند گرفت.",
                parse_mode="Markdown"
            )

    except Exception as e:
        print("خطا در پردازش داده‌ها:", e)

if __name__ == "__main__":
    print("ربات صرافی آنلاین ارمنستان با موفقیت روشن شد...")
    bot.infinity_polling()
        
