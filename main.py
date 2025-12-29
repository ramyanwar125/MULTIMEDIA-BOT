import os, asyncio, time
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from engine import get_all_formats, run_download
from flask import Flask
from threading import Thread

# --- خادم الويب للحفاظ على استمرارية الخدمة ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is Online & Healthy"

def run_web():
    web_app.run(host="0.0.0.0", port=8080)

# --- الإعدادات الأساسية ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAEgqqEwFCxvs1_vKqhqwtOmq0svd2eB0Yc"
ADMIN_ID = 7349033289 
DEV_USER = "@TOP_1UP"
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"
CHANNEL_USER = "Fast_Mediia"
USERS_FILE = "users_database.txt" 

app = Client("fast_media_v19_final", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
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
            f"قناة البوت: @{CHANNEL_USER}\n"
            f"بعد الاشتراك، أرسل /start مجدداً.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Join Channel | اشترك الآن", url=f"https://t.me/{CHANNEL_USER}")
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
    tmp = (
        f"🚀 **Transferring.. جاري النقل**\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"◈ **Progress:** `{bar}` **{percentage:.1f}%**\n"
        f"◈ **Speed:** `{speed/(1024*1024):.2f} MB/s` ⚡️\n"
        f"◈ **Size:** `{current/(1024*1024):.1f}` / `{total/(1024*1024):.1f} MB`\n\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    try: await status_msg.edit(tmp)
    except: pass

# --- الأوامر ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await check_subscription(client, message): return
    add_user(message.from_user.id)
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID: kb[0].append('📣 Broadcast | إذاعة')
    
    welcome_text = (
        f"✨━━━━━━━━━━━━━✨\n"
        f"  🙋‍♂️ Welcome | أهلاً بك يا **{message.from_user.first_name}**\n"
        f"  🌟 In **{BOT_NAME}** World\n"
        f"✨━━━━━━━━━━━━━✨\n\n"
        f"🚀 **Fast Downloader for:**\n"
        f"📹 YouTube | 📸 Instagram | 🎵 TikTok\n"
        f"👻 Snapchat | 🔵 Facebook\n\n"
        f"👇 **Send link now! | أرسل الرابط الآن!**"
    )
    await message.reply(welcome_text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    if not await check_subscription(client, message): return
    text, user_id = message.text, message.from_user.id
    
    if text == '🔄 Restart Service | بدء الخدمة':
        await message.reply("📡 **System Ready.. النظام جاهز!** ⚡️")
        return
    
    if "http" in text:
        status = await message.reply("🔍 **Analyzing.. جاري المعالجة** ⏳")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            if not formats or "error" in str(formats).lower():
                await status.edit("❌ **فشل استخراج البيانات. تأكد من صحة الرابط.**")
                return
            
            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ **تم العثور على الجودات:**\nإختر ما تريد تحميله: 👇", reply_markup=InlineKeyboardMarkup(btns))
        except Exception as e:
            await status.edit(f"❌ **حدث خطأ أثناء المعالجة:**\n`{str(e)[:50]}`")

@app.on_callback_query()
async def download_cb(client, callback_query):
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    
    if not url:
        await callback_query.answer("⚠️ انتهت الجلسة، ارسل الرابط مجدداً", show_alert=True)
        return
    
    status_msg = await callback_query.message.edit("⚙️ **جاري التحميل المعالجة...**\n━━━━━━━━━━━━━━━━━━\n📡 **الاتصال:** `Direct` ⚡️")
    
    is_audio = "audio" in f_id or "bestaudio" in f_id
    file_path = f"media_{user_id}.{'m4a' if is_audio else 'mp4'}"
    
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        if os.path.exists(file_path):
            st_time = time.time()
            if is_audio:
                await client.send_audio(user_id, file_path, caption=f"🎵 **{BOT_NAME}**", progress=progress_bar, progress_args=(status_msg, st_time))
            else:
                await client.send_video(user_id, file_path, caption=f"🎬 **{BOT_NAME}**", progress=progress_bar, progress_args=(status_msg, st_time))
            
            await status_msg.delete()
        else:
            await status_msg.edit("❌ **فشل تحميل الملف من السيرفر.**")
    except Exception as e:
        await status_msg.edit(f"❌ **خطأ أثناء الرفع:**\n`{str(e)[:100]}`")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    app.run()
