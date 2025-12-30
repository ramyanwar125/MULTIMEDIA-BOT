# استخدام نسخة بايثون مستقرة
FROM python:3.10-slim

# تثبيت FFmpeg لدمج الصوت والفيديو وتثبيت الأدوات الأساسية
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ جميع ملفات المشروع إلى الحاوية
COPY . .

# أمر التشغيل (تأكد أن اسم ملفك هو main.py)
CMD ["python", "main.py"]
