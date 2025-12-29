import os, asyncio, time
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from engine import get_all_formats, run_download

# --- الإعدادات ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAHgMSW6NCwveOfuTEvTEbr17wtMl0VeSBw" 
ADMIN_ID = 7349033289 
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia" 
USERS_FILE = "users_database.txt" 

app = Client("fast_media_v2_final", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_cache = {}

# --- دالات النظام ---
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
            f"⚠️ **عذراً، يجب عليك الاشتراك في القناة أولاً!**\n\n"
            f"قناة البوت: @{CHANNEL_USER}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Join Channel | اشترك الآن", url=f"https://t.me/{CHANNEL_USER}")
            ]])
        )
        return False
    except: return True

# --- شريط التقدم ---
async def progress_bar(current, total, status_msg, start_time):
    now = time.time()
    if now - start_time < 3.5: return 
    percentage = current * 100 / total
    speed = current / (now - start_time)
    bar = "▬" * int(percentage // 10) + "▭" * (10 - int(percentage // 10))
    try:
        await status_msg.edit(
            f"🚀 **Transferring.. جاري النقل**\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"◈ **Progress:** `{bar}` **{percentage:.1f}%**\n"
            f"◈ **Speed:** `{speed/(1024*1024):.2f} MB/s` ⚡️\n\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
    except: pass

# --- الأوامر ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await check_subscription(client, message): return
    add_user(message.from_user.id)
    
    # رسالة ترحيب فخمة
    welcome_text = (
        f"✨━━━━━━━━━━━━━✨\n"
        f"  🙋‍♂️ **أهلاً بك يا {message.from_user.first_name}**\n"
        f"  🌟 **في بوت {BOT_NAME}**\n"
        f"✨━━━━━━━━━━━━━✨\n\n"
        f"🚀 **يمكنني التحميل من المواقع التالية:**\n"
        f"YouTube, TikTok, Instagram, Facebook\n\n"
        f"🔗 **فقط أرسل لي الرابط الآن!**"
    )
    
    kb = [['🔄 بدء الخدمة'], ['👨‍💻 المطور']]
    if message.from_user.id == ADMIN_ID: kb[0].append('📣 الإذاعة')
    
    await message.reply(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

@app.on_message(filters.regex('👨‍💻 المطور') & filters.private)
async def dev_info(client, message):
    await message.reply(f"👤 **المطور:** {DEV_USER}\n\nيمكنك التواصل مع المطور لأي استفسار أو طلب بوت خاص.")

@app.on_message(filters.regex('📣 الإذاعة') & filters.private & filters.user(ADMIN_ID))
async def broadcast_manager(client, message):
    await message.reply("📝 **أرسل الآن الرسالة التي تريد إذاعتها لجميع المستخدمين (نص، صورة، فيديو):**")

# معالجة الإذاعة عند إرسال المحتوى
@app.on_message(filters.private & filters.user(ADMIN_ID) & ~filters.command(["start"]))
async def do_broadcast(client, message):
    if message.text in ['🔄 بدء الخدمة', '👨‍💻 المطور', '📣 الإذاعة'] or "http" in (message.text or ""):
        return
        
    users = open(USERS_FILE, "r").read().splitlines()
    count = 0
    status = await message.reply("⏳ **جاري الإذاعة...**")
    for user in users:
        try:
            await message.copy(int(user))
            count += 1
            await asyncio.sleep(0.1) # منع الحظر
        except: pass
    await status.edit(f"✅ **تمت الإذاعة بنجاح إلى {count} مستخدم.**")

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    if not await check_subscription(client, message): return
    if "http" in message.text:
        status = await message.reply("🔍 **جاري فحص الرابط ومعالجته...**")
        try:
            formats = await asyncio.to_thread(get_all_formats, message.text)
            user_cache[message.from_user.id] = message.text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ **تم العثور على الجودات المتوفرة:**\nإختر الجودة التي تناسبك: 👇", reply_markup=InlineKeyboardMarkup(btns))
        except: await status.edit("❌ **عذراً، الرابط غير مدعوم أو فيه مشكلة.**")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    if not url: return
    
    status_msg = await callback_query.message.edit("⚙️ **جاري سحب الملف من المصدر...**")
    file_path = f"media_{user_id}.mp4"
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        if os.path.exists(file_path):
            st_time = time.time()
            await client.send_video(user_id, file_path, caption=f"🎬 **تم التحميل بواسطة {BOT_NAME}**", 
                                   progress=progress_bar, progress_args=(status_msg, st_time))
            # رسالة النجاح النهائية
            await client.send_message(user_id, f"✨━━━━━━━━━━━━━✨\n✅ **تم تحميل وإرسال الفيديو بنجاح!**\n✨━━━━━━━━━━━━━✨")
            await status_msg.delete()
    except Exception as e: await status_msg.edit(f"❌ **حدث خطأ:** `{e}`")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    for f in os.listdir():
        if f.endswith(".session") or f.endswith(".session-journal"):
            try: os.remove(f)
            except: pass
    print("🚀 البوت انطلق الآن بكافة مميزاته...")
    app.run()
