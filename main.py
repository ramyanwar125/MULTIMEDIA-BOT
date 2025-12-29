import os, asyncio, time
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from engine import get_all_formats, run_download

# --- الإعدادات المحدثة ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAHgMSW6NCwveOfuTEvTEbr17wtMl0VeSBw" # التوكن الجديد
ADMIN_ID = 7349033289 
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia" 
USERS_FILE = "users_database.txt" 

# اسم جلسة جديد تماماً لمنع أي تداخل مع التوكن القديم
app = Client("fast_media_v2_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_cache = {}

# --- دالات النظام ---
def add_user(user_id):
    if not os.path.exists(USERS_FILE): open(USERS_FILE, "w").close()
    try:
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
        if str(user_id) not in users:
            with open(USERS_FILE, "a") as f: f.write(f"{user_id}\n")
    except: pass

async def check_subscription(client, message):
    try:
        await client.get_chat_member(CHANNEL_USER, message.from_user.id)
        return True
    except UserNotParticipant:
        await message.reply(
            f"⚠️ **يجب الاشتراك في القناة أولاً!**\n\nقناة البوت: @{CHANNEL_USER}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ اشترك الآن", url=f"https://t.me/{CHANNEL_USER}")
            ]])
        )
        return False
    except: return True

async def progress_bar(current, total, status_msg, start_time):
    now = time.time()
    if now - start_time < 3.0: return 
    percentage = current * 100 / total
    speed = current / (now - start_time)
    bar = "▬" * int(percentage // 10) + "▭" * (10 - int(percentage // 10))
    try:
        await status_msg.edit(
            f"🚀 **جاري النقل..**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"◈ **التقدم:** `{percentage:.1f}%`\n"
            f"◈ **السرعة:** `{speed/(1024*1024):.2f} MB/s`⚡️\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
    except: pass

# --- الأوامر ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await check_subscription(client, message): return
    add_user(message.from_user.id)
    kb = [['🔄 بدء الخدمة'], ['👨‍💻 المطور']]
    await message.reply(f"🙋‍♂️ أهلاً بك في **{BOT_NAME}**\nأرسل رابط الفيديو للتحميل فوراً 👇", 
                        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    if not await check_subscription(client, message): return
    if "http" in message.text:
        status = await message.reply("🔍 جاري فحص الرابط...")
        try:
            formats = await asyncio.to_thread(get_all_formats, message.text)
            user_cache[message.from_user.id] = message.text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ تم العثور على الجودات:\nإختر ما تريد تحميله: 👇", reply_markup=InlineKeyboardMarkup(btns))
        except:
            await status.edit("❌ فشل استخراج البيانات، تأكد من الرابط.")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    if not url: return
    
    status_msg = await callback_query.message.edit("⚙️ جاري التحميل من السيرفر...")
    file_path = f"media_{user_id}.mp4"
    
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        if os.path.exists(file_path):
            st_time = time.time()
            await client.send_video(user_id, file_path, caption=f"🎬 **By {BOT_NAME}**", 
                                   progress=progress_bar, progress_args=(status_msg, st_time))
            await client.send_message(user_id, "✅ تمت المهمة بنجاح!")
            await status_msg.delete()
        else:
            await status_msg.edit("❌ فشل تحميل الملف.")
    except Exception as e:
        await status_msg.edit(f"❌ خطأ: `{str(e)[:50]}`")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    # تنظيف شامل قبل التشغيل
    for f in os.listdir():
        if f.endswith(".session") or f.endswith(".session-journal"):
            try: os.remove(f)
            except: pass
    print("🚀 تشغيل البوت بالتوكن الجديد...")
    app.run()
