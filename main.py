import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# --- الجزء الخاص بخادم الويب (لتجنب رسائل الخطأ في الاستضافة) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "<h1>Bot is Alive!</h1>"

def run_web():
    web_app.run(host="0.0.0.0", port=8080)

# --- إعدادات البوت ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAEgqqEwFCxvs1_vKqhqwtOmq0svd2eB0Yc"

app = Client("my_production_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("✅ **تم تشغيل البوت بنجاح!**\nأرسل لي أي رابط فيديو (يوتيوب، تيك توك، انستقرام) وسأعطيك خيارات التحميل.")

@app.on_message(filters.text & filters.private)
async def handle_link(client, message):
    if "http" in message.text:
        # ملاحظة: إذا لم ترفع ملف engine.py سيتوقف البوت هنا
        try:
            from engine import get_all_formats
            status = await message.reply("🔍 جاري فحص الرابط...")
            formats = await asyncio.to_thread(get_all_formats, message.text)
            
            if not formats:
                await status.edit("❌ لم أجد جودات متاحة.")
                return
                
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ اختر الجودة:", reply_markup=InlineKeyboardMarkup(btns))
        except ImportError:
            await message.reply("⚠️ خطأ: ملف `engine.py` مفقود من حساب GitHub الخاص بك!")
        except Exception as e:
            await message.reply(f"❌ حدث خطأ: {str(e)[:50]}")

if __name__ == "__main__":
    # تشغيل الويب في الخلفية
    Thread(target=run_web, daemon=True).start()
    # تشغيل البوت
    print("🚀 البوت بدأ العمل...")
    app.run()
