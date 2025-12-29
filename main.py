import os, asyncio, time
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from engine import get_all_formats, run_download

# --- الإعدادات المحدثة ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAG2YCeBsEew587TQoXBTnBQgBQgvLbI7p8" # التوكن الجديد
ADMIN_ID = 7349033289 
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia"
USERS_FILE = "users_database.txt"

# استخدام نظام الجلسة في الذاكرة لتخطي أخطاء الـ API ID في Railway
app = Client(
    "fast_media_v19", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    in_memory=True 
)

user_cache = {}

# --- دوال قاعدة البيانات والاشتراك ---

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
            f"⚠️ **يجب عليك الاشتراك في القناة أولاً!**\n\n@{CHANNEL_USER}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ اشترك الآن", url=f"https://t.me/{CHANNEL_USER}")
            ]])
        )
        return False
    except: return True

# --- شريط التقدم ---

async def progress_bar(current, total, status_msg, start_time):
    try:
        now = time.time()
        diff = now - start_time
        if round(diff % 4.0) == 0 or current == total:
            percentage = current * 100 / total
            speed = current / diff if diff > 0 else 0
            bar = "▬" * int(percentage // 10) + "▭" * (10 - int(percentage // 10))
            await status_msg.edit(
                f"🚀 **جاري الرفع...**\n"
                f"📊 `{bar}` {percentage:.1f}%\n"
                f"⚡ السرعة: `{speed/(1024*1024):.1f} MB/s`"
            )
    except: pass

# --- الأوامر ---

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await check_subscription(client, message): return
    add_user(message.from_user.id)
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID: kb[1].append('📣 Broadcast | إذاعة')
    await message.reply(f"🙋‍♂️ أهلاً بك في **{BOT_NAME}**\nأرسل الرابط للتحميل الآن!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    if not await check_subscription(client, message): return
    text, user_id = message.text, message.from_user.id
    
    if text == '👨‍💻 Developer | المطور':
        msg = f"👑 **المطور:** {DEV_USER}\n📊 **المستخدمين:** `{get_users_count()}`"
        await message.reply(msg)
        return

    if "http" in text:
        status = await message.reply("🔍 **جاري فحص الرابط...**")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ اختر الجودة المطلوبة:", reply_markup=InlineKeyboardMarkup(btns))
        except: await status.edit("❌ فشل معالجة الرابط.")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    if not url: return

    status_msg = await callback_query.message.edit("⚙️ **جاري التحميل... يرجى الانتظار**")
    is_audio = "audio" in f_id
    file_path = f"media_{user_id}_{int(time.time())}.{'m4a' if is_audio else 'mp4'}"
    
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        if os.path.exists(file_path):
            st = time.time()
            await status_msg.edit("📤 **اكتمل التحميل، جاري الرفع...**")
            if is_audio: 
                await client.send_audio(user_id, file_path, caption=f"🎵 {BOT_NAME}", progress=progress_bar, progress_args=(status_msg, st))
            else: 
                await client.send_video(user_id, file_path, caption=f"🎬 {BOT_NAME}", supports_streaming=True, progress=progress_bar, progress_args=(status_msg, st))
            await status_msg.delete()
        else:
            await status_msg.edit("❌ لم يتم العثور على الملف.")
    except Exception as e: 
        await status_msg.edit(f"❌ خطأ: {e}")
    finally: 
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    print("✅ البوت يعمل الآن بالتوكن الجديد...")
    app.run()
