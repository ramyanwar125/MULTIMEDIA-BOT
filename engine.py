import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
# حاول استيراد المحرك، وإذا لم يوجد سنعرف السبب
try:
    from engine import get_all_formats, run_download
except ImportError:
    print("⚠️ ملف engine.py غير موجود في GitHub!")

app_web = Flask(__name__)
@app_web.route('/')
def home(): return "Bot Active"

def run_web():
    app_web.run(host="0.0.0.0", port=8080)

API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAEgqqEwFCxvs1_vKqhqwtOmq0svd2eB0Yc"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("🚀 البوت يعمل بكامل طاقته! أرسل رابطاً الآن.")

@app.on_message(filters.text & filters.private)
async def handle_msg(client, message):
    if "http" in message.text:
        status = await message.reply("⏳ جاري استخراج الجودات...")
        try:
            # استخدام asyncio لتشغيل وظيفة engine دون تجميد البوت
            formats = await asyncio.to_thread(get_all_formats, message.text)
            if not formats:
                await status.edit("❌ لم أتمكن من العثور على جودات.")
                return
            
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ اختر الجودة:", reply_markup=InlineKeyboardMarkup(btns))
        except NameError:
            await status.edit("❌ خطأ: ملف engine.py مفقود من السيرفر.")
        except Exception as e:
            await status.edit(f"❌ خطأ تقني: {str(e)[:50]}")

if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    app.run()
