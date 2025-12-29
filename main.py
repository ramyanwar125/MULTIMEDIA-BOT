import os
import time
import asyncio
import sys
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from engine import get_all_formats, run_download

# --- الإعدادات ---
API_ID = "21453268" # يمكنك تغييرها إذا لزم الأمر
API_HASH = "805608c0282b9a7c640e0be034c44158"
BOT_TOKEN = "8320774023:AAEFFNtk5A7r7utaBFclQXltq6VhSYSrNvo"
BOT_NAME = "@Downloader_Bot"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# مخزن مؤقت لحفظ الروابط لكل مستخدم
user_cache = {}

# --- دوال المساعدة ---

async def progress_bar(current, total, message, start_time):
    """دالة تحديث شريط تقدم الرفع إلى تليجرام"""
    try:
        now = time.time()
        diff = now - start_time
        if round(diff % 4.0) == 0 or current == total:
            percentage = current * 100 / total
            speed = current / diff if diff > 0 else 0
            time_to_completion = round((total - current) / speed) if speed > 0 else 0
            
            progress_str = f"🚀 **جاري الرفع...**\n" \
                           f"📊 النسبة: {percentage:.1f}%\n" \
                           f"⚡ السرعة: {speed / 1024 / 1024:.1f} MB/s\n" \
                           f"⏳ المتبقي: {time_to_completion} ثانية"
            
            await message.edit(progress_str)
    except:
        pass

# --- الأوامر واستقبال الروابط ---

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(f"مرحباً بك في بوت {BOT_NAME} 🚀\n\nأرسل لي رابط فيديو من (YouTube, Facebook, Instagram, TikTok) وسأقوم بتحميله لك فوراً!")

@app.on_message(filters.regex(r'http'))
async def link_handler(client, message):
    url = message.text
    user_id = message.from_user.id
    user_cache[user_id] = url
    
    status_msg = await message.reply_text("🔎 **جاري فحص الرابط واستخراج الجودات...**")
    
    try:
        # استدعاء المحرك لاستخراج الجودات
        formats = await asyncio.to_thread(get_all_formats, url)
        
        if not formats:
            await status_msg.edit("❌ فشل استخراج البيانات. تأكد من أن الرابط صحيح وعام.")
            return

        buttons = []
        for text, f_id in formats.items():
            buttons.append([InlineKeyboardButton(text, callback_query_data=f_id)])

        reply_markup = InlineKeyboardMarkup(buttons)
        await status_msg.edit("✅ اختر الجودة المطلوبة للبدء:", reply_markup=reply_markup)
        
    except Exception as e:
        await status_msg.edit(f"❌ حدث خطأ: {str(e)}")

# --- معالجة الضغط على أزرار التحميل ---

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id = callback_query.data
    user_id = callback_query.from_user.id
    url = user_cache.get(user_id)

    if not url:
        await callback_query.answer("⚠️ انتهت الجلسة، أرسل الرابط مجدداً", show_alert=True)
        return

    status_msg = await callback_query.message.edit("⚙️ **جاري التحميل والمعالجة...**")
    
    # تحديد صيغة الملف ومساره
    is_audio = "audio" in f_id
    ext = "m4a" if is_audio else "mp4"
    file_path = f"media_{user_id}_{int(time.time())}.{ext}"

    try:
        # 1. تنفيذ التحميل (استدعاء engine.py)
        await asyncio.to_thread(run_download, url, f_id, file_path)
        
        # 2. التأكد من وجود الملف قبل الرفع
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            start_time = time.time()
            await status_msg.edit("📤 **اكتمل التحميل، جاري الرفع إلى تليجرام...**")
            
            if is_audio:
                await client.send_audio(
                    chat_id=user_id,
                    audio=file_path,
                    caption=f"🎵 {BOT_NAME}",
                    progress=progress_bar,
                    progress_args=(status_msg, start_time)
                )
            else:
                await client.send_video(
                    chat_id=user_id,
                    video=file_path,
                    caption=f"🎬 {BOT_NAME}",
                    supports_streaming=True,
                    progress=progress_bar,
                    progress_args=(status_msg, start_time)
                )
            
            await status_msg.delete()
        else:
            await status_msg.edit("❌ فشل التحميل: لم يتم إنشاء الملف بشكل صحيح.")

    except Exception as e:
        await status_msg.edit(f"❌ خطأ أثناء العملية: {str(e)}")
    
    finally:
        # 3. تنظيف المجلد من الملفات المؤقتة فوراً
        if os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass

# --- نظام التشغيل الآمن لمنع التكرار ---

if __name__ == "__main__":
    # تنظيف ملفات الجلسة والملفات العالقة عند البدء
    for f in os.listdir():
        if f.endswith(".session") or f.endswith(".session-journal") or ".part" in f:
            try: os.remove(f)
            except: pass

    print(f"🚀 {BOT_NAME} يعمل الآن...")
    app.run()
