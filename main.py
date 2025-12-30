import os, asyncio, time, threading
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from engine import get_all_formats, run_download
from flask import Flask

# --- Flask Server ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is Running!"

def run_web():
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# --- Config ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8304738811:AAHJOLC8ObX0gRdM8oTqVsuE8q3Ifl95Fd0"
ADMIN_ID = 7349033289 
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia" 
USERS_FILE = "users_database.txt" 

app = Client("fast_media_final_v1", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_cache = {}

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
        await message.reply(
            f"⚠️ **يجب الاشتراك في القناة أولاً!**\n\n@{CHANNEL_USER}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ اشترك الآن", url=f"https://t.me/{CHANNEL_USER}")]])
        )
        return False
    except: return True

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await check_subscription(client, message): return
    add_user(message.from_user.id)
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID: kb[1].append('📣 Broadcast | إذاعة')
    await message.reply(f"🙋‍♂️ أهلاً بك في {BOT_NAME}\nأرسل الرابط الآن للتحميل!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    if not await check_subscription(client, message): return
    text, user_id = message.text, message.from_user.id
    
    if "http" in text:
        status = await message.reply("🔍 **جاري الفحص...**")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            if not formats: raise Exception
            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ **تم استخراج الجودات:**", reply_markup=InlineKeyboardMarkup(btns))
        except: await status.edit("❌ فشل معالجة الرابط، تأكد أنه صحيح.")

@app.on_callback_query()
async def download_cb(client, callback_query):
    # منع التكرار بالرد الفوري
    await callback_query.answer("⏳ جاري بدء التحميل...")
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    
    if not url: return
    
    # تحديث الرسالة لمنع الضغط مرتين
    await callback_query.message.edit("⚙️ **جاري التحميل والمعالجة...**\nيرجى الانتظار.")
    
    is_audio = "audio" in f_id
    file_path = f"media_{user_id}.{'m4a' if is_audio else 'mp4'}"
    
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        if os.path.exists(file_path):
            if is_audio: await client.send_audio(user_id, file_path, caption=f"🎵 {BOT_NAME}")
            else: await client.send_video(user_id, file_path, caption=f"🎬 {BOT_NAME}")
            await callback_query.message.delete()
    except Exception as e: await callback_query.message.edit(f"❌ فشل: {e}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    app.run()
