import os
import yt_dlp

def prepare_engine():
    """التحقق من وجود ملف الكوكيز الذي يحتوي على بيانات يوتيوب وإنستجرام"""
    cookie_file = "cookies.txt"
    if not os.path.exists(cookie_file):
        # سيعود بـ None إذا لم يجد الملف، لكننا نفضل وجوده لضمان تخطي الحظر
        return None
    return cookie_file

def get_all_formats(url):
    """استخراج الجودات المتاحة مع معالجة خاصة للفيسبوك والإنستجرام"""
    cookie_path = prepare_engine()
    
    ydl_opts = {
        'quiet': True, 
        'nocheckcertificate': True, 
        'no_warnings': True,
        'cookiefile': cookie_path if cookie_path else None,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {}

        # التحقق من نوع المنصة لضمان جلب فيديو كامل (صوت + صورة)
        is_social = any(x in url for x in ["facebook.com", "fb.watch", "instagram.com"])

        if is_social:
            # دمج أفضل فيديو مع أفضل صوت (يحل مشكلة "صوت فقط" في فيسبوك)
            formats_btns["🎬 Best Quality | أفضل جودة"] = "bestvideo+bestaudio/best"
        else:
            # يوتيوب والمواقع الأخرى: استخراج الجودات المدمجة مباشرة
            for f in info.get('formats', []):
                # نختار فقط الملفات التي تحتوي فيديو وصوت معاً بصيغة mp4
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    res = f.get('height')
                    if res:
                        formats_btns[f"🎬 {res}p"] = f.get('format_id')
        
        # إضافة خيار تحميل الصوت فقط دائماً
        formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
        
        return formats_btns

def run_download(url, format_id, file_path):
    """تنفيذ التحميل الفعلي والدمج باستخدام FFmpeg"""
    cookie_path = prepare_engine()
    
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': cookie_path if cookie_path else None,
        'nocheckcertificate': True,
        'quiet': True,
        # --- إعدادات السرعة الفائقة ---
        'concurrent_fragment_downloads': 15, 
        'continuedl': True,
        'buffersize': 1024 * 1024,
        'retries': 10,
        # --- إعدادات معالجة الفيديو (تتطلب وجود FFmpeg) ---
        'merge_output_format': 'mp4',
        'postprocessor_args': [
            '-c:v', 'copy', # نسخ الفيديو بدون إعادة ترميز لتوفير الوقت
            '-c:a', 'aac'   # ترميز الصوت بصيغة متوافقة
        ],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
