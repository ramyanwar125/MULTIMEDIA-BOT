import yt_dlp
import os

# دالة إنشاء ملف الكوكيز بالتنسيق الذي يطلبه يوتيوب (Netscape)
def get_cookies_path():
    cookie_file = "youtube_cookies.txt"
    lines = [
        "# Netscape HTTP Cookie File\n",
        ".youtube.com\tTRUE\t/\tTRUE\t1766757959\tGPS\t1\n",
        ".youtube.com\tTRUE\t/\tTRUE\t1801316163\tPREF\ttz=Africa.Cairo&f7=100\n",
        ".youtube.com\tTRUE\t/\tTRUE\t1800424038\tSOCS\tCAISEwgDEgk4NDYxMjU0NDcaAmVuIAEaBgiA8ZzKBg\n"
    ]
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return cookie_file

def get_all_formats(url):
    cookie_path = get_cookies_path()
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'cookiefile': cookie_path,
        'cachedir': False,
    }
    
    formats_dict = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            for f in formats:
                # استخراج الصوت
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    abr = f.get('abr', 128)
                    res = f"🎵 Audio ({abr}kbps)"
                    formats_dict[res] = f['format_id']
                
                # استخراج الفيديو MP4
                if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                    height = f.get('height')
                    if height:
                        res = f"🎬 Video {height}p"
                        if res not in formats_dict:
                            formats_dict[res] = f['format_id']
                            
        except Exception as e:
            raise e
    
    return dict(sorted(formats_dict.items(), key=lambda x: x[0], reverse=True))

def run_download(url, format_id, output_path):
    cookie_path = get_cookies_path()
    ydl_opts = {
        'format': f'{format_id}+bestaudio/best',
        'outtmpl': output_path,
        'cookiefile': cookie_path,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }
    
    # إذا كان التحميل صوتاً فقط
    if "audio" in format_id.lower():
        ydl_opts['format'] = format_id

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            raise e
