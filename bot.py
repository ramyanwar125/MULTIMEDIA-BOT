import os, asyncio, time, threading
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from engine import get_all_formats, run_download
from flask import Flask
from pymongo import MongoClient
import certifi

# --- سيرفر Flask لمنع ريندر من إعادة التشغيل العشوائي ---
server = Flask('')
@server.route('/')
def home(): return "Bot is Running!"
def run_web():
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- الإعدادات ---
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAFiFH3DMFZVI-njS3i-h50q4WmNwGpdpeg"
ADMIN_ID = 7349033289 
BOT_NAME = "『 ＦＡＳＴ ＭＥＤＩＡ 』"

# --- اتصال MongoDB ---
MONGO_URL = "mongodb+srv://ramyanwar880_db_user:ns8O3Y2eCr7aLdxw@cluster0.nezvqdf.mongodb.net/?appName=Cluster0" 
db_client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())
db = db_client["fast_media_bot"]
users_col = db["users"]

# --- تعريف الكلاينت ---
app = Client("fast_media_v19", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_cache = {}

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    # إضافة المستخدم للقاعدة
    if not users_col.find_one({"user_id": message.from_user.id}):
        users_col.insert_one({"user_id": message.from_user.id})
    
    kb = [['🔄 Restart Service | بدء الخدمة'], ['👨‍💻 Developer | المطور']]
    if message.from_user.id == ADMIN_ID: kb[1].append('📣 Broadcast | إذاعة')
    
    await message.reply(
        f"✨━━━━━━━━━━━━━✨\n  🙋‍♂️ أهلاً بك يا **{message.from_user.first_name}**\n  🌟 في بوت **{BOT_NAME}**\n✨━━━━━━━━━━━━━✨\n\n👇 **أرسل الرابط الآن!**",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )

@app.on_message(filters.text & filters.private)
async def handle_text(client, message):
    text, user_id = message.text, message.from_user.id
    
    if "http" in text:
        status = await message.reply("🔍 **جاري المعالجة...**")
        try:
            formats = await asyncio.to_thread(get_all_formats, text)
            user_cache[user_id] = text
            btns = [[InlineKeyboardButton(res, callback_data=fid)] for res, fid in formats.items()]
            await status.edit("✅ **اختر الجودة:**", reply_markup=InlineKeyboardMarkup(btns))
        except:
            await status.edit("❌ **فشل في استخراج الروابط.**")

@app.on_callback_query()
async def download_cb(client, callback_query):
    # مسح الـ Cache بعد الاستخدام لمنع أي تكرار في التحميل
    f_id, user_id = callback_query.data, callback_query.from_user.id
    url = user_cache.get(user_id)
    
    if not url:
        return await callback_query.answer("⚠️ انتهت الجلسة، أرسل الرابط مجدداً", show_alert=True)
    
    await callback_query.message.edit("⚙️ **جاري التحميل...**")
    file_path = f"media_{user_id}_{int(time.time())}.mp4" # اسم فريد للملف لمنع التداخل
    
    try:
        await asyncio.to_thread(run_download, url, f_id, file_path)
        if os.path.exists(file_path):
            await client.send_video(user_id, file_path, caption=f"🎬 **بواسطة {BOT_NAME}**")
            await callback_query.message.delete()
            # حذف الرابط من الكاش بعد نجاح الإرسال لضمان عدم التكرار
            user_cache.pop(user_id, None)
    except Exception as e:
        await callback_query.message.edit(f"❌ حدث خطأ: {e}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)

if __name__ == "__main__":
    # تشغيل سيرفر Flask في ثريد منفصل
    threading.Thread(target=run_web, daemon=True).start()
    
    # تشغيل البوت مع خاصية حذف التحديثات المعلقة (الحل السحري للتكرار)
    print("Bot is starting...")
    app.run()
