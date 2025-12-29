import os
import asyncio
from pyrogram import Client, filters
from flask import Flask
from threading import Thread

# خادم ويب بسيط لإرضاء المنصة
app_web = Flask(__name__)
@app_web.route('/')
def home(): return "Bot is running!"

def run_web():
    app_web.run(host="0.0.0.0", port=8080)

# إعدادات البوت
API_ID = 33536164
API_HASH = "c4f81cfa1dc011bcf66c6a4a58560fd2"
BOT_TOKEN = "8320774023:AAEgqqEwFCxvs1_vKqhqwtOmq0svd2eB0Yc"

bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("✅ مبروك! البوت يعمل الآن على Koyeb.")

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.run()
