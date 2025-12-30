import os
import yt_dlp
import re

def prepare_engine():
    cookie_file = "cookies_stable.txt"
    if not os.path.exists(cookie_file):
        with open(cookie_file, "w") as f:
            with open(cookie_file, "w") as f: f.write("# Netscape HTTP Cookie File\n")
    return cookie_file

def get_all_formats(url):
    ydl_opts = {
        'quiet': True, 
        'cookiefile': prepare_engine(), 
        'nocheckcertificate': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {}
        all_formats = info.get('formats', [])
        
        for f in all_formats:
            # الشرط هنا: يجب أن يحتوي الملف على فيديو وصوت معاً
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                res = f.get('height')
                ext = f.get('ext')
                if res:
                    label = f"🎬 {res}p ({ext})"
                    # نأخذ الـ format_id المباشر للجودة الجاهزة
                    formats_btns[label] = f.get('format_id')
        
        def extract_res(label):
            nums = re.findall(r'\d+', label)
            return int(nums[0]) if nums else 0

        sorted_labels = sorted(formats_btns.keys(), key=extract_res, reverse=True)
        return {label: formats_btns[label] for label in sorted_labels}

def run_download(url, format_id, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id, # سيحمل الملف الجاهز مباشرة
        'cookiefile': 'cookies_stable.txt',
        'nocheckcertificate': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
