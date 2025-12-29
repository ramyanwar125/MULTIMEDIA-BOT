import os
import yt_dlp

def prepare_engine():
    """التحقق من ملف الكوكيز (يوتيوب + إنستجرام)"""
    cookie_file = "cookies.txt"
    if not os.path.exists(cookie_file):
        return None
    return cookie_file

def get_all_formats(url):
    """استخراج الجودات مع دعم كامل للمنصات الاجتماعية"""
    cookie_path = prepare_engine()
    
    ydl_opts = {
        'quiet': True, 
        'nocheckcertificate': True, 
        'no_warnings': True,
        'cookiefile': cookie_path if cookie_path else None,
        'format': 'best', # ضمان جلب معلومات صحيحة في البداية
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats_btns = {}

            # تمييز فيسبوك وإنستجرام وتيك توك لضمان جلب فيديو كامل
            social_platforms = ["facebook.com", "fb.watch", "instagram.com", "tiktok.com"]
            is_social = any(x in url for x in social_platforms)

            if is_social:
                # طلب أفضل فيديو + أفضل صوت (يحل مشكلة "صوت فقط" في فيسبوك)
                formats_btns["🎬 Best Quality | أفضل جودة"] = "bestvideo+bestaudio/best"
            else:
                # يوتيوب والمواقع الأخرى
                for f in info.get('formats', []):
                    # نختار الجودات المدمجة الجاهزة بصيغة mp4 لتوفير الوقت
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                        res = f.get('height')
                        if res:
                            formats_btns[f"🎬 {res}p"] = f.get('format_id')
            
            # إضافة خيار الصوت دائماً بصيغة m4a المستقرة
            formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
            
            return formats_btns
        except Exception as e:
            print(f"Error extracting formats: {e}")
            return {}

def run_download(url, format_id, file_path):
    """التحميل النهائي مع حل مشكلة Frag والملفات المؤقتة"""
    cookie_path = prepare_engine()
    
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': cookie_path if cookie_path else None,
        'nocheckcertificate': True,
        'quiet': True,
        
        # --- حل مشكلة Errno 2 و Frag (تحميل مستقر في Railway) ---
        'concurrent_fragment_downloads': 5, # تقليل العدد لضمان ثبات الكتابة على القرص
        'continuedl': False, # البدء من جديد لتجنب تضارب ملفات .part القديمة
        'retries': 10,
        'buffersize': 1024 * 512, # حجم بافر مناسب للسيرفرات السحابية
        
        # --- إعدادات الدمج (تتطلب FFmpeg عبر Dockerfile) ---
        'merge_output_format': 'mp4',
        'postprocessor_args': [
            '-c:v', 'copy', # نسخ الفيديو كما هو (أسرع)
            '-c:a', 'aac'    # تحويل الصوت لصيغة متوافقة
        ],
    }
    
    # حذف أي ملف قديم بنفس الاسم قبل البدء لتجنب الأخطاء
    if os.path.exists(file_path):
        os.remove(file_path)
        
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
