import os
import asyncio
import time
import yt_dlp
import pyrogram
from pyrogram import Client, filters, idle
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait

# --- 1. ENGINE SECTION (المحرك المطور) ---

def prepare_engine():
    cookie_file = "cookies_stable.txt"
    if not os.path.exists(cookie_file):
        with open(cookie_file, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
    return cookie_file

def get_all_formats(url):
    ydl_opts = {
        'quiet': True, 
        'cookiefile': prepare_engine(), 
        'nocheckcertificate': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {}
        formats_btns["🎬 Best Quality | أفضل جودة"] = "bestvideo+bestaudio/best"
        
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                res = f.get('height')
                if res: formats_btns[f"🎬 {res}p (MP4)"] = f.get('format_id')
        
        formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
        return formats_btns

def run_download(url, format_id, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': 'cookies_stable.txt',
        'nocheckcertificate': True,
        'quiet': True,
        'merge_output_format': 'mp4', 
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# --- 2. BOT SECTION ---

API_ID = int(os.environ.get("API_ID", 33536164))
API_HASH = os.environ.get("API_HASH", "c4f81cfa1dc011bcf66c6a4a58560fd2")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8320774023:AAHtxSIqRsXQR3GGitkpkWjquH3t-fOk2MQ")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 7349033289))

# تم تغيير اسم الجلسة لتجنب مشاكل الاتصال العالقة
app = Client("fast_media_fixed_v1", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_cache = {}
USERS_FILE = "users_database.txt"
CHANNEL_USER = "Fast_Mediia"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
DEV_USER = "@TOP_1UP"

def add_user(user_id):
    if not os.path.exists(USERS_FILE): open(USERS_FILE, "w").close()
    users = open(USERS_FILE, "r").read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f: f.write(f"{user_id}\n")

async def check_subscription(client, message):
    try:
        await client.get_chat_member(CHANNEL_USER, message.from_user.id)
        return True
    except UserNotParticipant:
        await message.reply(f"⚠️ اشترك في القناة أولاً: @{CHANNEL_USER}", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ اشترك الآن", url=f"https://t.me/{CHANNEL_USER}")]]))
        return False
    except: return True

async def progress_bar(current, total, status_msg, start_time):
    now = time.time()
    if now - start_time < 2.5: return
    percentage = current * 100 / total
    bar = "▬" * int(percentage // 10) + "▭" * (10 - int(percentage // 10))
    try: await status_msg.edit(f"🚀 جاري النقل: {percentage:.1f}%\n`{bar}`")
    except: pass

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await check_subscription(client, message): return
    add_user(message.from_user.id)
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID: kb[1].append('📣 Broadcast | إذاعة')
    await message.reply(f"🙋‍♂️ أهلاً بك في {BOT_NAME}\nأرسل الرابط الآن!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    if not await check_subscription(client, message): return
    text, user_id = message.text, message.from_user.id
    if "http" in text:
        status = await message.reply("🔍 جاري التحليل..")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ اختر الجودة المطلوبة:", reply_markup=InlineKeyboardMarkup(btns))
        except Exception as e: await status.edit(f"❌ خطأ: {str(e)[:50]}")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    if not url: return
    await callback_query.message.edit("⚙️ جاري التحميل والدمج...")
    file_path = f"media_{user_id}.{'m4a' if 'audio' in f_id else 'mp4'}"
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        st = time.time()
        if "audio" in f_id:
            await client.send_audio(user_id, file_path, progress=progress_bar, progress_args=(callback_query.message, st))
        else:
            await client.send_video(user_id, file_path, progress=progress_bar, progress_args=(callback_query.message, st))
        await callback_query.message.delete()
    except Exception as e: await callback_query.message.edit(f"❌ خطأ: {str(e)[:100]}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

# --- 3. THE FINAL FIX: معالجة الحظر والبدء النظيف ---
async def main():
    try:
        await app.start()
        # تصحيح دالة الـ Webhook لمسح التكرار
        try:
            await app.set_webhook(drop_pending_updates=True)
            await app.stop_webhook()
        except:
            pass
        print("✅ البوت يعمل الآن بنسخة واحدة فقط...")
        await idle()
        await app.stop()
    except FloodWait as e:
        print(f"⚠️ حظر من تليجرام! سننتظر {e.value} ثانية...")
        await asyncio.sleep(e.value)
        await main()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
