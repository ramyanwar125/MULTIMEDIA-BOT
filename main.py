import os, asyncio, time, re
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- Config | الإعدادات ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8254937829:AAH1MvppZabP7RCHrrzPSIy5-taWUYWmz8Y"
ADMIN_ID = 7349033289 
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia" 
USERS_FILE = "users_database.txt" 
MAX_SIZE_MB = 450  # حد التحميل

# --- سيرفر وهمي لريندر ---
def run_health_check_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is Running")
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

# --- قسم المحرك (بدون تكرار) ---
def prepare_engine():
    cookie_file = "cookies_stable.txt"
    if not os.path.exists(cookie_file):
        with open(cookie_file, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1766757959\tGPS\t1\n")
    return cookie_file

def get_video_data(url):
    ydl_opts = {
        'quiet': True, 
        'cookiefile': prepare_engine(), 
        'nocheckcertificate': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

# --- قسم البوت ---
app = Client("SkyNet_Media_v25", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_cache = {}

async def progress_bar(current, total, status_msg, start_time):
    now = time.time()
    diff = now - start_time
    if diff < 3.0: return
    percentage = (current * 100) / total
    speed = current / diff
    bar = "▬" * int(percentage // 10) + "▭" * (10 - int(percentage // 10))
    tmp = (
        f"🚀 **Transferring.. جاري النقل**\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"◈ **Progress:** `{bar}` **{percentage:.1f}%**\n"
        f"◈ **Speed:** `{speed/(1024*1024):.2f} MB/s` ⚡️\n\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    try: await status_msg.edit(tmp)
    except: pass

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not os.path.exists(USERS_FILE): open(USERS_FILE, "w").close()
    users = open(USERS_FILE).read().splitlines()
    if str(message.from_user.id) not in users:
        with open(USERS_FILE, "a") as f: f.write(f"{message.from_user.id}\n")
    
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID: kb.append(['📣 Broadcast | إذاعة'])
    
    welcome_text = (
        f"✨━━━━━━━━━━━━━✨\n"
        f"  🙋‍♂️ Welcome | أهلاً بك يا **{message.from_user.first_name}**\n"
        f"  🌟 In **{BOT_NAME}** World\n"
        f"✨━━━━━━━━━━━━━✨\n\n"
        f"🚀 **Fast Downloader for | بوت تحميل سريع:**\n"
        f"📹 YouTube | 📸 Instagram | 🎵 TikTok\n"
        f"👇 **Send link now! | أرسل الرابط الآن!**"
    )
    await message.reply(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    text, user_id = message.text, message.from_user.id
    
    if text == '👨‍💻 Developer | المطور':
        msg = f"👑 **Main Developer:** {DEV_USER}\n📢 **Our Channel:** @{CHANNEL_USER}"
        await message.reply(msg)
        return

    if "http" in text:
        status = await message.reply("🔍 **Analyzing.. جاري المعالجة** ⏳")
        try:
            info = await asyncio.to_thread(get_video_data, text)
            user_cache[user_id] = {"url": text, "info": info}
            btns = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('height'):
                    btns.append([InlineKeyboardButton(f"🎬 {f['height']}p", callback_data=f['format_id'])])
            btns.append([InlineKeyboardButton("🎶 Audio | تحميل صوت", callback_data="bestaudio")])
            await status.edit("✅ **Formats Found | تم الاستخراج**\nChoose your option: 👇", reply_markup=InlineKeyboardMarkup(btns))
        except: await status.edit("❌ **Error | فشل المعالجة**")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    data = user_cache.get(user_id)
    if not data: return

    # فحص الحجم
    size_bytes = 0
    for f in data["info"].get('formats', []):
        if f.get('format_id') == f_id:
            size_bytes = f.get('filesize') or f.get('filesize_approx') or 0
    
    if (size_bytes / (1024*1024)) > MAX_SIZE_MB:
        await callback_query.message.edit(f"❌ **File too large | الحجم كبير**\nMax: {MAX_SIZE_MB}MB")
        return

    status_msg = await callback_query.message.edit("⚙️ **Processing.. جاري التنفيذ**")
    file_path = f"media_{user_id}.mp4"
    
    try:
        ydl_opts = {'outtmpl': file_path, 'format': f_id, 'cookiefile': 'cookies_stable.txt', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [data["url"]])
        
        st = time.time()
        await client.send_video(user_id, file_path, caption=f"🎬 **By {BOT_NAME}**", progress=progress_bar, progress_args=(status_msg, st))
        
        thanks_text = (
            f"✨ **Mission Completed | تمت المهمة** ✨\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🤖 **Bot:** {BOT_NAME}\n"
            f"👨‍💻 **Dev:** {DEV_USER}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        await client.send_message(user_id, thanks_text)
        await status_msg.delete()
    except Exception as e: await status_msg.edit(f"❌ **Failed:** {e}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    threading.Thread(target=run_health_check_server, daemon=True).start()
    app.run()
