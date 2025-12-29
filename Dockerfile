# استخدام بايثون كبيئة أساسية
FROM python:3.10-slim

# تحديث النظام وتثبيت FFmpeg إجبارياً
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل
WORKDIR /app

# نسخ ملف المكتبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كل ملفات البوت (main.py, engine.py, cookies.txt)
COPY . .

# أمر تشغيل البوت
CMD ["python", "main.py"]
