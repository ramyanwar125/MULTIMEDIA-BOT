import os
import yt_dlp

def prepare_engine():
    cookie_file = "cookies_stable.txt"
    if not os.path.exists(cookie_file):
        with open(cookie_file, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1766757959\tGPS\t1\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1801316163\tPREF\ttz=Africa.Cairo&f7=100\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1800424038\tSOCS\tCAISEwgDEgk4NDYxMjU0NDcaAmVuIAEaBgiA8ZzKBg\n")
    return cookie_file

def get_all_formats(url):
    """تحسين استخراج الجودات لفيسبوك وإنستغرام"""
    ydl_opts = {
        'quiet': True, 
        'cookiefile': prepare_engine(), 
        'nocheckcertificate': True, 
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {}
        
        # إذا كان الرابط من إنستجرام أو فيسبوك، نستخدم صيغة 'best' مباشرة
        if "instagram.com" in url or "facebook.com" in url or "fb.watch" in url:
            formats_btns["🎬 Best Quality | أفضل جودة"] = "bestvideo+bestaudio/best"
        else:
            # يوتيوب والمواقع الأخرى
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    res = f.get('height')
                    if res:
                        label = f"🎬 {res}p"
                        formats_btns[label] = f.get('format_id')

        # خيار الصوت دائماً متاح
        formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
        
        return formats_btns

def run_download(url, format_id, file_path):
    """إعدادات التحميل لضمان دمج الصوت مع الصورة"""
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': 'cookies_stable.txt',
        'nocheckcertificate': True,
        'quiet': True,
        'concurrent_fragment_downloads': 15,
        'continuedl': True,
        'retries': 10,
        # إضافة ffmpeg لدمج الصوت والصورة إذا كانا منفصلين
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
