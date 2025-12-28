import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from engine import get_all_formats, run_download

API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAFiFH3DMFZVI-njS3i-h50q4WmNwGpdpeg"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_cache = {}

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("أهلاً بك! أرسل لي رابطاً لتحميله.")

@app.on_message(filters.text & filters.private)
async def handle_message(client, message):
    url = message.text
    status = await message.reply("🔍 جاري معالجة الرابط...")
    try:
        formats = get_all_formats(url)
        user_cache[message.from_user.id] = url
        buttons = []
        for res, f_id in formats.items():
            buttons.append([InlineKeyboardButton(res, callback_data=f_id)])
        
        await status.edit("✅ اختر الجودة:", reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await status.edit(f"❌ فشل في استخراج الروابط.")

@app.on_callback_query()
async def callback(client, callback_query):
    format_id = callback_query.data
    user_id = callback_query.from_user.id
    url = user_cache.get(user_id)
    
    if not url:
        await callback_query.answer("خطأ: الرابط غير موجود.")
        return

    await callback_query.message.edit("⏳ جاري التحميل...")
    file_path = f"download_{user_id}.mp4"
    
    try:
        run_download(url, format_id, file_path)
        await client.send_video(user_id, video=file_path)
        await callback_query.message.delete()
    except Exception as e:
        await callback_query.message.edit(f"❌ حدث خطأ أثناء التحميل.")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

app.run()
