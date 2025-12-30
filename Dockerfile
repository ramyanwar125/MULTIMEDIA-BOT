# استخدام نسخة بايثون خفيفة
FROM python:3.10-slim

# تثبيت التحديثات و FFmpeg الضروري لتحميل الفيديوهات
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات أولاً لتسريع البناء
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات البوت (bot.py, engine.py, cookies...)
COPY . .

# تشغيل البوت
CMD ["python", "bot.py"]
