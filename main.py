import os
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from engine import get_all_formats, run_download

# --- الإعدادات (تم تحديث الـ API لضمان التشغيل) ---
# هذه القيم رسمية وتعمل مع معظم البوتات
API_ID = 6 
API_HASH = "eb06d4ab35213ad159887517983e0493"
BOT_TOKEN = "8320774023:AAEFFNtk5A7r7utaBFclQXltq6VhSYSrNvo"
BOT_NAME = "@Downloader_Bot"

# إنشاء الكلاينت مع إجبار حذف الجلسة القديمة لتجنب التعليق
app = Client(
    "bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True # تشغيل الجلسة في الذاكرة لتجنب مشاكل الملفات في Railway
)

user_cache = {}

# --- دالة شريط التقدم ---
async def progress_bar(current, total, message, start_time):
    try:
        now = time.time()
        diff = now - start_time
        if round(diff % 4.0) == 0 or current == total:
            percentage = current * 100 / total
            speed = current / diff if diff > 0 else 0
            progress = f"🚀 **جاري الرفع...**\n📊 {percentage:.1f}% | ⚡ {speed / 1024 / 1024:.1f} MB/s"
            await message.edit(progress)
    except:
        pass

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(f"مرحباً! أرسل رابط الفيديو للتحميل 🎬")

@app.on_message(filters.regex(r'http'))
async def link_handler(client, message):
    url = message.text
    user_id = message.from_user.id
    user_cache[user_id] = url
    status_msg = await message.reply_text("🔎 **جاري استخراج الجودات...**")
    
    try:
        formats = await asyncio.to_thread(get_all_formats, url)
        if not formats:
            await status_msg.edit("❌ لم يتم العثور على جودات.")
            return

        buttons = [[InlineKeyboardButton(text, callback_query_data=f_id)] for text, f_id in formats.items()]
        await status_msg.edit("✅ اختر الجودة:", reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await status_msg.edit(f"❌ خطأ: {str(e)}")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id = callback_query.data
    user_id = callback_query.from_user.id
    url = user_cache.get(user_id)
    
    if not url:
        return await callback_query.answer("⚠️ أرسل الرابط مرة أخرى")

    status_msg = await callback_query.message.edit("⚙️ **جاري التحميل...**")
    ext = "m4a" if "audio" in f_id else "mp4"
    file_path = f"video_{user_id}.{ext}"

    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        
        if os.path.exists(file_path):
            await status_msg.edit("📤 **جاري الرفع...**")
            start_t = time.time()
            if "audio" in f_id:
                await client.send_audio(user_id, file_path, progress=progress_bar, progress_args=(status_msg, start_t))
            else:
                await client.send_video(user_id, file_path, supports_streaming=True, progress=progress_bar, progress_args=(status_msg, start_t))
            await status_msg.delete()
        else:
            await status_msg.edit("❌ فشل التحميل")
    except Exception as e:
        await status_msg.edit(f"❌ خطأ: {str(e)}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    print("✅ البوت انطلق...")
    app.run()
