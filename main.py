import os, asyncio, time, threading, sys
# حل مشكلة عدم العثور على ملف engine عند الرفع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from engine import get_all_formats, run_download
from flask import Flask

# --- Flask Server لضمان عمل ريندر ---
web_app = Flask(__name__)

@web_app.route('/')
def home(): 
    return "Bot is Running!"

def run_web():
    # ريندر يحتاج Port ديناميكي من متغيرات البيئة
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- Config | الإعدادات ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8304738811:AAFSzPbVzT6uT6HfexDHVjtj4iqvm3SRsOc"
ADMIN_ID = 7349033289 
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia" 
USERS_FILE = "users_database.txt" 

app = Client("fast_media_v19", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_cache = {}

def add_user(user_id):
    if not os.path.exists(USERS_FILE): open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f: f.write(f"{user_id}\n")

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
    if diff < 2.5: return
    percentage = current * 100 / total
    speed = current / (diff if diff > 0 else 1)
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
    if not await check_subscription(client, message): return
    add_user(message.from_user.id)
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID: kb[1].append('📣 Broadcast | إذاعة')
    
    await message.reply(
        f"✨ **Welcome {message.from_user.first_name}**\nIn **{BOT_NAME}**\n\nأرسل رابط فيديو لتحميله 🎬",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    if not await check_subscription(client, message): return
    text, user_id = message.text, message.from_user.id

    if "http" in text:
        status = await message.reply("🔍 **Analyzing.. جاري المعالجة** ⏳")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ **تم استخراج الصيغ:**", reply_markup=InlineKeyboardMarkup(btns))
        except Exception as e:
            await status.edit(f"❌ **خطأ:** {str(e)[:50]}")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    if not url: return

    await callback_query.message.edit("⚙️ **جاري التحميل...**")
    file_path = f"media_{user_id}.mp4"
    
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        st = time.time()
        await client.send_video(user_id, file_path, progress=progress_bar, progress_args=(callback_query.message, st))
        await callback_query.message.delete()
    except Exception as e:
        await callback_query.message.edit(f"❌ فشل: {e}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    # تشغيل سيرفر الويب في خلفية منفصلة
    threading.Thread(target=run_web, daemon=True).start()
    # تشغيل البوت مع حذف أي رسائل قديمة متراكمة
    app.run()
