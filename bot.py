import os, asyncio, time, threading
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from engine import get_all_formats, run_download
from flask import Flask
from pymongo import MongoClient

# --- Flask Server (لضمان بقاء البوت حياً على ريندر) ---
server = Flask('')
@server.route('/')
def home(): return "<h1>Bot is Online!</h1>"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    server.run(host='0.0.0.0', port=port)

# --- الإعدادات الأساسية ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAFiFH3DMFZVI-njS3i-h50q4WmNwGpdpeg"
ADMIN_ID = 7349033289 
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia"

# --- نظام قاعدة البيانات (MongoDB) ---
# ملاحظة: استبدل كلمة 'PASSWORD' بكلمة السر الحقيقية الخاصة بك
MONGO_URL = "mongodb+srv://ramyanwar880_db_user:PASSWORD@cluster0.nezvqdf.mongodb.net/?appName=Cluster0" 
db_client = MongoClient(MONGO_URL)
db = db_client["fast_media_bot"]
users_col = db["users"]

app = Client("fast_media_v19", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_cache = {}

# --- الدوال المساعدة ---
def add_user(user_id):
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({"user_id": user_id})

def get_users_count():
    return users_col.count_documents({})

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
    except: return True

async def progress_bar(current, total, status_msg, start_time):
    now = time.time()
    diff = now - start_time
    if diff < 3.0: return 
    percentage = current * 100 / total
    speed = current / diff
    bar = "▬" * int(percentage // 10) + "▭" * (10 - int(percentage // 10))
    tmp = (f"🚀 **Transferring..**\n`{bar}` **{percentage:.1f}%**\n"
           f"⚡️ Speed: `{speed/(1024*1024):.2f} MB/s`")
    try: await status_msg.edit(tmp)
    except: pass

# --- الأوامر ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await check_subscription(client, message): return
    add_user(message.from_user.id)
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID: kb[1].append('📣 Broadcast | إذاعة')
    await message.reply(f"✨ Welcome **{message.from_user.first_name}** to **{BOT_NAME}**\n\nSend link now! 👇", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    if not await check_subscription(client, message): return
    text, user_id = message.text, message.from_user.id
    
    if text == '👨‍💻 Developer | المطور':
        msg = f"👑 **Main Developer:** {DEV_USER}"
        if user_id == ADMIN_ID: msg += f"\n📊 **Total Users:** `{get_users_count()}`"
        await message.reply(msg)
        return

    if text == '📣 Broadcast | إذاعة' and user_id == ADMIN_ID:
        await message.reply("📥 **Send your message:**")
        user_cache[f"bc_{user_id}"] = True
        return

    if user_cache.get(f"bc_{user_id}"):
        all_users = users_col.find({})
        count = 0
        for u in all_users:
            try: 
                await message.copy(int(u['user_id']))
                count += 1
            except: pass
        await message.reply(f"✅ **Broadcast Sent to {count} users**")
        user_cache[f"bc_{user_id}"] = False
        return

    if "http" in text:
        status = await message.reply("🔍 **Analyzing..**")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ **Choose Quality:**", reply_markup=InlineKeyboardMarkup(btns))
        except: await status.edit("❌ **Unsupported URL or Error!**")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    if not url: return await callback_query.answer("⚠️ Session Expired", show_alert=True)
    
    status = await callback_query.message.edit("⚙️ **Processing...**")
    is_audio = "audio" in f_id
    file_path = f"media_{user_id}.{'m4a' if is_audio else 'mp4'}"
    
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        if os.path.exists(file_path):
            st = time.time()
            if is_audio: await client.send_audio(user_id, file_path, caption=f"🎵 By {BOT_NAME}", progress=progress_bar, progress_args=(status, st))
            else: await client.send_video(user_id, file_path, caption=f"🎬 By {BOT_NAME}", progress=progress_bar, progress_args=(status, st))
            await status.delete()
    except Exception as e: await status.edit(f"❌ Error: {e}")
    finally: 
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    app.run()
