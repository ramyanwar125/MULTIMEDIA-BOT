import os, asyncio, time, re, threading, sys
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import yt_dlp
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 1. منع تكرار النسخ (Anti-Double Instance) ---
LOCK_FILE = "bot.lock"
def check_single_instance():
    if os.path.exists(LOCK_FILE):
        try: os.remove(LOCK_FILE)
        except: sys.exit(1)
    with open(LOCK_FILE, "w") as f: f.write(str(os.getpid()))
check_single_instance()

# --- 2. سيرفر الصحة لريندر ---
def run_health_check_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is Running")
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

# --- 3. الإعدادات ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8254937829:AAE2ayqwQJlxix9VC70sWvj2Ss5nSOxgId0"
ADMIN_ID = 7349033289 
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia" # اسم القناة بدون @
USERS_FILE = "users_database.txt" 
MAX_SIZE_MB = 450 
COOKIES_FILE = "cookies.txt" # تأكد من رفع هذا الملف

app = Client("fast_media_v999", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_cache = {}

# --- 4. وظائف الاشتراك الإجباري والقاعدة ---
async def check_subscribe(client, message):
    if not CHANNEL_USER: return True
    try:
        user = await client.get_chat_member(CHANNEL_USER, message.from_user.id)
        return True
    except UserNotParticipant:
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USER}")],
            [InlineKeyboardButton("✅ تم الاشتراك", callback_data="check_sub")]
        ])
        await message.reply(f"⚠️ **عذراً! يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت.**\n\n🔹 @{CHANNEL_USER}", reply_markup=btn)
        return False
    except Exception: return True

def add_user(user_id):
    if not os.path.exists(USERS_FILE): open(USERS_FILE, "w").close()
    users = open(USERS_FILE, "r").read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f: f.write(f"{user_id}\n")

# --- 5. محرك التحميل مع الكوكيز ---
def get_all_formats(url):
    ydl_opts = {
        'quiet': True, 
        'nocheckcertificate': True,
        'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {}
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                res = f.get('height')
                size = f.get('filesize') or f.get('filesize_approx')
                if res:
                    size_mb = size / (1024 * 1024) if size else 0
                    if size_mb > MAX_SIZE_MB:
                        label, fid = f"⚠️ {res}p ({int(size_mb)}MB > Limit)", "too_large"
                    else:
                        label, fid = f"🎬 {res}p" + (f" ({int(size_mb)}MB)" if size_mb > 0 else ""), f.get('format_id')
                    formats_btns[label] = fid
        
        sorted_labels = sorted(formats_btns.keys(), key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0, reverse=True)
        final = {l: formats_btns[l] for l in sorted_labels}
        final["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
        return final

async def progress_bar(current, total, status_msg, start_time):
    now = time.time()
    if now - start_time < 3.0: return
    percentage = current * 100 / total
    speed = current / (now - start_time)
    bar = "▬" * int(percentage // 10) + "▭" * (10 - int(percentage // 10))
    try: await status_msg.edit(f"🚀 **Transferring..**\n`{bar}` **{percentage:.1f}%**\n⚡️ `{speed/(1024*1024):.2f} MB/s`")
    except: pass

# --- 6. معالجة الرسائل (الترحيب والإنهاء موجودة هنا) ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await check_subscribe(client, message): return
    add_user(message.from_user.id)
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID: kb.append(['📣 Broadcast | إذاعة'])
    
    welcome_text = (
        f"✨━━━━━━━━━━━━━✨\n"
        f"  🙋‍♂️ Welcome | أهلاً بك يا **{message.from_user.first_name}**\n"
        f"  🌟 In **{BOT_NAME}** World\n"
        f"✨━━━━━━━━━━━━━✨\n\n"
        f"🚀 **بوت تحميل سريع من:**\n"
        f"📹 YouTube | 📸 Instagram | 🎵 TikTok\n\n"
        f"👇 **أرسل الرابط الآن!**"
    )
    await message.reply(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    if not await check_subscribe(client, message): return
    text, user_id = message.text, message.from_user.id
    
    if text == '👨‍💻 Developer | المطور':
        await message.reply(f"👑 **Main Developer:** {DEV_USER}\n📢 **Channel:** @{CHANNEL_USER}")
        return

    if "http" in text:
        status = await message.reply("🔍 **Analyzing.. جاري المعالجة** ⏳")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ **تم استخراج الجودات بنجاح:**\nاختر الجودة المطلوبة للتحميل: 👇", reply_markup=InlineKeyboardMarkup(btns))
        except Exception as e: await status.edit(f"❌ **حدث خطأ:**\nتأكد من الرابط أو الكوكيز.")

@app.on_callback_query()
async def callbacks(client, callback_query):
    data, user_id = callback_query.data, callback_query.from_user.id
    if data == "check_sub":
        if await check_subscribe(client, callback_query.message):
            await callback_query.message.edit("✅ تم التحقق! يمكنك الآن إرسال الرابط.")
        else: await callback_query.answer("⚠️ لم تشترك بعد!", show_alert=True)
        return

    url = user_cache.get(user_id)
    if not url or data == "too_large":
        await callback_query.answer("⚠️ غير متاح أو الحجم كبير جداً!", show_alert=True); return
    
    status_msg = await callback_query.message.edit("⚙️ **جاري التحميل والمعالجة...**")
    file_path = f"media_{user_id}.{'m4a' if 'audio' in data else 'mp4'}"
    
    try:
        ydl_opts = {'outtmpl': file_path, 'format': data, 'quiet': True, 'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None}
        await asyncio.to_thread(lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))
        
        if os.path.exists(file_path):
            st = time.time()
            if "audio" in data:
                await client.send_audio(user_id, file_path, caption=f"🎵 **By {BOT_NAME}**", progress=progress_bar, progress_args=(status_msg, st))
            else:
                await client.send_video(user_id, file_path, caption=f"🎬 **By {BOT_NAME}**", progress=progress_bar, progress_args=(status_msg, st))
            
            # --- رسالة الانتهاء والشكر ---
            thanks_text = (
                f"✨ **Mission Completed | تمت المهمة** ✨\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🤖 **Bot:** {BOT_NAME}\n"
                f"👨‍💻 **Dev:** {DEV_USER}\n\n"
                f"🌟 **شكراً لاستخدامك خدمتنا!**\n"
                f"📢 **Channel:** @{CHANNEL_USER}\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            await client.send_message(user_id, thanks_text)
            await status_msg.delete()
    except Exception as e: await status_msg.edit(f"❌ خطأ أثناء التحميل.")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    threading.Timer(5, lambda: threading.Thread(target=run_health_check_server, daemon=True).start()).start()
    app.run()
