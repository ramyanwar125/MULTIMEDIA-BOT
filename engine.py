import os
import yt_dlp

def prepare_engine():
    """إعداد ملف الكوكيز لضمان استقرار التحميل وتخطي القيود"""
    cookie_file = "cookies_stable.txt"
    if not os.path.exists(cookie_file):
        with open(cookie_file, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1766757959\tGPS\t1\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1801316163\tPREF\ttz=Africa.Cairo&f7=100\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1800424038\tSOCS\tCAISEwgDEgk4NDYxMjU0NDcaAmVuIAEaBgiA8ZzKBg\n")
    return cookie_file

def get_all_formats(url):
    """استخراج جميع الجودات المتاحة مع دعم خاص للفيسبوك والإنستجرام"""
    ydl_opts = {
        'quiet': True, 
        'cookiefile': prepare_engine(), 
        'nocheckcertificate': True, 
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {}

        # تمييز روابط الفيسبوك وإنستجرام لضمان جلب فيديو كامل (صوت وصورة)
        is_social = any(x in url for x in ["facebook.com", "fb.watch", "instagram.com"])

        if is_social:
            # نطلب أفضل جودة مدمجة مباشرة لهذه المواقع
            formats_btns["🎬 Best Quality | أفضل جودة"] = "bestvideo+bestaudio/best"
        else:
            # المواقع الأخرى (يوتيوب وغيرها) - استخراج الجودات المتوفرة
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    res = f.get('height')
                    if res:
                        formats_btns[f"🎬 {res}p"] = f.get('format_id')
        
        # إضافة خيار الصوت دائماً بصيغة m4a المستقرة
        formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
        
        return formats_btns

def run_download(url, format_id, file_path):
    """تنفيذ التحميل بأقصى سرعة مع تفعيل خاصية الدمج"""
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': 'cookies_stable.txt',
        'nocheckcertificate': True,
        'quiet': True,
        # --- إعدادات السرعة القصوى ---
        'concurrent_fragment_downloads': 15, 
        'continuedl': True,
        'buffersize': 1024 * 1024,
        'retries': 10,
        # --- إعدادات الدمج (تطلب وجود ffmpeg على السيرفر) ---
        'merge_output_format': 'mp4',
        'postprocessor_args': ['-c:v', 'copy', '-c:a', 'aac'], # تسريع عملية الدمج دون إعادة ترميز
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
