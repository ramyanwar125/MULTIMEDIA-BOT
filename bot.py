import os, asyncio, time
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from engine import get_all_formats, run_download
from flask import Flask
from threading import Thread
from waitress import serve

# --- Render Web Server (الخادم الاحترافي) ---
server = Flask('')

@server.route('/')
def home():
    return "✅ FAST MEDIA BOT IS ALIVE AND RUNNING!"

def run_server():
    # Render يرسل البورت تلقائياً عبر متغيرات البيئة
    port = int(os.environ.get("PORT", 8080))
    # استخدام serve (waitress) بدلاً من Flask العادي لمنع تحذيرات الإنتاج
    serve(server, host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.daemon = True # لضمان إغلاق الخادم عند إغلاق البوت
    t.start()

# --- Configuration | الإعدادات ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAFiFH3DMFZVI-njS3i-h50q4WmNwGpdpeg"
ADMIN_ID = 7349033289 
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia" 
USERS_FILE = "users_database.txt" 

app = Client("fast_media_v21", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_cache = {}

# --- Helper Functions | وظائف مساعدة ---
def add_user(user_id):
    if not os.path.exists(USERS_FILE): open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f: f.write(f"{user_id}\n")

def get_users_count():
    if not os.path.exists(USERS_FILE): return 0
    with open(USERS_FILE, "r") as f:
        return len(f.read().splitlines())

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
    if diff < 3.0: return # تحديث كل 3 ثوانٍ لمنع الحظر
    percentage = current * 100 / total
    speed = current / diff
    bar = "▬" * int(percentage // 10) + "▭" * (10 - int(percentage // 10))
    tmp = (
        f"🚀 **Transferring.. جاري النقل**\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"◈ **Progress:** `{bar}` **{percentage:.1f}%**\n"
        f"◈ **Speed:** `{speed/(1024*1024):.2f} MB/s` ⚡️\n"
        f"◈ **Size:** `{current/(1024*1024):.1f}` / `{total/(1024*1024):.1f} MB`"
    )
    try: await status_msg.edit(tmp)
    except: pass

# --- Message Handlers | معالجة الرسائل ---

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await check_subscription(client, message): return
    add_user(message.from_user.id)
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID: kb[1].append('📣 Broadcast | إذاعة')
    
    welcome_text = (
        f"✨━━━━━━━━━━━━━✨\n"
        f"  🙋‍♂️ أهلاً بك يا **{message.from_user.first_name}**\n"
        f"  🌟 في عالم **{BOT_NAME}**\n"
        f"✨━━━━━━━━━━━━━✨\n\n"
        f"🚀 **أرسل رابط الفيديو من المنصات التالية:**\n"
        f"📹 YouTube | 📸 Instagram | 🎵 TikTok\n"
        f"👻 Snapchat | 🔵 Facebook\n\n"
        f"👇 **أرسل الرابط الآن!**"
    )
    await message.reply(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

@app.on_message(filters.text & filters.private & ~filters.bot) # فلتر لمنع البوتات والتكرار
async def handle_text(client, message):
    if not await check_subscription(client, message): return
    text, user_id = message.text, message.from_user.id
    
    if text == '🔄 Restart Service | بدء الخدمة':
        await message.reply("📡 **النظام جاهز لاستقبال روابطك!** ⚡️")
        return
    
    if text == '👨‍💻 Developer | المطور':
        msg = f"👑 **Main Developer:** {DEV_USER}\n📢 **Channel:** @{CHANNEL_USER}\n"
        if user_id == ADMIN_ID: msg += f"📊 **Total Users:** `{get_users_count()}`"
        await message.reply(msg)
        return

    # نظام الإذاعة
    if text == '📣 Broadcast | إذاعة' and user_id == ADMIN_ID:
        await message.reply("📥 **أرسل رسالة الإذاعة الآن (نص، صورة، فيديو):**")
        user_cache[f"bc_{user_id}"] = True
        return

    if user_cache.get(f"bc_{user_id}"):
        users = open(USERS_FILE).read().splitlines()
        await message.reply(f"🔄 جاري الإرسال إلى {len(users)} مستخدم...")
        count = 0
        for u in users:
            try: 
                await message.copy(int(u))
                count += 1
                await asyncio.sleep(0.1) # حماية من السبام
            except: pass
        await message.reply(f"✅ تمت الإذاعة بنجاح لـ {count} مستخدم.")
        user_cache[f"bc_{user_id}"] = False
        return

    # معالجة الروابط
    if "http" in text:
        status = await message.reply("🔍 **جاري فحص الرابط واستخراج الجودات...** ⏳")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ **تم العثور على الوسائط!**\nاختر الجودة المطلوبة للتحميل: 👇", reply_markup=InlineKeyboardMarkup(btns))
        except: await status.edit("❌ **عذراً، فشل استخراج البيانات. تأكد من صحة الرابط.**")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    if not url:
        await callback_query.answer("⚠️ انتهت الجلسة، أرسل الرابط مجدداً.", show_alert=True)
        return
    
    await callback_query.message.edit("⚙️ **جاري التحميل والمعالجة...**\n━━━━━━━━━━━━━━━━━━\n📡 **الاتصال:** `Direct Connection` ⚡️")
    is_audio = "audio" in f_id
    file_path = f"media_{user_id}.{'m4a' if is_audio else 'mp4'}"
    
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        if os.path.exists(file_path):
            st = time.time()
            if is_audio: 
                await client.send_audio(user_id, file_path, caption=f"🎵 **{BOT_NAME}**", progress=progress_bar, progress_args=(callback_query.message, st))
            else: 
                await client.send_video(user_id, file_path, caption=f"🎬 **{BOT_NAME}**", progress=progress_bar, progress_args=(callback_query.message, st))
            
            # الرسالة النهائية الجميلة
            await client.send_message(user_id, f"✨━━━━━━━━━━━━━✨\n✅ **تمت المهمة بنجاح**\n✨━━━━━━━━━━━━━✨\n\n📂 **الحالة:** `جاهز للتحميل` 🎬\n🚀 **بواسطة:** **{BOT_NAME}**")
            await callback_query.message.delete()
    except Exception as e: 
        await callback_query.message.edit(f"❌ **فشل التحميل:** {str(e)}")
    finally: 
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    keep_alive() # تشغيل خادم Waitress لتجاوز نظام Port في Render
    app.run()
