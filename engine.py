import os
import yt_dlp

def prepare_engine():
    """التحقق من وجود ملف الكوكيز"""
    cookie_file = "cookies.txt"
    # إذا لم يكن الملف موجوداً، لن يعطل البوت بل سيحاول التحميل بدونه
    if not os.path.exists(cookie_file):
        return None
    return cookie_file

def get_all_formats(url):
    """استخراج الجودات المتاحة مع دعم ذكي للمواقع الاجتماعية"""
    cookie_file = prepare_engine()
    
    ydl_opts = {
        'quiet': True, 
        'nocheckcertificate': True, 
        'no_warnings': True,
        'cookiefile': cookie_file if cookie_file else None,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {}

        # التحقق إذا كان الرابط لفيسبوك أو إنستجرام لفرض دمج الصوت والصورة
        is_social = any(x in url for x in ["facebook.com", "fb.watch", "instagram.com"])

        if is_social:
            # فيسبوك وإنستجرام: نطلب أفضل فيديو + أفضل صوت لضمان جودة عالية
            formats_btns["🎬 Best Quality | أفضل جودة"] = "bestvideo+bestaudio/best"
        else:
            # يوتيوب والمواقع الأخرى: استخراج الجودات المدمجة بصيغة mp4
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    res = f.get('height')
                    if res:
                        formats_btns[f"🎬 {res}p"] = f.get('format_id')
        
        # إضافة خيار الصوت دائماً
        formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
        
        return formats_btns

def run_download(url, format_id, file_path):
    """تنفيذ التحميل والدمج بأقصى سرعة"""
    cookie_file = prepare_engine()
    
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': cookie_file if cookie_file else None,
        'nocheckcertificate': True,
        'quiet': True,
        # --- إعدادات السرعة ---
        'concurrent_fragment_downloads': 15, 
        'continuedl': True,
        'buffersize': 1024 * 1024,
        'retries': 10,
        # --- إعدادات الدمج (تطلب FFmpeg) ---
        'merge_output_format': 'mp4',
        'postprocessor_args': ['-c:v', 'copy', '-c:a', 'aac'],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
