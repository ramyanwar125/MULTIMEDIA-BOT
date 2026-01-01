import os, asyncio, time, re, threading, sys
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import yt_dlp
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- منع تكرار النسخ (Anti-Double Instance) ---
LOCK_FILE = "bot.lock"

def check_single_instance():
    """تمنع تشغيل أكثر من نسخة للبوت في نفس الوقت على ريندر"""
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except Exception:
            print("⚠️ هناك نسخة تعمل بالفعل.. سيتم إغلاق هذه النسخة لتجنب التكرار.")
            sys.exit(1)
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

# تشغيل الفحص فوراً عند تشغيل الملف
check_single_instance()

# --- سيرفر وهمي لإرضاء ريندر (Port Binding) ---
def run_health_check_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is Running")
    
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"📡 Health Check Server started on port {port}")
    server.serve_forever()

# --- Config | الإعدادات ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8254937829:AAE2ayqwQJlxix9VC70sWvj2Ss5nSOxgId0"
ADMIN_ID = 7349033289 
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia" 
USERS_FILE = "users_database.txt" 
MAX_SIZE_MB = 450 

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
        
        for f in all_formats:
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                res = f.get('height')
                size = f.get('filesize') or f.get('filesize_approx')
                
                if res:
                    size_mb = size / (1024 * 1024) if size else 0
                    if size_mb > MAX_SIZE_MB:
                        label = f"⚠️ {res}p ({int(size_mb)}MB > Limit)"
                        fid = "too_large"
                    else:
                        label = f"🎬 {res}p" + (f" ({int(size_mb)}MB)" if size_mb > 0 else "")
                        fid = f.get('format_id')
                    
                    formats_btns[label] = fid
                    
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
        ydl.download([url])

# --- Bot Section | قسم البوت ---
app = Client("fast_media_v200", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
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

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    add_user(message.from_user.id)
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID:
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

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    text, user_id = message.text, message.from_user.id
    
    if text == '🔄 Restart Service | بدء الخدمة':
        await message.reply("📡 **System Ready.. النظام جاهز!** ⚡️")
        return
    
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

    if "http" in text:
        status = await message.reply("🔍 **Analyzing.. جاري المعالجة** ⏳")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ **Formats Found | تم الاستخراج**\nChoose your option: 👇", reply_markup=InlineKeyboardMarkup(btns))
        except: 
            await status.edit("❌ **Error | فشل في جلب البيانات**\nالرابط غير مدعوم أو أن الفيديو خاص.")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    
    if f_id == "too_large":
        await callback_query.answer("⚠️ عفواً، هذا الملف حجمه أكبر من 450 ميجابايت!\nلا يمكن تحميله عبر البوت.", show_alert=True)
        return

    if not url:
        await callback_query.answer("⚠️ انتهت الجلسة، أرسل الرابط مجدداً", show_alert=True); return
    
    status_msg = await callback_query.message.edit("⚙️ **Processing.. جاري التنفيذ**")
    is_audio = "audio" in f_id
    file_path = f"media_{user_id}.{'m4a' if is_audio else 'mp4'}"
    
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        
        if os.path.exists(file_path):
            actual_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if actual_size_mb > MAX_SIZE_MB:
                await status_msg.edit(f"❌ **عفواً، الحجم الفعلي للملف ({int(actual_size_mb)}MB) تجاوز الحد المسموح.**")
                os.remove(file_path)
                return

            st = time.time()
            if is_audio: 
                await client.send_audio(user_id, file_path, caption=f"🎵 **Audio by {BOT_NAME}**", progress=progress_bar, progress_args=(status_msg, st))
            else: 
                await client.send_video(user_id, file_path, caption=f"🎬 **Video by {BOT_NAME}**", progress=progress_bar, progress_args=(status_msg, st))
            
            # --- رسالة الانتهاء والشكر ---
            thanks_text = (
                f"✨ **Mission Completed | تمت المهمة** ✨\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🤖 **Bot:** {BOT_NAME}\n"
                f"👨‍💻 **Dev:** {DEV_USER}\n\n"
                f"🌟 **شكراً لاستخدامك خدمتنا!**\n"
                f"📢 **Channel:** @{CHANNEL_USER}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🚀 *Fast • Simple • High Quality*"
            )
            await client.send_message(user_id, thanks_text)
            await status_msg.delete()
    except Exception as e: 
        await status_msg.edit(f"❌ **Failed:** {str(e)[:100]}")
    finally: 
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    # تشغيل سيرفر الصحة في الخلفية بعد تأخير بسيط لضمان استقرار البوت
    threading.Timer(5, lambda: threading.Thread(target=run_health_check_server, daemon=True).start()).start()
    
    print("🚀 Bot is starting now...")
    app.run()
