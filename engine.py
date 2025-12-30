import os
import yt_dlp
import re

def prepare_engine():
    cookie_file = "cookies_stable.txt"
    if not os.path.exists(cookie_file):
        with open(cookie_file, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
    return cookie_file

def get_all_formats(url):
    ydl_opts = {
        'quiet': True, 
        'cookiefile': prepare_engine(), 
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats_btns = {}
            all_formats = info.get('formats', [])
            
            for f in all_formats:
                # فلتر لجلب الجودات التي تحتوي فيديو وصوت معاً لفيسبوك
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    res = f.get('height')
                    if res:
                        label = f"🎬 {res}p"
                        formats_btns[label] = f.get('format_id')
            
            if not formats_btns: # محاولة إضافية إذا لم يجد جودات مرقمة
                formats_btns["🎬 Best Quality"] = "best"

            def extract_res(label):
                nums = re.findall(r'\d+', label)
                return int(nums[0]) if nums else 0

            sorted_labels = sorted(formats_btns.keys(), key=extract_res, reverse=True)
            final_formats = {label: formats_btns[label] for label in sorted_labels}
            final_formats["🎶 Audio | تحميل صوت"] = "bestaudio"
            return final_formats
    except Exception as e:
        print(f"Error in engine: {e}")
        return {}

def run_download(url, format_id, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': f"{format_id}+bestaudio/best",
        'cookiefile': 'cookies_stable.txt',
        'nocheckcertificate': True,
        'quiet': True,
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
