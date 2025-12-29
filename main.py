import os
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
from engine import get_all_formats, run_download

# --- خادم الويب ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is Online"

def run_web():
    web_app.run(host="0.0.0.0", port=8080)

# --- إعدادات البوت ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAEgqqEwFCxvs1_vKqhqwtOmq0svd2eB0Yc"

app = Client("final_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# تخزين مؤقت للروابط
url_cache = {}

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("🚀 أرسل رابط الفيديو الآن!")

@app.on_message(filters.text & filters.private)
async def handle_link(client, message):
    if "http" in message.text:
        status = await message.reply("🔍 جاري فحص الرابط...")
        formats = await asyncio.to_thread(get_all_formats, message.text)
        if formats:
            url_cache[message.from_user.id] = message.text # حفظ الرابط
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ اختر الجودة للتحميل:", reply_markup=InlineKeyboardMarkup(btns))
        else:
            await status.edit("❌ فشل استخراج الجودات.")

# --- الجزء المفقود: معالجة الضغط على زر الجودة ---
@app.on_callback_query()
async def download_logic(client, callback_query):
    user_id = callback_query.from_user.id
    format_id = callback_query.data
    url = url_cache.get(user_id)

    if not url:
        await callback_query.answer("⚠️ انتهت الجلسة، أرسل الرابط مجدداً", show_alert=True)
        return

    await callback_query.message.edit("⚙️ جاري التحميل من السيرفر... يرجى الانتظار")
    
    file_path = f"video_{user_id}.mp4"
    try:
        # تحميل الفيديو إلى سيرفر الاستضافة
        await asyncio.to_thread(run_download, url, format_id, file_path)
        
        # إرسال الفيديو للمستخدم
        await callback_query.message.edit("📤 جاري رفع الفيديو إلى تليجرام...")
        await client.send_video(chat_id=user_id, video=file_path, caption="✅ تم التحميل بنجاح!")
        await callback_query.message.delete()
        
    except Exception as e:
        await callback_query.message.edit(f"❌ خطأ في التحميل: {str(e)[:100]}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path) # حذف الفيديو من السيرفر لتوفير المساحة

if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    app.run()
