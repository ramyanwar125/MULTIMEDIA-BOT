import os
import asyncio
import time
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# --- 1. ENGINE SECTION (المحرك المطور لحل مشكلة الصوت والفيديو) ---

def prepare_engine():
    cookie_file = "cookies_stable.txt"
    if not os.path.exists(cookie_file):
        with open(cookie_file, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1766757959\tGPS\t1\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1801316163\tPREF\ttz=Africa.Cairo&f7=100\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1800424038\tSOCS\tCAISEwgDEgk4NDYxMjU0NDcaAmVuIAEaBgiA8ZzKBg\n")
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
        
        # خيار يحل مشكلة فيسبوك ويوتيوب عبر دمج أفضل فيديو مع أفضل صوت تلقائياً
        formats_btns["🎬 Best Quality | أفضل جودة"] = "bestvideo+bestaudio/best"
        
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                res = f.get('height')
                if res: 
                    formats_btns[f"🎬 {res}p (MP4)"] = f.get('format_id')
        
        formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
        return formats_btns

def run_download(url, format_id, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': 'cookies_stable.txt',
        'nocheckcertificate': True,
        'quiet': True,
        'merge_output_format': 'mp4', # لضمان دمج الصوت والفيديو في ملف واحد
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# --- 2. BOT SECTION (الإعدادات مع التوكن الجديد) ---

API_ID = int(os.environ.get("API_ID", 33536164))
API_HASH = os.environ.get("API_HASH", "c4f81cfa1dc011bcf66c6a4a58560fd2")
# تم وضع التوكن الجديد هنا كما طلبت
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8320774023:AAGcW3Q5KZyN43jY_rbdlePflfxf0Xv8q00")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 7349033289))
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia" 
USERS_FILE = "users_database.txt" 

app = Client("fast_media_v19", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_cache = {}

def add_user(user_id):
    if not os.path.exists(USERS_FILE): open(USERS_FILE, "w").close()
    users = open(USERS_FILE, "r").read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f: f.write(f"{user_id}\n")

def get_users_count():
    if not os.path.exists(USERS_FILE): return 0
    return len(open(USERS_FILE, "r").read().splitlines())

async def check_subscription(client, message):
    try:
        await client.get_chat_member(CHANNEL_USER, message.from_user.id)
        return True
    except UserNotParticipant:
        await message.reply(
            f"⚠️ **عذراً، يجب عليك الاشتراك في القناة أولاً!**\n\n"
            f"قناة البوت: @{CHANNEL_USER}\n"
            f"بعد الاشتراك، أرسل /start مجدداً.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Join Channel | اشترك الآن", url=f"https://t.me/{CHANNEL_USER}")
            ]])
        )
        return False
    except Exception: return True

async def progress_bar(current, total, status_msg, start_time):
    now = time.time()
    diff = now - start_time
    if diff < 2.5: return
    percentage = current * 100 / total
    speed = current / diff
    bar = "▬" * int(percentage // 10) + "▭" * (10 - int(percentage // 10))
    tmp = (
        f"🚀 **Transferring.. جاري النقل**\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"◈ **Progress:** `{bar}` **{percentage:.1f}%**\n"
        f"◈ **Speed:** `{speed/(1024*1024):.2f} MB/s` ⚡️\n"
        f"◈ **Size:** `{current/(1024*1024):.1f}` / `{total/(1024*1024):.1f} MB`\n\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    try: await status_msg.edit(tmp)
    except: pass

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await check_subscription(client, message): return
    add_user(message.from_user.id)
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID: kb[1].append('📣 Broadcast | إذاعة')
    
    welcome_text = (
        f"✨━━━━━━━━━━━━━✨\n"
        f"  🙋‍♂️ Welcome | أهلاً بك يا **{message.from_user.first_name}**\n"
        f"  🌟 In **{BOT_NAME}** World\n"
        f"✨━━━━━━━━━━━━━✨\n\n"
        f"🚀 **Fast Downloader for:**\n"
        f"📹 YouTube | 📸 Instagram | 🎵 TikTok\n"
        f"👻 Snapchat | 🔵 Facebook\n\n"
        f"👇 **Send link now! | أرسل الرابط الآن!**"
    )
    await message.reply(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    if not await check_subscription(client, message): return
    text, user_id = message.text, message.from_user.id
    
    if text == '🔄 Restart Service | بدء الخدمة':
        await message.reply("📡 **System Ready..** ⚡️")
        return
    
    if text == '👨‍💻 Developer | المطور':
        msg = f"👑 **Main Developer:** {DEV_USER}\n📢 **Our Channel:** @{CHANNEL_USER}\n"
        if user_id == ADMIN_ID: msg += f"📊 **Total Users:** `{get_users_count()}`"
        await message.reply(msg)
        return

    if text == '📣 Broadcast | إذاعة' and user_id == ADMIN_ID:
        await message.reply("📥 **Send your message:**")
        user_cache[f"bc_{user_id}"] = True
        return

    if user_cache.get(f"bc_{user_id}"):
        users = open(USERS_FILE).read().splitlines()
        for u in users:
            try: await message.copy(int(u))
            except: pass
        await message.reply("✅ **Broadcast Sent**")
        user_cache[f"bc_{user_id}"] = False
        return

    if "http" in text:
        status = await message.reply("🔍 **Analyzing..** ⏳")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ **Formats Found**\nChoose your option: 👇", reply_markup=InlineKeyboardMarkup(btns))
        except Exception as e: 
            await status.edit(f"❌ **Error:** {str(e)[:50]}")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    if not url: return
    
    await callback_query.message.edit("⚙️ **Processing...**\n📡 **Status:** `Direct Connection` ⚡️")
    is_audio = "audio" in f_id
    file_path = f"media_{user_id}.{'m4a' if is_audio else 'mp4'}"
    
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        if os.path.exists(file_path):
            st = time.time()
            if is_audio: 
                await client.send_audio(user_id, file_path, caption=f"🎵 **By {BOT_NAME}**", progress=progress_bar, progress_args=(callback_query.message, st))
            else: 
                await client.send_video(user_id, file_path, caption=f"🎬 **By {BOT_NAME}**", progress=progress_bar, progress_args=(callback_query.message, st), supports_streaming=True)
            await callback_query.message.delete()
    except Exception as e: 
        await callback_query.message.edit(f"❌ **Download Error:** {str(e)[:100]}")
    finally: 
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    app.run()
