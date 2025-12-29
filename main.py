import os
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from engine import get_all_formats, run_download

# --- البيانات التي أرسلتها أنت ---
API_ID = 24652261 
API_HASH = "805608c0282b9a7c640e0be034c44158"
BOT_TOKEN = "8320774023:AAEFFNtk5A7r7utaBFclQXltq6VhSYSrNvo"

# --- تنظيف إجباري للجلسات القديمة لحل خطأ الـ API ---
for file in os.listdir():
    if file.endswith(".session") or file.endswith(".session-journal"):
        try:
            os.remove(file)
        except:
            pass

# إنشاء الكلاينت بنظام الجلسة المؤقتة
app = Client(
    "final_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True # هذا يحل مشكلة الـ Bad Request نهائياً
)

user_cache = {}

async def progress_bar(current, total, message, start_time):
    try:
        now = time.time()
        diff = now - start_time
        if round(diff % 4.0) == 0 or current == total:
            percentage = current * 100 / total
            speed = current / diff if diff > 0 else 0
            await message.edit(f"🚀 **جاري الرفع...**\n📊 {percentage:.1f}% | ⚡ {speed / 1024 / 1024:.1f} MB/s")
    except: pass

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 أهلاً بك! أرسل رابط الفيديو للتحميل.")

@app.on_message(filters.regex(r'http'))
async def link_handler(client, message):
    url = message.text
    user_id = message.from_user.id
    user_cache[user_id] = url
    status = await message.reply_text("🔎 جاري فحص الرابط...")
    
    try:
        formats = await asyncio.to_thread(get_all_formats, url)
        if not formats:
            return await status.edit("❌ لم أجد جودات متاحة.")
        
        buttons = [[InlineKeyboardButton(text, callback_query_data=f_id)] for text, f_id in formats.items()]
        await status.edit("✅ اختر الجودة:", reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await status.edit(f"❌ خطأ: {e}")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id = callback_query.data
    user_id = callback_query.from_user.id
    url = user_cache.get(user_id)
    if not url: return
    
    status = await callback_query.message.edit("⚙️ جاري التحميل...")
    ext = "m4a" if "audio" in f_id else "mp4"
    file_path = f"file_{user_id}_{int(time.time())}.{ext}"

    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        if os.path.exists(file_path):
            await status.edit("📤 جاري الرفع...")
            start_t = time.time()
            if "audio" in f_id:
                await client.send_audio(user_id, file_path, progress=progress_bar, progress_args=(status, start_t))
            else:
                await client.send_video(user_id, file_path, supports_streaming=True, progress=progress_bar, progress_args=(status, start_t))
            await status.delete()
        else:
            await status.edit("❌ فشل تحميل الملف.")
    except Exception as e:
        await status.edit(f"❌ خطأ: {e}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    print("🚀 البوت انطلق بالقيم الجديدة!")
    app.run()
