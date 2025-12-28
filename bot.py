import os, asyncio, time
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait
from engine import get_all_formats, run_download
from flask import Flask
from threading import Thread
from waitress import serve

# --- نظام الحماية من توقف ريندر (Render Fix) ---
server = Flask('')
@server.route('/')
def home(): return "SERVICE_PROVIDER_ONLINE"

def run_server():
    # ريندر يطلب فتح منفذ (Port) وهذا الكود يقوم بذلك تلقائياً
    port = int(os.environ.get("PORT", 8080))
    serve(server, host='0.0.0.0', port=port)

# --- الإعدادات الأساسية ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAFiFH3DMFZVI-njS3i-h50q4WmNwGpdpeg"
ADMIN_ID = 7349033289 
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia" 
USERS_FILE = "users_database.txt" 

# تغيير اسم الجلسة يحل مشكلة التكرار فوراً
app = Client("fast_media_v25", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
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
                InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{CHANNEL_USER}")
            ]])
        )
        return False
    except Exception: return True

async def progress_bar(current, total, status_msg, start_time):
    now = time.time()
    if now - start_time < 3.0: return # تحديث كل 3 ثواني لتجنب حظر تليجرام
    percentage = current * 100 / total
    speed = current / (now - start_time)
    bar = "▬" * int(percentage // 10) + "▭" * (10 - int(percentage // 10))
    tmp = (f"🚀 **Transferring..**\n`{bar}` **{percentage:.1f}%**\n⚡️ Speed: `{speed/(1024*1024):.2f} MB/s`")
    try: await status_msg.edit(tmp)
    except: pass

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await check_subscription(client, message): return
    add_user(message.from_user.id)
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID: kb[1].append('📣 Broadcast | إذاعة')
    await message.reply(f"✨ **Welcome to {BOT_NAME}**\n\nأرسل الرابط الآن للتحميل!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

@app.on_message(filters.text & filters.private & ~filters.bot)
async def handle_text(client, message):
    # فلتر منع معالجة الرسائل القديمة (يمنع التكرار عند إعادة التشغيل)
    if time.time() - message.date.timestamp() > 50: return

    if not await check_subscription(client, message): return
    text, user_id = message.text, message.from_user.id
    
    if text == '🔄 Restart Service | بدء الخدمة':
        await message.reply("📡 **System Ready!**")
        return
    
    if text == '👨‍💻 Developer | المطور':
        msg = f"👑 **Dev:** {DEV_USER}\n"
        if user_id == ADMIN_ID: msg += f"📊 **Users:** `{get_users_count()}`"
        await message.reply(msg)
        return

    if text == '📣 Broadcast | إذاعة' and user_id == ADMIN_ID:
        await message.reply("📥 **Send broadcast message:**")
        user_cache[f"bc_{user_id}"] = True
        return

    if user_cache.get(f"bc_{user_id}"):
        users = open(USERS_FILE).read().splitlines()
        for u in users:
            try: await message.copy(int(u))
            except: pass
        await message.reply("✅ **Sent!**")
        user_cache[f"bc_{user_id}"] = False
        return

    if "http" in text:
        status = await message.reply("🔍 **Analyzing...**")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ **Choose Quality:**", reply_markup=InlineKeyboardMarkup(btns))
        except: await status.edit("❌ **Link Error or Protected Content.**")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    if not url: return
    
    await callback_query.message.edit("⚙️ **Downloading...**")
    file_path = f"media_{user_id}.{'m4a' if 'audio' in f_id else 'mp4'}"
    
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        if os.path.exists(file_path):
            st = time.time()
            if "audio" in f_id: await client.send_audio(user_id, file_path, progress=progress_bar, progress_args=(callback_query.message, st))
            else: await client.send_video(user_id, file_path, progress=progress_bar, progress_args=(callback_query.message, st))
            await callback_query.message.delete()
    except Exception as e: await callback_query.message.edit(f"❌ Error: {e}")
    finally: 
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    try:
        app.run()
    except FloodWait as e:
        print(f"⚠️ FloodWait: Waiting {e.value} seconds...")
        time.sleep(e.value)
        app.run()
