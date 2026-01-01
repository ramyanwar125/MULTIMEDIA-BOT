import os, asyncio, time, re
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import yt_dlp
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- سيرفر وهمي لإرضاء ريندر (Port Binding) ---
def run_health_check_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is Running")
    
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

# --- Config | الإعدادات ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8254937829:AAE2ayqwQJlxix9VC70sWvj2Ss5nSOxgId0"
ADMIN_ID = 7349033289 
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia" 
CHANNEL_ID = -1002235941650  
USERS_FILE = "users_database.txt" 
MAX_SIZE_MB = 450  # الحد الأقصى للتحميل بالميجابايت

# --- Engine Section | قسم المحرك ---
def prepare_engine():
    cookie_file = "cookies_stable.txt"
    if not os.path.exists(cookie_file):
        with open(cookie_file, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1766757959\tGPS\t1\n")
    return cookie_file

def get_all_formats(url):
    ydl_opts = {
        'quiet': True, 
        'cookiefile': prepare_engine(), 
        'nocheckcertificate': True, 
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {}
        all_formats = info.get('formats', [])
        
        # فحص الحجم قبل عرض الجودات
        filesize = info.get('filesize') or info.get('filesize_approx')
        if filesize and filesize > (MAX_SIZE_MB * 1024 * 1024):
            return "too_big"

        for f in all_formats:
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                res = f.get('height')
                if res:
                    label = f"🎬 {res}p"
                    formats_btns[label] = f.get('format_id')
        if not formats_btns:
            formats_btns["🎬 Best Quality | أفضل جودة"] = "best"
        
        def extract_res(label):
            nums = re.findall(r'\d+', label)
            return int(nums[0]) if nums else 0
        
        sorted_labels = sorted(formats_btns.keys(), key=extract_res, reverse=True)
        final_formats = {label: formats_btns[label] for label in sorted_labels}
        final_formats["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
        return final_formats

def run_download(url, format_id, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': 'cookies_stable.txt',
        'nocheckcertificate': True,
        'quiet': True,
        'continuedl': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # فحص إضافي للحجم قبل البدء بالتحميل الفعلي
        info = ydl.extract_info(url, download=False)
        filesize = info.get('filesize') or info.get('filesize_approx')
        if filesize and filesize > (MAX_SIZE_MB * 1024 * 1024):
             raise Exception("LIMIT_EXCEEDED")
        ydl.download([url])

# --- Bot Section | قسم البوت ---
app = Client("fast_media_v155", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_cache = {}

def add_user(user_id):
    if not os.path.exists(USERS_FILE): open(USERS_FILE, "w").close()
    users = open(USERS_FILE, "r").read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f: f.write(f"{user_id}\n")

def get_users_count():
    if not os.path.exists(USERS_FILE): return 0
    return len(open(USERS_FILE, "r").read().splitlines())

async def progress_bar(current, total, status_msg, start_time):
    now = time.time()
    diff = now - start_time
    if diff < 3.0: return
    percentage = current * 100 / total
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

# --- دالة التحقق من الاشتراك ---
async def check_subscription(client, user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = await client.get_chat_member(CHANNEL_ID, user_id)
        if member.status: return True
    except UserNotParticipant:
        return False
    except Exception:
        return True
    return False

@app.on_message(filters.private)
async def sub_and_start_logic(client, message):
    user_id = message.from_user.id
    add_user(user_id)
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(client, user_id):
        join_button = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel | انضم للقناة 📢", url=f"https://t.me/{CHANNEL_USER}")]])
        await message.reply(
            f"⚠️ **عذراً! يجب عليك الاشتراك في قناة البوت أولاً لاستخدام الخدمة.**\n\n"
            f"📢 القناة: @{CHANNEL_USER}\n\n"
            f"بعد الاشتراك، أرسل /start",
            reply_markup=join_button
        )
        return

    if message.text == "/start" or message.text == '🔄 Restart Service | بدء الخدمة':
        kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
        if user_id == ADMIN_ID:
            kb.append(['📣 Broadcast | إذاعة'])
        
        welcome_text = (
            f"✨━━━━━━━━━━━━━✨\n"
            f"  🙋‍♂️ Welcome | أهلاً بك يا **{message.from_user.first_name}**\n"
            f"  🌟 In **{BOT_NAME}** World\n"
            f"✨━━━━━━━━━━━━━✨\n\n"
            f"🚀 **Fast Downloader for | بوت تحميل سريع:**\n"
            f"📹 YouTube | 📸 Instagram | 🎵 TikTok\n"
            f"👻 Snapchat | 🔵 Facebook\n\n"
            f"👇 **Send link now! | أرسل الرابط الآن!**"
        )
        await message.reply(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        return

    await handle_text(client, message)

async def handle_text(client, message):
    text, user_id = message.text, message.from_user.id
    
    if text == '👨‍💻 Developer | المطور':
        msg = f"👑 **Main Developer:** {DEV_USER}\n📢 **Our Channel:** @{CHANNEL_USER}\n"
        if user_id == ADMIN_ID:
            msg += f"📊 **Total Users:** `{get_users_count()}`"
        await message.reply(msg)
        return

    if text == '📣 Broadcast | إذاعة' and user_id == ADMIN_ID:
        await message.reply("📥 **Send your message | أرسل رسالة الإذاعة:**")
        user_cache[f"bc_{user_id}"] = True
        return

    if user_cache.get(f"bc_{user_id}"):
        users = open(USERS_FILE).read().splitlines()
        for u in users:
            try: await message.copy(int(u))
            except: pass
        await message.reply("✅ **Broadcast Sent | تمت الإذاعة**")
        user_cache[f"bc_{user_id}"] = False
        return

    if text and "http" in text:
        # التحقق من الاشتراك قبل البدء بالمعالجة
        if not await check_subscription(client, user_id):
            await message.reply("⚠️ يرجى الاشتراك في القناة أولاً @"+CHANNEL_USER)
            return

        status = await message.reply("🔍 **Analyzing.. جاري المعالجة** ⏳")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            
            if formats == "too_big":
                await status.edit(f"❌ **عذراً! الحجم كبير جداً.**\n\nالحد الأقصى للتحميل هو **{MAX_SIZE_MB} ميجابايت**.")
                return

            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ **Formats Found | تم الاستخراج**\nChoose your option: 👇", reply_markup=InlineKeyboardMarkup(btns))
        except: 
            await status.edit("❌ **Error | فشل في جلب البيانات**")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    
    # تحقق من الاشتراك عند الضغط على أزرار الجودة
    if not await check_subscription(client, user_id):
        await callback_query.answer("⚠️ يجب عليك الاشتراك في القناة أولاً!", show_alert=True)
        return

    url = user_cache.get(user_id)
    if not url:
        await callback_query.answer("⚠️ Session Expired", show_alert=True); return
    
    status_msg = await callback_query.message.edit("⚙️ **Processing.. جاري التنفيذ**")
    is_audio = "audio" in f_id
    file_path = f"media_{user_id}.{'m4a' if is_audio else 'mp4'}"
    
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        if os.path.exists(file_path):
            st = time.time()
            if is_audio: 
                await client.send_audio(user_id, file_path, caption=f"🎵 **Audio by {BOT_NAME}**", progress=progress_bar, progress_args=(status_msg, st))
            else: 
                await client.send_video(user_id, file_path, caption=f"🎬 **Video by {BOT_NAME}**", progress=progress_bar, progress_args=(status_msg, st))
            
            await client.send_message(user_id, f"✨ **Mission Completed | تمت المهمة**\n📢 **Channel:** @{CHANNEL_USER}")
            await status_msg.delete()
    except Exception as e:
        if str(e) == "LIMIT_EXCEEDED":
            await status_msg.edit(f"⚠️ **فشل التحميل:** الحجم يتجاوز الـ {MAX_SIZE_MB} ميجابايت.")
        else:
            await status_msg.edit(f"❌ **Failed:** {e}")
    finally: 
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    threading.Thread(target=run_health_check_server, daemon=True).start()
    app.run()
